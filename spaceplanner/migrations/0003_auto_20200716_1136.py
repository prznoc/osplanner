# Generated by Django 2.2.5 on 2020-07-16 09:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spaceplanner', '0002_auto_20200716_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workweek',
            name='workstation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaceplanner.Workstation'),
        ),
    ]
