# Generated by Django 2.2.5 on 2020-07-24 10:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaceplanner', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeepreferences',
            name='is_mac',
            field=models.BooleanField(default=False, verbose_name='Mac'),
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='is_mac_preference',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Mac priority'),
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='large_screen',
            field=models.BooleanField(default=False, verbose_name='Large screen'),
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='large_screen_preference',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Large_screen priority'),
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='noise',
            field=models.BooleanField(default=False, verbose_name='Noise'),
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='noise_preference',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Noise priority'),
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='window',
            field=models.BooleanField(default=False, verbose_name='Window'),
        ),
        migrations.AlterField(
            model_name='employeepreferences',
            name='window_preference',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Window priority'),
        ),
        migrations.AlterField(
            model_name='workstationpreferences',
            name='is_mac',
            field=models.BooleanField(default=False, verbose_name='Mac'),
        ),
        migrations.AlterField(
            model_name='workstationpreferences',
            name='large_screen',
            field=models.BooleanField(default=False, verbose_name='Large_screen'),
        ),
        migrations.AlterField(
            model_name='workstationpreferences',
            name='noise',
            field=models.BooleanField(default=False, verbose_name='Noise'),
        ),
        migrations.AlterField(
            model_name='workstationpreferences',
            name='window',
            field=models.BooleanField(default=False, verbose_name='Window'),
        ),
    ]
