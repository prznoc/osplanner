from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('spaceplanner/', views.Home.as_view(), name='home'),
    path('spaceplanner/out_of_range', views.OutOfRange.as_view(), name = 'out_of_range'),
    path('spaceplanner/user_panel/', views.user_panel, name='user_panel'),
    path('spaceplanner/user_panel/<date>', views.user_panel, name='user_panel'),
    path('spaceplanner/schedule_week/<int:pk>/', views.schedule_week, name='schedule_week'),
    path('spaceplanner/edit_preferences/', views.EditPreferences.as_view(), name='edit_preferences'),
    path('spaceplanner/workstation_schedule/<date>', views.WorkstationSchedule.as_view(), name='workstation_schedule'),
    path('spaceplanner/workstation_preferences', views.WorkstationPreferencesView.as_view(), name='workstation_preferences'),
    path('spaceplanner/edit_information', views.EditInformation.as_view(), name='edit_information'),
    path('accounts/', include('django.contrib.auth.urls')),
]