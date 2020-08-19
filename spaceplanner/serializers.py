from spaceplanner.models import Workstation, WorkstationPreferences, EmployeePreferences, Workweek, Userweek

from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):

    last_login = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField()
    employee_preferences = serializers.HyperlinkedRelatedField(many=False, view_name='employee-preference-detail', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'employee_preferences']

class WorkstationSerializer(serializers.ModelSerializer):

    workstation_preferences = serializers.HyperlinkedRelatedField(many=False, view_name='workstation-preference-detail', read_only=True)
    class Meta:
        model = Workstation
        fields = [ 'ws_id', 'label', 'workstation_preferences']

class WorkstationPreferencesSerializer(serializers.ModelSerializer):
    
    workstation = serializers.StringRelatedField()

    class Meta:
        model = WorkstationPreferences
        fields = '__all__'

    def create(self, validated_data):
        workstation = WorkstationSerializer.create(WorkstationSerializer(), validated_data)
        preference, created = WorkstationPreferences.objects.create(workstation=workstation)
        return preference

class EmployeePreferencesSerializer(serializers.ModelSerializer):
    
    employee = serializers.StringRelatedField()

    class Meta:
        model = EmployeePreferences
        fields = '__all__'


class WorkweekSerializer(serializers.ModelSerializer):

    year = serializers.IntegerField(read_only=True)
    week = serializers.IntegerField(read_only=True)
    workstation = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Workweek
        fields = '__all__'


class UserweekSerializer(serializers.ModelSerializer):

    year = serializers.IntegerField(read_only=True)
    week = serializers.IntegerField(read_only=True)
    monday_date = serializers.DateField(read_only=True)
    employee = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Userweek
        fields = '__all__'