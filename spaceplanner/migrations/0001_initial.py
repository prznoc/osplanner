# Generated by Django 2.2.5 on 2020-07-20 12:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Workstation',
            fields=[
                ('ws_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='WorkstationPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('window', models.BooleanField(default=False, verbose_name='window')),
                ('noise', models.BooleanField(default=False, verbose_name='noise')),
                ('large_screen', models.BooleanField(default=False, verbose_name='large_screen')),
                ('is_mac', models.BooleanField(default=False, verbose_name='is_mac')),
                ('workstation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaceplanner.Workstation')),
            ],
        ),
        migrations.CreateModel(
            name='Userweek',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='year')),
                ('week', models.IntegerField(verbose_name='week')),
                ('monday_date', models.DateField(verbose_name='monday_date')),
                ('Friday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Friday', to='spaceplanner.Workstation')),
                ('Monday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Monday', to='spaceplanner.Workstation')),
                ('Saturday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Saturday', to='spaceplanner.Workstation')),
                ('Sunday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Sunday', to='spaceplanner.Workstation')),
                ('Thursday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Thursday', to='spaceplanner.Workstation')),
                ('Tuesday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Tuesday', to='spaceplanner.Workstation')),
                ('Wednesday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Wednesday', to='spaceplanner.Workstation')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeePreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('window', models.BooleanField(default=False, verbose_name='window')),
                ('window_preference', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='window_preference')),
                ('noise', models.BooleanField(default=False, verbose_name='noise')),
                ('noise_preference', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='noise_preference')),
                ('large_screen', models.BooleanField(default=False, verbose_name='large_screen')),
                ('large_screen_preference', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='large_screen_preference')),
                ('is_mac', models.BooleanField(default=False, verbose_name='is_mac')),
                ('is_mac_preference', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='is_mac_preference')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('favourite_workspace', models.ManyToManyField(to='spaceplanner.Workstation')),
            ],
        ),
        migrations.CreateModel(
            name='Workweek',
            fields=[
                ('week_id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.IntegerField(verbose_name='year')),
                ('week', models.IntegerField(verbose_name='week')),
                ('Friday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Friday', to=settings.AUTH_USER_MODEL)),
                ('Monday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Monday', to=settings.AUTH_USER_MODEL)),
                ('Saturday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Saturday', to=settings.AUTH_USER_MODEL)),
                ('Sunday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Sunday', to=settings.AUTH_USER_MODEL)),
                ('Thursday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Thursday', to=settings.AUTH_USER_MODEL)),
                ('Tuesday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Tuesday', to=settings.AUTH_USER_MODEL)),
                ('Wednesday', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Wednesday', to=settings.AUTH_USER_MODEL)),
                ('workstation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaceplanner.Workstation')),
            ],
            options={
                'unique_together': {('workstation', 'year', 'week')},
            },
        ),
    ]
