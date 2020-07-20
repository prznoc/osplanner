from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('user_panel/', views.user_panel, name='user_panel'),
    path('schedule_week/', views.schedule_week, name='schedule_week'),
    path('accounts/', include('django.contrib.auth.urls')),
]