# Generated by Django 2.2.5 on 2020-08-18 12:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spaceplanner', '0007_auto_20200814_1219'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employeepreferences',
            options={'verbose_name': 'Employee Preferences'},
        ),
        migrations.AlterModelOptions(
            name='userweek',
            options={'verbose_name': 'Userweek', 'verbose_name_plural': 'Userweeks'},
        ),
        migrations.AlterModelOptions(
            name='workstation',
            options={'verbose_name': 'Workstation', 'verbose_name_plural': 'Workstations'},
        ),
        migrations.AlterModelOptions(
            name='workstationpreferences',
            options={'verbose_name': 'Workstation Preferences'},
        ),
        migrations.AlterModelOptions(
            name='workweek',
            options={'verbose_name': 'Workweek', 'verbose_name_plural': 'Workweeks'},
        ),
        migrations.AlterField(
            model_name='userweek',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userweeks', to=settings.AUTH_USER_MODEL, verbose_name='employee'),
        ),
    ]