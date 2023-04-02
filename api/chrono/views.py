import math
import calendar
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime

from . import serializers, models

ID_NOT_PROVIDED = "ID not provided"
DATA_PROVIDED_IS_NOT_VALID = "Data isn't valid"
ENTITY_NOT_FOUND = "Entity not found"
ENTITY_ADDED_SUCCESSFULLY = "Entity added successfully"
ENTITY_UPDATED_SUCCESSFULLY = "Entity updated successfully"
ENTITY_DELETED_SUCCESSFULLY = "Entity deleted successfully"


# First page
@api_view(['GET'])
def get_data_for_date(request, user_id, date):
    activities = models.Activity.objects.filter(timestamp=date).filter(user_id=user_id)
    serialized_activities = serializers.ActivitySerializer(activities, many=True).data
    data_to_return = {
        'usage': {},
        'score': 0,
        'total_time': 0
    }

    for activity in serialized_activities:
        app = models.Application.objects.get(id=activity['application'])
        serialized_app = serializers.ApplicationSerializer(app, many=False).data

        if serialized_app['category'] not in data_to_return['usage']:
            data_to_return['usage'][serialized_app['category']] = []
        data_to_return['score'] = activity["duration"] * serialized_app["score"]
        data_to_return['total_time'] += activity["duration"]

        activity_minutes = (activity["duration"] / (1000 * 60)) % 60
        activity_minutes = int(activity_minutes)
        activity_hours = (activity["duration"] / (1000 * 60 * 60)) % 24

        data_to_return['usage'][serialized_app['category']].append({
            "name": serialized_app["name"],
            "logo": serialized_app["logo"],
            "time": str(round(activity_hours)) + 'h:' + str(round(activity_minutes)) + 'm',
            "score": activity["duration"] * serialized_app["score"]
        })

        minutes = (data_to_return['total_time'] / (1000 * 60)) % 60
        minutes = int(minutes)
        hours = (data_to_return['total_time'] / (1000 * 60 * 60)) % 24

        data_to_return['total_time'] = str(round(hours)) + 'h:' + str(round(minutes)) + 'm'

    return Response(data_to_return)


# Leaderboard

@api_view(['GET'])
def get_leaderboard(request, company_id):
    users = models.User.objects.filter(company=company_id)
    serialized_users = serializers.UserSerializer(users, many=True).data
    leaderboard = []

    today = datetime.now()
    month = today.month
    year = today.year
    for user in serialized_users:
        activities = models.Activity.objects.filter(user_id=user["id"]).filter(
            timestamp__contains=str(month) + '-' + str(year))
        serialized_activities = serializers.ActivitySerializer(activities, many=True).data
        user_month_score = 0
        for activity in serialized_activities:
            user_month_score += activity['points']

        leaderboard.append({
            "userId": user['id'],
            "name": user['first_name'] + ' ' + user['last_name'],
            "points": user_month_score
        })
    leaderboard = sorted(leaderboard, key=lambda d: d['points'], reverse=True)
    return Response(leaderboard)


# Post activity
@api_view(['POST'])
def upsert_activity(request, user_id):
    today = datetime.now()
    month = today.month
    year = today.year
    day = today.day

    data = JSONParser().parse(request)

    if data['apps']:
        for app in data['apps']:
            current_app = models.Application.objects.filter(name=app['app_name'])
            serialized_app = serializers.ApplicationSerializer(current_app, many=True).data
            activity_record = models.Activity.objects.filter(user_id=user_id).filter(
                timestamp__contains=str(month) + '-' + str(year)).filter(application=serialized_app[0]['id']).first()

            activity = {
                'user': user_id,
                'points': app['ms'] * serialized_app[0]['score'],
                'timestamp': str(today.day) + '-' + str(today.month) + '-' + str(today.year),
                'application': serialized_app[0]['id'],
                'duration': app['ms']
            }

            if activity_record:

                serialized_activity_new = serializers.ActivitySerializer(instance=activity_record, data=activity)
                if serialized_activity_new.is_valid():
                    serialized_activity_new.save()

            else:
                new_activity = serializers.ActivitySerializer(data=activity)
                if new_activity.is_valid():
                    new_activity.save()

        return Response()
    else:
        return HttpResponseNotFound()


@api_view(['GET'])
def get_badges(request, user_id):
    badges = models.Badge.objects.filter(user=user_id)
    serialized_badges = serializers.BadgeSerializer(badges, many=True).data

    user = models.User.objects.filter(id=user_id).first()
    serialized_user = serializers.UserSerializer(user).data

    data_to_return = {
        'badges': {},
        'name': serialized_user['first_name'] + ' ' + serialized_user['last_name']
    }
    for badge in serialized_badges:
        dates = badge['timestamp'].split('-')
        date = str(calendar.month_name[int(dates[1])]) + ' ' + dates[2]
        data_to_return['badges'][date] = badge['image']
    return Response(data_to_return)


@api_view(['POST'])
def register_user(request):
    data = JSONParser().parse(request)
    user = serializers.UserSerializer(data=data)
    if user.is_valid():
        user.save()
        return Response("Added Successfully!!")
    else:
        return HttpResponseNotFound("Failed to Add.")


@api_view(['POST'])
def login_user(request):
    data = JSONParser().parse(request)
    if not data['email'] or not data['password']:
        return HttpResponseNotFound('Credentials not provided')
    else:
        user = models.User.objects.filter(email=data['email']).first()
        if not user:
            return HttpResponseNotFound("User not found")

        user_serialized = serializers.UserSerializer(user).data

        if user_serialized['password'] != data['password']:
            return HttpResponseNotFound("Wrong password")

        company = models.Company.objects.filter(id=user_serialized['company']).first()
        company_serialized = serializers.CompanySerializer(company).data

        data_to_return = {
            'userId': user_serialized['id'],
            'name': user_serialized['first_name'] + ' ' + user_serialized['last_name'],
            'company': company_serialized['name'],
            'badges': {}
        }

        badges = models.Badge.objects.filter(user=user_serialized['id'])
        serialized_badges = serializers.BadgeSerializer(badges, many=True).data

        for badge in serialized_badges:
            if len(data_to_return['badges'].keys()) == 3:
                break
            dates = badge['timestamp'].split('-')
            date = str(calendar.month_name[int(dates[1])]) + ' ' + dates[2]
            data_to_return['badges'][date] = badge['image']

        return Response(data_to_return)


@api_view(['GET'])
def get_users(request, company_id):
    users = models.User.objects.filter(company=company_id)
    serializer = serializers.UserSerializer(users, many=True)

    return Response(serializer.data)


@api_view(['DELETE'])
def delete_user(request, user_id):
    user = models.User.objects.get(id=user_id)
    if user:
        user.delete()
        return Response("Deleted")
    else:
        return Response("Nothing to delete")


@api_view(['GET'])
def get_progress_monthly(request, user_id):
    today = datetime.now()
    month = today.month
    year = today.year

    monthly = []

    for i in range(1, month + 1):
        activities = models.Activity.objects.filter(
            timestamp__contains=str(i) + '-' + str(year)).filter(user_id=user_id)
        serialized_activities = serializers.ActivitySerializer(activities, many=True).data
        sum = 0
        for activity in serialized_activities:
            sum += activity['points']
        monthly.append({
            'date': str(calendar.month_name[i]),
            'score': sum
        })

    return Response(monthly)


@api_view(['GET'])
def get_progress_daily(request, user_id):
    today = datetime.now()
    month = today.month
    day = today.day
    year = today.year

    daily = []

    for i in range(1, day + 1):
        activities = models.Activity.objects.filter(
            timestamp__contains=str(i) + '-' + str(month) + '-' + str(year)).filter(user_id=user_id)
        serialized_activities = serializers.ActivitySerializer(activities, many=True).data
        sum = 0
        for activity in serialized_activities:
            sum += activity['points']
        daily.append({
            'date': i,
            'score': sum
        })

    return Response(daily)