from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('user_panel/', views.user_panel, name='user_panel'),
<<<<<<< HEAD
    path('schedule_week/', views.schedule_week, name='schedule_week'),
    path('edit_preferences/', views.edit_preferences, name='edit_preferences'),
=======
    path('schedule_week/<int:pk>/', views.schedule_week, name='schedule_week'),
>>>>>>> d275dd5... Schedule doesnt works
    path('accounts/', include('django.contrib.auth.urls')),
]