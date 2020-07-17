from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'spaceplanner/home.html', {})

@login_required
def user_panel(request):
    user = request.user
    return render(request, 'spaceplanner/user_panel.html', {})