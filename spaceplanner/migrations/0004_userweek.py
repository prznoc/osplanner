# Generated by Django 2.2.5 on 2020-07-17 11:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spaceplanner', '0003_employeepreferences_favourite_workspace'),
    ]

    operations = [
        migrations.CreateModel(
            name='Userweek',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='year')),
                ('week', models.IntegerField(verbose_name='week')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('friday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='friday', to='spaceplanner.Workstation')),
                ('monday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='monday', to='spaceplanner.Workstation')),
                ('saturday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='saturday', to='spaceplanner.Workstation')),
                ('sunday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sunday', to='spaceplanner.Workstation')),
                ('thursday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='thursday', to='spaceplanner.Workstation')),
                ('tuesday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tuesday', to='spaceplanner.Workstation')),
                ('wednesday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wednesday', to='spaceplanner.Workstation')),
            ],
        ),
    ]
