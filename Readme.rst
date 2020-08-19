------------
Spaceplanner
------------

App for managing allocation of employees to workstations

-----------
Quick start
-----------

1. Add "spaceplanner" and "django tables 2" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        'spaceplanner.apps.SpaceplannerConfig',
        'rest_framework',
        'django_tables2',
    ]

2. Add settings:

    LOGIN_REDIRECT_URL = '/spaceplanner/user_panel'
    LOGOUT_REDIRECT_URL = '/spaceplanner/'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"
    MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

3. Import and include the spaceplanner URLconf in your project urls.py like this:

    ...
    path('accounts/', include('django.contrib.auth.urls')),     # optional, to access password reset and change forms, if necessary
    path('spaceplanner/', include('spaceplanner.urls', namespace='spaceplanner')),

To access app provided password change and reset forms, move 'spaceplanner.apps.SpaceplannerConfig', to top of app list

4. Available localizations:
    -Polish

5. Run `python manage.py migrate` to create the models.

6. Start the development server and visit http://127.0.0.1:8000/admin/ (you'll need the Admin app enabled).

7. Visit http://127.0.0.1:8000/spaceplanner to open app.
