from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import date
from Myapp.models import Employee, Task, TaskProgress, Chat, Company, WorkLeave
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
import pytz


india_timezone = pytz.timezone('Asia/Kolkata')
current_time = now().astimezone(india_timezone)


# Dashboard views show the top 4 box's dinemicaly from the DB, new task, accepted task, completed task 
@login_required(login_url='Myapp:login')
def dashboard(request):
    role = request.session.get("role")
    if role != "Employee":
        messages.warning(request,"You need to be logged in as an Employee to access this page")
        return redirect('Myapp:login')
    
    completed = True

    login_user = request.session.get("username")
    company_id = request.session.get("company_id")


    today = date.today()
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    company = employee.company
    team_member = Employee.objects.filter(company=company)
    team_members = team_member.count

    task_count = Task.objects.filter(assigned_to=employee, created_at__date=current_time.date()).count() 
    pending_task_count = Task.objects.filter(assigned_to=employee, status="Pending", created_at__date=today).count()

    completed_task_count = TaskProgress.objects.filter(employee=employee,status="Completed", completion_date__date=today).count()


    task_due_today = Task.objects.filter(
        created_at__date=current_time.date(),  # Ensure it matches only the date part
        assigned_to=employee
    ).count()



    # Get all accepted tasks
    accepted_tasks = TaskProgress.objects.filter(employee=employee, status="Accepted", action_date__date=current_time.date())

    # Count accepted tasks for today
    accepted_task_count = accepted_tasks.filter(action_date=current_time.date()).count()

    # Get new tasks (with status Pending)
    new_tasks = Task.objects.filter(assigned_to=employee,status="Pending",created_at__date=current_time.date())
    # Apply priority color styling
    new_tasks = assign_priority_color(new_tasks)

    # Update progress data for accepted tasks
    for task_progress in accepted_tasks:
        task_progress.task = calculate_task_progress(task_progress.task)
        task_progress.task = assign_priority_color([task_progress.task])[0]
    

    # Fetch completed tasks for the logged-in employee
    complete_task = TaskProgress.objects.filter(completion_date__date=current_time.date(), employee=employee, status="Completed", action_date__date=current_time.date()).order_by('-completion_date')

    for task in complete_task:
        Completiondate = task.completion_date
        Creationdate = task.task.created_at
        Totalduration = Completiondate - Creationdate  # timedelta

        # Convert to total seconds
        total_seconds = int(Totalduration.total_seconds())

        # Breakdown into days, hours, minutes, and seconds
        days = total_seconds // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # Optional display-friendly version
        if days == 0 and hours == 0 and minutes == 0:
            task.time_taken_display = f"{seconds} sec"
        else:
            task.time_taken_display = f"{days:02d}days {hours:02d}hour {minutes:02d}min"   



    if request.path == '/Employee/dashboard/completed/':
        completed = False

    completion_rate = round((completed_task_count/task_count)*100) if task_count > 0 else 0
    remaining_pct = 100 - completion_rate if completion_rate is not None else 0


    approved_leave = WorkLeave.objects.filter(user=employee, status='Approved').count()
    pending_leaves = WorkLeave.objects.filter(user=employee, status='Pending').count()
    leave_status = WorkLeave.objects.filter(user=employee, is_responded=True).order_by('-applied_at').count()
    leaves = WorkLeave.objects.filter(user=employee).order_by('-applied_at').count()
    rejected_leaves = WorkLeave.objects.filter(user=employee, status='Rejected').count()
    modification_requested = WorkLeave.objects.filter(user=employee, status='Modification Requested').count()

    total_allowed_leaves = 20

    approved_leaves = WorkLeave.objects.filter(user=employee, status="Approved").count()
    current_leave_balance = total_allowed_leaves - approved_leaves
    leave_bar_width = int((current_leave_balance / total_allowed_leaves) * 100)


    context = {
        "new_tasks": new_tasks,
        "accepted_tasks": accepted_tasks,
        "accepted_task_count": accepted_task_count,
        "completed": completed,
        "complete_task": complete_task,
        "today": current_time.date(),
        "employee_dets": employee,
        "team_members": team_members,
        "task_count": task_count,
        "pending_task_count": pending_task_count,
        "completed_task_count": completed_task_count,
        "task_due_today": task_due_today,
        "completion_rate": completion_rate,
        "remaining_rate": 100 - completion_rate,
        "remaining_pct":remaining_pct,
        'approved_leave': approved_leave,
        'pending_leaves': pending_leaves,
        'rejected_leaves': rejected_leaves,
        'modification_requested': modification_requested,
        'leave_status': leave_status,
        'current_leave_balance': current_leave_balance,
        'leave_bar_width': leave_bar_width,
        'leaves': leaves,
    }

    return render(request, 'Employee_App/employee_dashboard.html', context)


@login_required(login_url='Myapp:login')
def accept_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "EmployeeApp:dashboard"

    task_progress, created = TaskProgress.objects.get_or_create(
        task=task,
        employee=employee,
        defaults={
            "status": "Accepted",
            "action_date": current_time
        }
    )

    if not created:
        messages.warning(request, "You have already accepted this task.")
    else:
        task.status = "Accepted"
        task.save()
        messages.success(request, "Task successfully accepted.")

    return redirect(next_url)


@login_required
def pending_task_complete(request, task_id):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    task = get_object_or_404(Task, id=task_id, assigned_to=employee)

    task_progress, created = TaskProgress.objects.get_or_create(
        task=task,
        employee=employee,
        defaults={
            "status": "Accepted",
            "action_date": current_time.date()
        }
    )

    if not created:
        messages.warning(request, "You already accepted this task.")
    else:
        task.status = "Accepted"
        task.save()
        messages.success(request, "Task accepted. You can now mark it as completed.")

    return redirect("EmployeeApp:complete_task", task_id=task.id)


@login_required
def complete_task(request, task_id):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    try:
        # Try to fetch TaskProgress directly by ID
        task_progress = TaskProgress.objects.get(id=task_id, employee=employee)
        redirect_url = "/Employee/Dashboard/"
    except TaskProgress.DoesNotExist:
        # If not found, maybe the passed ID is Task.id, get progress by employee + task
        task = get_object_or_404(Task, id=task_id, assigned_to=employee)
        task_progress = get_object_or_404(TaskProgress, task=task, employee=employee)
        redirect_url = "/Employee/pending_task/"

    print("Final Redirect URL:", redirect_url)

    now = current_time
    today = current_time.date()
    if request.method == 'POST':
        days_diff = (today - task_progress.task.due_date).days
        if days_diff < 0:
            completion_type = 'early'
            days = abs(days_diff)
        elif days_diff == 0:
            completion_type = 'ontime'
            days = 0
        else:
            completion_type = 'late'
            days = days_diff

        task_progress.status = "Completed"
        task_progress.completion_type = completion_type
        task_progress.completion_date = now
        task_progress.days_difference = days
        task_progress.notes = request.POST.get("completion_notes", "")
        task_progress.save()

        messages.success(request, f"Task '{task_progress.task.title}' marked as completed.")
        return redirect(redirect_url)

    days_diff = (today - task_progress.task.due_date).days
    context = {
        "task": task_progress,
        "is_late": days_diff > 0,
        "days_late": max(0, days_diff),
        "back_url": redirect_url,
    }
    return render(request, "Employee_App/complete_confirmation.html", context)


# Setting function to show basic dets of loginuser on setting page
@login_required(login_url='Myapp:login')
def setting(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee_dets = get_object_or_404(Employee, username=login_user, company_id=company_id)

    context = {
        'employee_dets': employee_dets
    }
    return render(request, 'Employee_App/Settings/settings.html', context)


# function to auto fill the input fields in the profile setting  
@login_required(login_url='Myapp:login')
def profile_settings(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    profile = get_object_or_404(Employee, username=login_user, company_id=company_id)

    context = {'employee_dets': profile}
    return render(request, 'Employee_App/Settings/profileSetting.html', context)


# function to update the profile pic, full name, username(according to username email, auto changes), password if user enters the old one correct
@login_required(login_url='Myapp:login')
def update_profile(request):
    if request.method == 'POST':
        try:
            # ✅ Get Form Data
            Image = request.FILES.get('avatarInput')
            Full_Name = request.POST.get('nameInput')
            New_UserName = request.POST.get('usernameInput')
            role = request.POST.get('roleInput')
            old_Password = request.POST.get('oldPasswordInput')
            new_Password = request.POST.get('passwordInput')

            user = request.user  
            login_user = request.session.get("username")
            company_name = request.session.get("company_name")
            # profile = get_object_or_404(Employee, username=login_user, company__name=company_name)
            company = Company.objects.get(name=company_name)
            profile = Employee.objects.get(
                username=login_user,
                company=company
            )
            if not profile:
                return HttpResponse("<script>alert('❌ Profile not found.'); window.location.href='/Employee/Profile_Settings/';</script>")

            # ✅ Handle Profile Picture Upload
            if Image:
                if profile.image and profile.image.name and profile.image.name != Image.name:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(profile.image))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                profile.image = Image

            # ✅ Handle Username Update
            if New_UserName and New_UserName != profile.username:
                if not re.match(r'^[A-Za-z0-9_]+$', New_UserName):
                    return HttpResponse("<script>alert('❌ Username can only contain letters, numbers, and underscore (_).'); window.location.href='/Employee/Profile_Settings/';</script>")

                if Employee.objects.filter(username=New_UserName, company__name=company).exists() or User.objects.filter(username=New_UserName).exists():
                    return HttpResponse(f"<script>alert('❌ Username \"{New_UserName}\" already exists. Please choose another one.'); window.location.href='/Employee/Profile_Settings/';</script>")

                old_username = user.username  # Store old username before updating

                if profile:
                    profile.username = New_UserName
                    profile.email = f"{New_UserName}@{profile.company.domain}"
                    user.username = New_UserName  # Update the User model as well

                user.save(update_fields=["username"])  
                profile.save(update_fields=["username", "email"])  

                # ✅ Delete old username from User model (only if successfully updated)
                User.objects.filter(username=old_username).delete()

                # ✅ Keep user logged in after username change
                update_session_auth_hash(request, user)
                request.session["username"] = New_UserName  

            # ✅ Handle Full Name and Role Update
            if Full_Name:
                profile.full_name = Full_Name
            
            if role:
                profile.role = role

            # ✅ Handle Password Update
            if new_Password or old_Password:  
                if not old_Password:
                    return HttpResponse("<script>alert('⚠️ Please enter your old password to set a new one.'); window.location.href='/Employee/Profile_Settings/';</script>")

                if not new_Password:
                    return HttpResponse("<script>alert('⚠️ Enter the new password to be set. Please try again.'); window.location.href='/Employee/Profile_Settings/';</script>")

                if old_Password != profile.password:
                    return HttpResponse("<script>alert('❌ Incorrect old password. Please try again.'); window.location.href='/Employee/Profile_Settings/';</script>")

                if old_Password == new_Password:
                    return HttpResponse("<script>alert('⚠️ New password cannot be the same as the old password. Please choose a different one.'); window.location.href='/Employee/Profile_Settings/';</script>")

                profile.password = new_Password  
            
            # ✅ Save All Changes at Once
            profile.save()

            return HttpResponse("<script>alert('✅ Profile updated successfully!'); window.location.href='/Employee/settings/';</script>")

        except IntegrityError:
            return HttpResponse("<script>alert('❌ Database error occurred. Please try again.'); window.location.href='/Employee/Profile_Settings/';</script>")

        except Exception as e:
            return HttpResponse(f"<script>alert('❌ Unexpected error: {str(e)}'); window.location.href='/Employee/Profile_Settings/';</script>")

    return HttpResponse("<script>window.location.href='/Employee/Profile_Settings/';</script>")


# logout function to clear session and user model
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


@login_required
def chat_list(request):
    chats = request.user.chats.all()
    users = User.objects.all()
    chat_data = []
    for chat in chats:
        other_user = chat.members.exclude(id=request.user.id).first()
        chat_data.append({
            'chat': chat,
            'other_user': other_user,
        })
    return render(request, 'chat/myapp/chat.html', {'chat_data': chat_data, 'users': users})


@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Order the members to ensure consistent chat identification regardless of who initiated
    members = sorted([request.user.id, other_user.id])
    chat = Chat.objects.filter(members=members[0]).filter(members=members[1])
    if chat.exists():
        chat = chat.first()
    else:
        chat = Chat.objects.create()
        chat.members.add(request.user, other_user)
        chat.name = f"{request.user.username}'s chat with {other_user.username}" # More descriptive name
        chat.save()
    return redirect('Myapp:view_chat', chat_id=chat.id)


@login_required
def view_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, members=request.user)
    messages = chat.messages.order_by('timestamp')
    other_user = chat.members.exclude(id=request.user.id).first()
    other_username = other_user.username if other_user else "Unknown User" # Handle the case if other_user is None
    return render(request, 'myapp/view_chat.html', {'chat': chat, 'messages': messages, 'other_username': other_username})


@login_required
def teamMember(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)
    company = employee.company
    team_member = Employee.objects.filter(company=company)
    team_members = team_member.count
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "EmployeeApp:dashboard"

    context = {
        'employee_dets': employee,
        'count': team_members,
        'team_members': team_member,
        'page_title': 'Team Members',
        'subtitle': employee.company.name,
        'unit': 'members',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'online', 'label': 'Online'},
            {'value': 'offline', 'label': 'Offline'},
        ],
        'search_id': 'memberSearch',
        'search_placeholder': 'Search members...',
        'back_url': next_url,
    }
    return render(request, 'Employee_App/team_members.html', context)


@login_required
def pendingTask(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    pending_task = Task.objects.filter(assigned_to=employee, status="Pending").order_by("-due_date")

    for task in pending_task:
        if task.due_date:
            task.daysLeft = (task.due_date - current_time.now().date()).days
            print(f"Task: {task.title}, Days Left: {task.daysLeft}")
        else:
            task.daysLeft = None
    pending_task_count = pending_task.count()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "EmployeeApp:dashboard"

    context = {
        'today': current_time.date(),
        'pending_tasks': pending_task,
        'employee_dets': employee,
        'count': pending_task_count,
        'page_title': 'All Pending Tasks',
        'subtitle': employee.company,
        'unit': 'Tasks',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Priority Filter',
                'options': [
                    {'value': 'low', 'label': 'Low'},
                    {'value': 'medium', 'label': 'Medium'},
                    {'value': 'high', 'label': 'High'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned by...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': True,
    }
    return render(request, 'Employee_App/pending_task.html', context)


@login_required
def completedTask(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    pending_task = TaskProgress.objects.filter(employee=employee, status="Completed")
    pending_task_count = pending_task.count()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "EmployeeApp:dashboard"

    context = {
        'employee_dets': employee,
        'pending_tasks': pending_task,
        'count': pending_task_count,
        'page_title': 'All Pending Tasks',
        'subtitle': employee.company.name,
        'unit': 'tasks',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
        ],
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned by...',
        'back_url': next_url,
    }
    return render(request, 'Employee_App/completed_task.html', context)


@login_required
def AllTask(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    all_task = Task.objects.filter(assigned_to=employee)
    for task in all_task:
        conformTask = TaskProgress.objects.filter(task=task, employee=employee).first()
        if conformTask:
            task.task_progress = conformTask.status
        else:
            task.task_progress = task.status

    all_task_count = all_task.count()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "Employee/Dashboard"

    context = {
        'employee_dets': employee,
        'all_tasks': all_task,
        'count': all_task_count,
        'page_title': 'All Tasks',
        'subtitle': employee.company.name,
        'unit': 'tasks',
        'filters':[
            {'value': 'all', 'label': 'All', 'url': '/Employee/all_tasks/'},
            {'value': 'pending', 'label': 'Pending Tasks', 'url': '/Employee/pending_task/'},
            {'value': 'completed', 'label': 'Completed Tasks', 'url': '/Employee/dashboard/completed/'},
        ],
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned by...',
        'back_url': '/Employee/Dashboard/',
    }
    return render(request, 'Employee_App/all_tasks.html', context)


@login_required
def leave_request(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    current_time = datetime.now()
    total_allowed_leaves = 20

    approved_leaves = WorkLeave.objects.filter(user=employee, status="Approved").count()
    current_leave_balance = total_allowed_leaves - approved_leaves

    leave_bar_width = int((current_leave_balance / total_allowed_leaves) * 100)
    if leave_bar_width < 0:
        leave_bar_width = 0

    if leave_bar_width < 25:
        balance_heading = "Critical Balance"
        bar_color = "bg-red-500"
    elif leave_bar_width < 50:
        balance_heading = "Low Balance"
        bar_color = "bg-yellow-500"
    else:
        balance_heading = "Available"
        bar_color = "bg-green-500"

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "/Employee/Dashboard/"

    if request.method == 'POST':
        # Get form data
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reasonTitle = request.POST.get('reasonTitle')
        reasonDiscription = request.POST.get('reasonDiscription')
        contactInfo = request.POST.get('contactInfo')
        documentAttachment = request.POST.get('documentAttachment')
        notify_team = request.POST.get('notify_team') == 'on'
        out_of_office = request.POST.get('out_of_office') == 'on'
        delegate_tasks = request.POST.get('delegate_tasks') == 'on'
        action = request.POST.get('action')
        is_half_day = request.POST.get('is_half_day') == 'true'
        half_day_period = request.POST.get('half_day_period', '')
        duration_date = request.POST.get('duration_date')

        # Validation for submit only
        if not all([leave_type, start_date, end_date, reasonTitle, reasonDiscription]):
            messages.error(request, "Please fill all required fields.")
            return redirect('EmployeeApp:leave_request')

        # Optional: Allow empty fields if saving as draft
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('EmployeeApp:leave_request')

        if start_date_obj and end_date_obj and end_date_obj < start_date_obj:
            messages.error(request, "End date cannot be before start date.")
            return redirect('EmployeeApp:leave_request')

        # Decide status
        leave_status = "Pending" if action == "submit" else "Draft"

        # Save leave
        new_leave = WorkLeave(
            user=employee,
            leave_type=leave_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            applied_at=current_time,
            reason_title=reasonTitle,
            reason_discription=reasonDiscription,
            contact_info=contactInfo,
            notify_team=notify_team,
            out_of_office=out_of_office,
            delegate_tasks=delegate_tasks,
            status=leave_status,
            duration=duration_date
        )

        if documentAttachment:
            new_leave.documentAttachment = documentAttachment  # Adjust field name if needed
        
        if is_half_day:
            new_leave.is_half_day=is_half_day
            new_leave.half_day_period=half_day_period

        new_leave.save()
        # print(f"User:- {employee}")
        # print(f"Leave Type:-{leave_type}, Start:-{start_date_obj} to End:-{end_date_obj}")
        # print(f"Applied at:-{current_time}")
        # print(f"Reason:- {reason}")
        # print(f"Contact Info:- {contactInfo}, Notify Team Members:- {notify_team}, Out of Office:- {out_of_office}, Delegate Tasks:- {delegate_tasks}")
        # print(f"Status Level:- {leave_status}")
        # if documentAttachment:
        #     print(f"Documents :- {documentAttachment}")
        
        # if is_half_day:
        #     print(f"Is Half Day:- {is_half_day}, Half Day Period:- {half_day_period}")

        if action == "submit":
            messages.success(request, "Your leave request has been submitted successfully.")
        else:
            messages.success(request, "Leave request saved as draft.")
        
        return redirect(next_url)

    print(leave_bar_width)
    context = {
        'employee_dets': employee,
        'page_title': 'Request Leave',
        'subtitle': 'Submit your leave request for approval',
        'count': approved_leaves,
        'current_leave_balance': current_leave_balance,
        'leave_bar_width': leave_bar_width,
        'balance_heading': balance_heading,
        'bar_color': bar_color,
        'unit': 'Leaves',
        'back_url': next_url,
        'searchFilterBar': False,
        'today': current_time.date(),
        'leave_types': [
            ("Sick Leave", "Sick Leave", "bg-blue-500"),
            ("Casual Leave", "Casual Leave", "bg-green-500"),
            ("Vacation Leave", "Vacation Leave", "bg-yellow-500"),
            ("Earned Leave", "Earned Leave", "bg-purple-500"),
            ("Unpaid Leave", "Unpaid Leave", "bg-orange-500"),
            ("Emergency Leave", "Emergency Leave", "bg-red-500"),
        ]
    }

    return render(request, 'Employee_App/leave_request.html', context)


@login_required
def leave_history(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    leaves_approved = WorkLeave.objects.filter(user=employee, status="Approved")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "/Employee/Dashboard/"


    context = {
        'employee_dets': employee,
        'count': leaves_approved.count(),
        'page_title': 'Leave History',
        'subtitle': employee.company,
        'leaves_approved': leaves_approved,
        'unit': 'Leaves',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Leave_Type Filter',
                'options': [
                    {'value': 'sick leave', 'label': 'Sick Leave'},
                    {'value': 'casual leave', 'label': 'Casual Leave'},
                    {'value': 'vacation leave', 'label': 'Vacation Leave'},
                    {'value': 'earned leave', 'label': 'Earned Leave'},
                    {'value': 'unpaid leave', 'label': 'Unpaid Leave'},
                    {'value': 'emergency leave', 'label': 'Emergency Leave'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'memberSearch',
        'search_placeholder': 'Search Leave Request by its Leave title, starting or ending date...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': True,
    }

    return render(request, 'Employee_App/leave_history.html', context)


@login_required
def leave_status(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = get_object_or_404(Employee, username=login_user, company_id=company_id)

    leaves_approved = WorkLeave.objects.filter(user=employee).order_by('-applied_at')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "/Employee/Dashboard/"


    context = {
        'employee_dets': employee,
        'count': leaves_approved.count(),
        'page_title': 'Leave History',
        'subtitle': employee.company,
        'leaves_approved': leaves_approved,
        'unit': 'Leaves',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Leave_Type Filter',
                'options': [
                    {'value': 'pending', 'label': 'Pending'},
                    {'value': 'approved', 'label': 'Approved'},
                    {'value': 'modified', 'label': 'Modified'},
                    {'value': 'reconsidered', 'label': 'Reconsidered'},
                    {'value': 'rejected', 'label': 'Rejected'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'memberSearch',
        'search_placeholder': 'Search Leave Request by its Leave title, starting or ending date...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': True,
    }

    return render(request, 'Employee_App/leave_status.html', context)

