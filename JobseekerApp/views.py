from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from Myapp.models import JobSeeker
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import date
from Myapp.models import Employee, Task, TaskProgress, Chat, Message, TeamLead, Company
from EmployeeApp.utility import assign_priority_color, calculate_task_progress
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError
import os
import re
from django.contrib.auth import update_session_auth_hash
from datetime import datetime
from django.contrib import messages
# Create your views here.

def Dashboard(request):
    role = request.session.get("role")
    login_user = request.session.get("username")
    jobseeker = get_object_or_404(JobSeeker, username=login_user)


    if role != "JobSeeker":
        context = {
            'alert_message': "You need to be logged For this account to access this page",
            'redirect_url': reverse("Myapp:login"),
        }
        return render(request, 'custom_alert.html', context)
    
    context = {
        'username': login_user,
        'profile': jobseeker,
    }
    return render(request, 'Jobseeker_App/jobseeker_dashboard.html', context)

def Find_Job(request):
    return render(request, 'Jobseeker_App/find_job.html')

def Saved_Jobs(request):
    return render(request, 'Jobseeker_App/saved_jobs.html')

def Resume(request):
    return render(request, 'Jobseeker_App/resume.html')

def Ai_Chat_Bot(request):
    return render(request, 'Jobseeker_App/ai_chat_bot.html')

def Messages(request):
    return render(request, 'Jobseeker_App/messages.html')


@login_required(login_url='Myapp:login')
def logout_view(request):
    """ Employee Logout & Deactivation """

    if request.user.is_authenticated:
        # Deactivate Employee model entry
        login_user = request.session.get("username")
        employee_user = Employee.objects.filter(username=login_user).first()
        if employee_user:
            employee_user.is_active = False
            employee_user.save()

        # Delete corresponding User model entry
        user_account = User.objects.filter(username=request.user.username).first()
        if user_account:
            user_account.delete()

        # Clear session and log out
        request.session.flush()
        logout(request)

    return redirect("Myapp:login")