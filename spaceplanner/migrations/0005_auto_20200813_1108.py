# Generated by Django 2.2.5 on 2020-08-13 09:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaceplanner', '0004_auto_20200806_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='workstation',
            name='label',
            field=models.CharField(default='komp1', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='large_screen_preference',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Large screen priority'),
        ),
        migrations.AlterField(
            model_name='workstation',
            name='ws_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]