from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('user_panel/', views.user_panel, name='user_panel'),
    path('schedule_week/<int:pk>/', views.schedule_week, name='schedule_week'),
    path('edit_preferences/', views.edit_preferences, name='edit_preferences'),
    path('workstation_schedule/<date>', views.workstation_schedule, name='workstation_schedule'),
    path('accounts/', include('django.contrib.auth.urls')),
]