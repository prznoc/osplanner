from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('spaceplanner/', views.home, name='home'),
    path('spaceplanner/out_of_range', views.out_of_range, name = 'out_of_range'),
    path('spaceplanner/user_panel/', views.user_panel, name='user_panel'),
    path('spaceplanner/user_panel/<date>', views.user_panel, name='user_panel'),
    path('spaceplanner/schedule_week/<int:pk>/', views.schedule_week, name='schedule_week'),
    path('spaceplanner/edit_preferences/', views.edit_preferences, name='edit_preferences'),
    path('spaceplanner/workstation_schedule/<date>', views.workstation_schedule, name='workstation_schedule'),
    path('spaceplanner/workstation_preferences', views.workstation_preferences, name='workstation_preferences'),
    path('spaceplanner/edit_information', views.edit_information, name='edit_information'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('workstations/', views.workstation_list),
    path('workstations/<int:pk>/', views.workstation_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)