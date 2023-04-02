"""chrono URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('get-data-for-date/<int:user_id>/<str:date>/', views.get_data_for_date),
    path('get-leaderboard/<int:company_id>/', views.get_leaderboard),
    path('upsert-activity/<int:user_id>/', views.upsert_activity),
    path('get-badges/<int:user_id>/', views.get_badges),
    path('register-user/', views.register_user),
    path('login-user/', views.login_user),
    path('get-users/<int:company_id>', views.get_users),
    path('delete-user/<int:user_id>', views.delete_user),
    path('get-progress/daily/<int:user_id>', views.get_progress_daily),
    path('get-progress/monthly/<int:user_id>', views.get_progress_monthly),

]
