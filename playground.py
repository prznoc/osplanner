import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osplanner.settings")

import django
django.setup()

from spaceplanner.models import Workstation, WorkstationPreferences, EmployeePreferences
from spaceplanner.serializers import WorkstationSerializer, UserSerializer, WorkstationPreferencesSerializer, EmployeePreferencesSerializer

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
import io

import sys


'''
workstation = Workstation.objects.get(ws_id=3)
serializer = WorkstationSerializer(workstation)
#print(serializer.data)


user = User.objects.get(username='andrzej_duda')
serializer = UserSerializer(user)
print(serializer.data)

preference = WorkstationPreferences.objects.get(workstation=workstation)
serializer = WorkstationPreferencesSerializer(preference)
print(serializer.data)


preference = EmployeePreferences.objects.get(employee=user)
serializer = EmployeePreferencesSerializer(preference)
print(serializer.data)
'''
'''
content = JSONRenderer().render(serializer.data)
#print(content)
content = b'{"ws_id":4,"label":"komp4"}'
#print(content)

stream = io.BytesIO(content)
data = JSONParser().parse(stream)
serializer = WorkstationSerializer(data=data)
serializer.is_valid()
#print(serializer.validated_data)
serializer.save()
'''
