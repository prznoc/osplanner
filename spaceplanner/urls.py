from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls, name='admin'),
    path('out_of_range', views.out_of_range, name = 'out_of_range'),
    path('user_panel/', views.user_panel, name='user_panel'),
    path('user_panel/<date>', views.user_panel, name='user_panel'),
    path('schedule_week/<int:pk>/', views.schedule_week, name='schedule_week'),
    path('edit_preferences/', views.edit_preferences, name='edit_preferences'),
    path('workstation_schedule/<date>', views.workstation_schedule, name='workstation_schedule'),
    path('workstation_preferences', views.workstation_preferences, name='workstation_preferences'),
    path('edit_information', views.edit_information, name='edit_information'),
    path('accounts/', include('django.contrib.auth.urls')),
]