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
]

#RestApi patterns
urlpatterns += [
    path('spaceplanner/workstations/', views.WorkstationList.as_view()),
    path('spaceplanner/workstations/<int:pk>/', views.WorkstationDetail.as_view()),
    path('spaceplanner/workstation_preferences/', views.WorkstationPreferencesList.as_view()),
    path('spaceplanner/workstation_preferences/<int:pk>/', views.WorkstationPreferencesDetail.as_view(), name='workstation-preference-detail'),
    path('spaceplanner/employee_preferences/', views.EmployeePreferencesList.as_view()),
    path('spaceplanner/employee_preferences/<int:pk>/', views.EmployeePreferencesDetail.as_view(), name='employee-preference-detail'),
    path('spaceplanner/workweeks/', views.WorkweekList.as_view()),
    path('spaceplanner/workweeks/<int:pk>/', views.WorkweekDetail.as_view()),
    path('spaceplanner/userweeks/', views.UserweekList.as_view()),
    path('spaceplanner/userweeks/<int:pk>/', views.UserweekDetail.as_view()),
    path('spaceplanner/users/', views.UserList.as_view()),
    path('spaceplanner/users/<int:pk>/', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)