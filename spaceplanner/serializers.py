from rest_framework import serializers
from spaceplanner.models import Workstation, WorkstationPreferences, EmployeePreferences, Workweek, Userweek
import calendar

# from django.utils.translation import ugettext_lazy  as _
from django.contrib.auth.models import User

class WorkstationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workstation
        fields = [ 'ws_id', 'label']

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

    class Meta:
        model = Workweek
        fields = '__all__'


class UserweekSerializer(serializers.ModelSerializer):

    class Meta:
        model = Userweek
        fields = '__all__'
