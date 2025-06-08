from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.db import IntegrityError
import os
from datetime import date
from Myapp.models import Employee, Task, TaskProgress
import re
from django.utils import timezone
from django.urls import reverse

@login_required(login_url='Myapp:login')
def dashboard(request):
    # Ensure Employee Profile Exists for the User
    employee_dets = Employee.objects.filter(username__iexact=request.user.username).first()

    # Fetching New Tasks (Tasks that are NOT accepted)
    accepted_task_ids = TaskStatus.objects.filter(status="Accepted").values_list("task", flat=True)
    new_tasks = Task.objects.exclude(id__in=accepted_task_ids)

    # Fetching Accepted Tasks for the logged-in Employee
    accepted_tasks = TaskStatus.objects.filter(
        employee__username=request.user.username, 
        status="Accepted"
    ).values_list("task", flat=True)
    
    # Get completed task IDs for this employee
    completed_task_ids = TaskCompletion.objects.filter(
        completed_by__username=request.user.username
    ).values_list('task_id', flat=True)
    
    # Get active tasks (accepted but not completed)
    active_tasks = Task.objects.filter(
        id__in=accepted_tasks
    ).exclude(
        id__in=completed_task_ids
    )
    
    todayDate = date.today()
    

    accept_task_count = TaskStatus.objects.filter(action_date = todayDate).count()



    for task in active_tasks:
        # Assign Priority Colors
        if task.task_priority == 'High':
            task.color = "red"
        elif task.task_priority == 'Medium':
            task.color = 'yellow'
        else:
            task.color = 'blue'

    for task in new_tasks:
        # Assign Priority Colors
        if task.task_priority == 'High':
            task.color = "red"
        elif task.task_priority == 'Medium':
            task.color = 'yellow'
        else:
            task.color = 'blue'
        
        # Calculate progress percentage if due_date exists
        if task.due_date:
            dueDate = task.due_date
            total_days = (dueDate - task.created_at.date()).days
            elapsed_days = (todayDate - task.created_at.date()).days
            
            # Handle same-day due dates differently
            if dueDate == todayDate:
                task.progress_date = 99  # Shows almost full progress but not 100%
                task.days_remaining = 0
                task.is_due_today = True
            else:
                if total_days > 0:
                    progress = min(100, max(0, (elapsed_days / total_days) * 100))
                else:
                    progress = 100 if elapsed_days >= 0 else 0
                
                task.progress_date = progress
                task.days_remaining = (dueDate - todayDate).days
                task.is_due_today = False
        else:
            task.progress_date = 0
            task.days_remaining = None
            task.is_due_today = False

    today = date.today()
    completed_Task = TaskCompletion.objects.filter(completion_date=today)
    print(completed_Task)
    print(date.today())
    
    return render(request, 'Employee_App/employee_dashboard.html', {
        'new_task': new_tasks,
        'accepted_Task': active_tasks,
        'employee_dets': employee_dets,
        'today': todayDate.strftime("%b %d, %Y"),
        "Accepted_Task_Count": accept_task_count,
        "completed":False,
        "completed_Task": completed_Task,
    })


@login_required(login_url='Myapp:login')
def accept_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    employee = get_object_or_404(Employee, username=request.user.username)
    
    # Check if the employee already accepted the task
    if TaskProgress.objects.filter(task=task, employee=employee).exists():
        return redirect('EmployeeApp:dashboard')

    # Create a TaskProgress entry
    TaskProgress.objects.create(
        task=task,
        employee=employee,
        status="Accepted",
        action_date=date.today()
    )

    return redirect('EmployeeApp:dashboard')



@login_required(login_url='Myapp:login')
def update_profile(request):
    if request.method == 'POST':
        Image = request.FILES.get('avatarInput')
        Full_Name = request.POST.get('nameInput')
        New_UserName = request.POST.get('usernameInput')
        role = request.POST.get('roleInput')
        old_Password = request.POST.get('oldPasswordInput')
        new_Password = request.POST.get('passwordInput')

        user = request.user  
        profile = Employee.objects.filter(username__iexact=user.username).first()

        if profile:
            # ✅ Handle Profile Picture Upload
            if Image:
                if profile.image and profile.image.name and profile.image.name != Image.name:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(profile.image))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                profile.image = Image

            # ✅ Handle Username Update
            if New_UserName and New_UserName != profile.username:
                # 🔹 Validate Username Format (Only A-Z, a-z, 0-9, and _ allowed)
                if not re.match(r'^[A-Za-z0-9_]+$', New_UserName):
                    return HttpResponse(
                        f"<script>alert('❌ Username can only contain letters (A-Z, a-z), numbers (0-9), and underscore (_).');;</script>", redirect('Employee:dashboard')
                    )

                # 🔹 Check if username is already taken
                if Employee.objects.filter(username=New_UserName).exists() or User.objects.filter(username=New_UserName).exists():
                    return HttpResponse(
                        f"<script>alert('❌ Username \"{New_UserName}\" already exists. Please choose another one.');</script>",
                        redirect('EmployeeApp:settings')
                    )

                profile.username = New_UserName
                profile.email = f"{New_UserName}@{profile.company.domain}"
                user.username = New_UserName

                try:
                    user.save(update_fields=["username"])  # ✅ Save safely
                except IntegrityError:
                    return HttpResponse(
                        f"<script>alert('❌ Failed to update username. Please try again.');</script>",
                        redirect('EmployeeApp:settings')
                    )

                request.session["username"] = New_UserName

            # ✅ Handle Full Name and Role Update
            profile.full_name = Full_Name if Full_Name else profile.full_name
            profile.role = role if role else profile.role

            # ✅ Handle Password Update
            if new_Password:
                if old_Password:
                    if check_password(old_Password, user.password):  
                        user.password = new_Password
                        user.save(update_fields=["password"])
                    else:
                        return HttpResponse(
                            f"<script>alert('❌ Incorrect old password. Please try again.');</script>",
                            redirect('EmployeeApp:settings')
                        )
                else:
                    return HttpResponse(
                        f"<script>alert('⚠️ Please enter your old password to set a new one.');</script>",
                        redirect('EmployeeApp:settings')
                    )

            profile.save()
            return HttpResponse(
                f"<script>alert('✅ Profile updated successfully!');</script>",
                redirect('EmployeeApp:settings')
            )

        else:
            return HttpResponse(
                f"<script>alert('❌ Profile not found.');</script>",
                redirect('EmployeeApp:settings')
            )

    return redirect('EmployeeApp:settings')


def setting(request):
    # Ensure Employee Profile Exists for the User
    employee_dets = Employee.objects.filter(username__iexact=request.user.username).first()

    context = {
        'employee_dets': employee_dets
    }
    return render(request, 'Employee_App/Settings/settings.html', context)


def profile_settings(request):
    if request.method == 'POST':
        Image = request.FILES.get('avatarInput')
        Full_Name = request.POST.get('nameInput')
        New_UserName = request.POST.get('usernameInput')
        role = request.POST.get('roleInput')
        old_Password = request.POST.get('oldPasswordInput')
        new_Password = request.POST.get('passwordInput')

        user = request.user  
        profile = Employee.objects.filter(username__iexact=user.username).first()

        if profile:
            # ✅ Handle Profile Picture Upload
            if Image:
                if profile.image and profile.image.name and profile.image.name != Image.name:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(profile.image))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                profile.image = Image

            # ✅ Handle Username Update
            if New_UserName and New_UserName != profile.username:
                # 🔹 Validate Username Format (Only A-Z, a-z, 0-9, and _ allowed)
                if not re.match(r'^[A-Za-z0-9_]+$', New_UserName):
                    return HttpResponse(
                        f"<script>alert('❌ Username can only contain letters (A-Z, a-z), numbers (0-9), and underscore (_).');window.location.href='/Employee/Profile_Settings';</script>"
                    )

                # 🔹 Check if username is already taken
                if Employee.objects.filter(username=New_UserName).exists() or User.objects.filter(username=New_UserName).exists():
                    return HttpResponse(
                        f"<script>window.location.href='/Employee/settings';</script>"
                    )

                profile.username = New_UserName
                profile.email = f"{New_UserName}@{profile.company.domain}"
                user.username = New_UserName

                try:
                    user.save(update_fields=["username"])  # ✅ Save safely
                except IntegrityError:
                    return HttpResponse(
                        f"<script>window.location.href='/Employee/settings';</script>"
                    )

                request.session["username"] = New_UserName

            # ✅ Handle Full Name and Role Update
            profile.full_name = Full_Name if Full_Name else profile.full_name
            profile.role = role if role else profile.role

            # ✅ Handle Password Update
            if new_Password:
                if old_Password:
                    if check_password(old_Password, user.password):  
                        user.password = new_Password
                        user.save(update_fields=["password"])
                    else:
                        return HttpResponse(
                            f"<script>window.location.href='/Employee/settings';</script>"
                        )
                else:
                    return HttpResponse(
                        f"<script>window.location.href='/Employee/settings';</script>"
                    )

            profile.save()
            return HttpResponse(
                f"<script>window.location.href='/Employee/settings';</script>"
            )

        else:
            return HttpResponse(
                f"<script>window.location.href='/Employee/settings';</script>"
            )

        # Ensure Employee Profile Exists for the User
    employee_dets = Employee.objects.filter(username__iexact=request.user.username).first()

    context = {
        'employee_dets': employee_dets
    }

    return render(request, 'Employee_App/Settings/profileSetting.html', context)


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    today = date.today()
    
    # Get the Employee instance from the username
    try:
        employee = Employee.objects.get(username=request.user.username)
    except Employee.DoesNotExist:
        return redirect('EmployeeApp:dashboard')
    
    if request.method == 'POST':
        # Calculate completion status
        days_diff = (today - task.due_date).days
        
        if days_diff < 0:
            status = 'early'
            days = abs(days_diff)
        elif days_diff == 0:
            status = 'ontime'
            days = 0
        else:
            status = 'late'
            days = days_diff
        
        # Create completion record
        TaskCompletion.objects.create(
            task=task,
            completed_by=employee,  # Use the employee we fetched
            status=status,
            days_difference=days,
            notes=request.POST.get('completion_notes', ''),
            completion_date=today
        )
        
        # Update task status
        TaskStatus.objects.update_or_create(
            task=task,
            employee=employee,  # Use the employee we fetched
            defaults={
                'completion_status': 'Complete',
                'status': 'Accepted',
                'completed_at': timezone.now()
            }
        )
        
        return redirect('EmployeeApp:dashboard')
    
    # For GET requests, show confirmation page
    days_diff = (today - task.due_date).days
    context = {
        'task': task,
        'is_late': days_diff > 0,
        'days_late': max(0, days_diff)
    }
    return render(request, 'Employee_App/complete_confirmation.html', context)



@login_required(login_url='Myapp:login')
def logout_view(request):
    """ Employee Logout & Deactivation """

    if request.user.is_authenticated:
        employee_user = Employee.objects.filter(username__iexact=request.user.username).first()
        if employee_user:
            employee_user.is_active = False  # Mark inactive on logout
            employee_user.save()

        # Clear session and log out
        request.session.flush()
        logout(request)

    return redirect("Myapp:login")
