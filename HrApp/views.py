from django.shortcuts import render, redirect, get_object_or_404
from Myapp.models import Company, TeamLead, Employee, Task, TaskProgress, WorkLeave
from django.utils.timezone import now
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError
import os
import re
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_protect
from datetime import timedelta
import pytz
from django.db.models import Q

india_timezone = pytz.timezone('Asia/Kolkata')
current_time = now().astimezone(india_timezone)



def progress_calculator(task):  
    if task.due_date and task.created_at:
        total_duration = (task.due_date - task.created_at.date()).days
        days_passed = (current_time.date() - task.created_at.date()).days

        # Calculate progress percentage
        progress = (days_passed / total_duration) * 100 if total_duration > 0 else 0

        # Ensure progress stays within 0% and 100%
        progress = max(0, min(progress, 100))
    else:
        progress = 0
    return progress


@login_required
def Dashboard(request):
    role = request.session.get("role")
    if role != "HR":
        messages.warning(request,"You need to be logged in as an HR to access this page")
        return redirect('Myapp:login')
    
    
    login_user = request.session.get("username")
    profile = TeamLead.objects.filter(username=login_user).first()
    company = Company.objects.get(created_by=profile)

    today = current_time.date()
    # Get all tasks

    task_due_today = Task.objects.filter(
        created_at__date=today,  # Ensure it matches only the date part
        assigned_by=profile
    ).count()

    tasks = Task.objects.filter(assigned_by=profile, created_at__date=today).order_by('-created_at')
    completed_task_progress= 0
    accepted_task_progress= 0

    if tasks.exists():
        completed_task_progress = TaskProgress.objects.filter(
            task__in=tasks,
            completion_date__date=today,
            status="Completed"
        ).all()

        accepted_task_progress = TaskProgress.objects.filter(
            task__in = tasks,
            action_date=today,
            status="Accepted",
        ).all()


        if accepted_task_progress:
            for task_progress in accepted_task_progress:
                task = task_progress.task
                task.calculated_progress = progress_calculator(task)
                task.days_remaining = (task.due_date - task.created_at.date()).days
        

        for task in completed_task_progress:
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


    
    all_Tasks = Task.objects.filter(assigned_by=profile).count()

    # Get the count of tasks due today
    tasks_due_today = Task.objects.filter(assigned_by=profile, created_at__date=today).count()

    # Get the count of completed tasks from TaskProgress
    completed_tasks_count = TaskProgress.objects.filter(status="Completed", completion_date__date=today).count()

    # Calculate completion percentage
    if tasks_due_today > 0:
        completion_percentage = round((completed_tasks_count / tasks_due_today) * 100)
        remaining_percentage = round(100 - completion_percentage)
    else:
        completion_percentage = 0
        remaining_percentage = 0

    tasks_count = TaskProgress.objects.count()



    progress_tasks = TaskProgress.objects.filter(task__assigned_by=profile)
    pending_task = Task.objects.filter(assigned_by=profile, status="Pending", created_at__date=today).count()

    
    if progress_tasks:
        progress_tasks_counts = progress_tasks.count()
        completed_task_counts = progress_tasks.filter(status="Completed", completion_date=today).count()
        accepted_task_counts = progress_tasks.filter(status="Accepted", action_date=today).count()
    else:
        progress_tasks_counts = 0
        completed_task_counts = 0
        accepted_task_counts = 0

    active_employees = Employee.objects.filter(is_active=True).count()
    total_employees = Employee.objects.filter(company=company).count()

    # Calculate Active percentage
    if total_employees > 0:
        total_percentage = round((active_employees / total_employees) * 100)
        total_remaining_percentage = round(100 - total_percentage)
    else:
        total_percentage = 0
        total_remaining_percentage = 0


    modified_tasks = []
    for task in tasks:
        # Assign color based on task priority
        priority_colors = {'High': 'red', 'Medium': 'yellow', 'Low': 'blue'}
        color = priority_colors.get(task.task_priority, 'gray')

        modified_tasks.append({
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date,
            'created_at': task.created_at,
            'assigned_to': task.assigned_to,
            'priority': task.task_priority,
            'color': color,
        })

    # Get logged-in user's profile (if exists)
    Employees_On_Work = Employee.objects.count()
    Companys_On_Going = Company.objects.filter(created_by=profile).count()

    company_for_user = Company.objects.filter(created_by=profile).first()
    print(f"Company for user: {company_for_user}")
    company_link = True if company_for_user else False
    print(f"Company Link: {company_link}")

    employee_on_leave = Employee.objects.filter(company=company_for_user, status="onleave").count()
    if employee_on_leave:
        employee_on_leave = Employee.objects.filter(company=company_for_user, status="onleave").count()
    else:
        employee_on_leave = 0


    return render(request, 'Hr_App/Hr_Dashboard.html', {
        'tasks': modified_tasks,
        'employees': Employees_On_Work,
        'companys': Companys_On_Going,
        'tasks_due_today': tasks_due_today,
        'complete_task': completed_tasks_count,
        'task_update': tasks_count,
        'active_employees': active_employees,
        'total_employees': total_employees,
        'tasks_till_now': all_Tasks,
        'profile':profile,
        "company_link": company_link,
        "pending_task_count":pending_task,
        "progress_tasks_counts":progress_tasks_counts,
        "completed_task_counts":completed_task_counts,
        "accepted_task_counts":accepted_task_counts,
        "completed_task_progress":completed_task_progress,
        "accepted_task_progress":accepted_task_progress,
        "task_due_today":task_due_today,
        "completion_percentage":completion_percentage,
        "remaining_percentage":remaining_percentage,
        "total_percentage":total_percentage,
        "total_remaining_percentage":total_remaining_percentage,
        "employee_on_leave":employee_on_leave,
        "company":company,
    })


@login_required
def create_company(request):
    profile = TeamLead.objects.filter(username=request.user).first()
    
    if request.method == "POST":
        company_name = request.POST.get("new_company_name")
        company_domain = request.POST.get("new_company_domain")
        print(f"Company Name: {company_name}, Domain: {company_domain}")
        
        if company_name and company_domain:
            Company.objects.create(
                name=company_name,
                domain=company_domain,
                created_by=profile
            )
            return redirect('Myapp:Hr_Pannel')
    
    return redirect('Myapp:Hr_Pannel')


@login_required
def Post_Task(request):  
    login_user = request.session.get("username")
    profile = TeamLead.objects.filter(username=login_user).first()
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    local_now = current_time.now()

    if not profile:
        return redirect("/")  

    hr_companies = profile.created_companies.all()
    employees = Employee.objects.filter(company__in=hr_companies)
    for emp in employees:
        print(f"Employee: {emp.username}, Company: {emp.company.name}, role: {emp.role}")
    
    if request.method == "POST":
        task_title = request.POST.get("taskHeading")
        task_description = request.POST.get("taskDescription")
        task_date = request.POST.get("taskDate")
        employee_id = request.POST.get("employeeSelect")
        task_priority = request.POST.get("Taskpriority")

        if employee_id:
            try:
                assigned_employee = Employee.objects.get(id=employee_id)
                Task.objects.create(
                    assigned_by=profile,
                    assigned_to=assigned_employee,
                    title=task_title,
                    description=task_description,
                    due_date=task_date,
                    task_priority=task_priority,
                    created_at=local_now
                )
                messages.success(request, f'Task successfully assigned to {assigned_employee.username}!')
                return redirect('HrApp:Post_Task')
            
            except Employee.DoesNotExist:
                messages.error(request, "Error assigning task. Selected employee does not exist!")
            except Exception as e:
                messages.error(request, f"Error assigning task: {str(e)}")

    task_by_user = Task.objects.filter(assigned_by=profile, created_at__date=local_now).count()

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"


    context = {
        'employee_dets': employee,
        'count': task_by_user,
        'page_title': 'Build Your Team',
        'subtitle': companys,
        'unit': 'Tasks for today',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Priority Filter',
                'options': [
                    {'value': 'high', 'label': 'High'},
                    {'value': 'low', 'label': 'Low'},
                    {'value': 'medium', 'label': 'Medium'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': False,
    }

    return render(request, "Hr_App/PostTask.html", context)


@login_required
def Manage_Team(request):
    login_user = request.session.get("username")
    employee_dets = get_object_or_404(TeamLead, username=login_user)
    employees = Employee.objects.filter(company__created_by=employee_dets).order_by('username')
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context ={
        'employees': employees,
        'profile': employee,
        'company_name': companys,
        'employee_dets': employee,
        'count': employees.count(),
        'page_title': 'Manage Your Team',
        'subtitle': companys,
        'unit': 'Employees',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Priority Filter',
                'options': [
                    {'value': 'high', 'label': 'High'},
                    {'value': 'low', 'label': 'Low'},
                    {'value': 'medium', 'label': 'Medium'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': False,  
    }
    return render(request, 'Hr_App/manageTeam.html', context)


@login_required
def view_employee(request, employee_id):
    login_user = request.session.get("username")
    profile = TeamLead.objects.filter(username=login_user).first()
    company_employee = get_object_or_404(Employee, id=employee_id)
    total_days_in_company = (current_time.date() - company_employee.joining_date).days
    company_id = request.session.get("company_id")

    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"
    print(f"Next URL: {next_url}")

    context={
        "employee": company_employee,
        'total_days_in_company': total_days_in_company,
        "profile": profile,
        'employee_dets': employee,
        'page_title': 'Employee Profile',
        'subtitle': companys,
        'unit': 'Employee',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Priority Filter',
                'options': [
                    {'value': 'high', 'label': 'High'},
                    {'value': 'low', 'label': 'Low'},
                    {'value': 'medium', 'label': 'Medium'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': False,
    }
    return render(request, "view_employee.html", context)


@login_required
@csrf_protect 
def delete_employee(request, employee_id):
    if request.method == "POST":
        employee = get_object_or_404(Employee, id=employee_id)
        company_name = employee.company.name
        employee.delete()
        return redirect("HrApp:Manage_Team")

    return redirect("HrApp:Manage_Team")


@login_required
@csrf_protect  
def delete_company(request, company_id):
    if request.method == "POST":
        company = get_object_or_404(Company, id=company_id)
        company.delete()
        messages.success(request, f"Company '{company.name}' deleted successfully!")
        return redirect("HrApp:Manage_Team")

    messages.error(request, "Invalid request method.")
    return redirect("HrApp:Manage_Team")


@login_required
def Build_Team(request):
    login_user = request.session.get("username")
    employee_dets = get_object_or_404(TeamLead, username=login_user)
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    members_count = Employee.objects.filter(company=companys).count()

    added_users = []
    skipped_users = []

    if request.method == "POST":
        # Handle employee creation
        usernames = request.POST.getlist("username[]") or []
        full_names = request.POST.getlist("full_name[]") or []
        passwords = request.POST.getlist("password[]") or []

        if not usernames or not full_names or not passwords:
            return HttpResponse("<script>alert('Please provide at least one employee entry!'); window.location.href='/Hr/Build_Team/';</script>")

        for username, full_name, password in zip(usernames, full_names, passwords):
            email = f"{username}@{companys.domain}"
            
            # Check if employee already exists in THIS COMPANY only
            if Employee.objects.filter(company=companys, username=username).exists():
                print(f"Employee {username} already exists in {companys.name}.")
                skipped_users.append(username)
                continue

            try:
                Employee.objects.create(
                    company=companys,
                    username=username,
                    full_name=full_name,
                    password=password,
                    email=email
                )
                added_users.append(username)
            except IntegrityError:
                print(f"Error creating employee {username}.")
                skipped_users.append(username)

        alert_message = ""
        if added_users:
            alert_message += f"Employees added successfully: {', '.join(added_users)}\n"
        if skipped_users:
            alert_message += f"Skipped duplicate employees in your company: {', '.join(skipped_users)}\n"

        return HttpResponse(f"<script>alert('{alert_message.strip()}'); window.location.href='/Hr/Build_Team/';</script>")
    
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context = {
        'employee_dets': employee_dets,
        'company': companys,
        "show_company_form": not Company.objects.exists(),
        'employee_dets': employee,
        'count': members_count,
        'page_title': 'Build Your Team',
        'subtitle': companys,
        'unit': 'Members',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Priority Filter',
                'options': [
                    {'value': 'high', 'label': 'High'},
                    {'value': 'low', 'label': 'Low'},
                    {'value': 'medium', 'label': 'Medium'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': False,
    }
    return render(request, 'Hr_App/buildTeam.html', context)


# Setting function to show basic dets of loginuser on setting page
@login_required
def setting(request):
    login_user = request.session.get("username")
    employee_dets = get_object_or_404(TeamLead, username=login_user)

    context = {
        'employee_dets': employee_dets
    }
    return render(request, 'Hr_App/Settings/settings.html', context)


# function to auto fill the input fields in the profile setting  
@login_required
def profile_settings(request):
    login_user = request.session.get("username")
    profile = get_object_or_404(TeamLead, username=login_user)

    context = {'employee_dets': profile}
    return render(request, 'Hr_App/Settings/profileSetting.html', context)


# function to update the profile pic, full name, username(according to username email, auto changes), password if user enters the old one correct
@login_required
def update_profile(request):
    print(request.user)
    if request.method == 'POST':
        try:
            # ✅ Get Form Data
            Image = request.FILES.get('avatarInput')
            Full_Name = request.POST.get('nameInput')
            New_UserName = request.POST.get('usernameInput')
            old_Password = request.POST.get('oldPasswordInput')
            new_Password = request.POST.get('passwordInput')

            user = request.user  
            login_user = request.session.get("username")
            company_name = request.session.get("company_name")
            # profile = get_object_or_404(Employee, username=login_user, company__name=company_name)
            profile = TeamLead.objects.get(
                username=login_user
            )
            if not profile:
                return HttpResponse("<script>alert('❌ Profile not found.'); window.location.href='/Hr/Profile_Settings/';</script>")

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
                    return HttpResponse("<script>alert('❌ Username can only contain letters, numbers, and underscore (_).'); window.location.href='/Hr/Profile_Settings/';</script>")

                if TeamLead.objects.filter(username=New_UserName).exists() or User.objects.filter(username=New_UserName).exists():
                    return HttpResponse(f"<script>alert('❌ Username \"{New_UserName}\" already exists. Please choose another one.'); window.location.href='/Hr/Profile_Settings/';</script>")

                old_username = user.username

                if profile:
                    profile.username = New_UserName
                    user.username = New_UserName

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

            # ✅ Handle Password Update
            if new_Password or old_Password:  
                if not old_Password:
                    return HttpResponse("<script>alert('⚠️ Please enter your old password to set a new one.'); window.location.href='/Hr/Profile_Settings/';</script>")

                if not new_Password:
                    return HttpResponse("<script>alert('⚠️ Enter the new password to be set. Please try again.'); window.location.href='/Hr/Profile_Settings/';</script>")

                if old_Password != profile.password:
                    return HttpResponse("<script>alert('❌ Incorrect old password. Please try again.'); window.location.href='/Hr/Profile_Settings/';</script>")

                if old_Password == new_Password:
                    return HttpResponse("<script>alert('⚠️ New password cannot be the same as the old password. Please choose a different one.'); window.location.href='/Hr/Profile_Settings/';</script>")

                profile.password = new_Password  
            
            # ✅ Save All Changes at Once
            profile.save()

            return HttpResponse("<script>alert('✅ Profile updated successfully!'); window.location.href='/Hr/settings/';</script>")

        except IntegrityError:
            return HttpResponse("<script>alert('❌ Database error occurred. Please try again.'); window.location.href='/Hr/Profile_Settings/';</script>")

        except Exception as e:
            return HttpResponse(f"<script>alert('❌ Unexpected error: {str(e)}'); window.location.href='/Hr/Profile_Settings/';</script>")

    return HttpResponse("<script>window.location.href='/Hr/Profile_Settings/';</script>")


@login_required
def teamMember(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=profile).first()

    team_members = Employee.objects.filter(company=companys)

    team_members_count = Employee.objects.filter(company=companys).count()

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context = {
        'employee_dets': profile,
        'count': team_members_count,
        'team_members': team_members,
        'page_title': 'Team Members',
        'subtitle': companys,
        'unit': 'members',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'online', 'label': 'Online'},
            {'value': 'offline', 'label': 'Offline'},
        ],
        'defaultFilter': 'all',
        'search_id': 'memberSearch',
        'search_placeholder': 'Search Employee by there name or role...',
        'back_url': next_url,
        'profile':profile,
        'searchFilterBar': True,
    }
    return render(request, 'Hr_App/team_members.html', context)


@login_required
def active_teams(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=profile).first()

    team_members = Employee.objects.filter(company=companys)

    team_members_count = Employee.objects.filter(company=companys).count()

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context = {
        'employee_dets': profile,
        'count': team_members_count,
        'team_members': team_members,
        'page_title': 'Team Members',
        'subtitle': companys,
        'unit': 'members',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'online', 'label': 'Online'},
            {'value': 'offline', 'label': 'Offline'},
        ],
        'defaultFilter': 'all',
        'search_id': 'memberSearch',
        'search_placeholder': 'Search Team by its name or ...',
        'back_url': next_url,
        'profile':profile,
        'searchFilterBar': True,
    }
    return render(request, 'Hr_App/team_members.html', context)


@login_required
def pendingTask(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    pending_task = Task.objects.filter(
        assigned_by=employee, 
        status="Pending"
    ).order_by("-due_date")

    for task in pending_task:
        if task.due_date and task.created_at:
            task.daysLeft = (task.due_date - task.created_at.date()).days
        else:
            task.daysLeft = None



    pending_task_count = pending_task.count()

    next_url = request.META.get('HTTP_REFERER') or "/Employee/Dashboard/"

    context = {
        'employee_dets': employee,
        'pending_tasks': pending_task,
        'count': pending_task_count,
        'page_title': 'All Pending Tasks',
        'subtitle': companys,
        'unit': 'tasks',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Priority Filter',
                'options': [
                    {'value': 'high', 'label': 'High'},
                    {'value': 'low', 'label': 'Low'},
                    {'value': 'medium', 'label': 'Medium'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': True,
    }
    return render(request, 'Employee_App/pending_task.html', context)


@login_required
def completedTask(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    pending_task = TaskProgress.objects.filter(
        task__assigned_by=employee,
        status="Completed"
    ).order_by('task__due_date')



    pending_task_count = pending_task.count()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context = {
        'employee_dets': employee,
        'pending_tasks': pending_task,
        'count': pending_task_count,
        'page_title': 'All Completed Tasks',
        'subtitle': companys,
        'unit': 'tasks',
        'filters': [
            {'value': 'month', 'label': 'This Month'},
            {'value': 'all', 'label': 'All Time'},
            {'value': 'year', 'label': 'This Year'},
            {
                'dropdown': True,
                'label': 'Status Filter',
                'options': [
                    {'value': 'early', 'label': 'Early'},
                    {'value': 'late', 'label': 'Late'},
                    {'value': 'ontime', 'label': 'OnTime'},
                    {'value': 'high', 'label': 'High'},
                    {'value': 'medium', 'label': 'Medium'},
                    {'value': 'low', 'label': 'Low'},
                ]
            }
        ],
        'defaultFilter': 'month',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': next_url,
        'profile': employee,
        'searchFilterBar': True,
    }

    return render(request, 'Hr_App/completed_task.html', context)


@login_required
def acceptedTask(request):
    from django.utils.timezone import now
    current_time = now()

    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    if not employee:
        messages.error(request, "Employee not found.")
        return redirect("HrApp:Dashboard")
    
    companys = Company.objects.filter(created_by=employee).first()

    pending_task = Task.objects.filter(assigned_by=employee, status="Accepted", created_at__date=current_time.date())
    progress_queryset = TaskProgress.objects.filter(task__in=pending_task)

    completed_task = progress_queryset.filter(status="Completed")
    completed_task_ids = set(completed_task.values_list("task_id", flat=True))

    for task in pending_task:
        progress = task.progress.first()
        if progress:
            print(f"{task.title} → {progress.status} on {progress.action_date or progress.completion_date}")
        else:
            print(f"{task.title} → No progress data")

        # Add dynamic field for status
        task.updateStatus = 'Accepted & Completed' if task.id in completed_task_ids else 'Accepted'

    context = {
        'employee_dets': employee,
        'pending_tasks': pending_task,
        'count': pending_task.count(),
        'page_title': 'All Accepted Tasks',
        'page_subTitle': f"Display tasks for {current_time.date()} only",
        'subtitle': companys,
        'unit': 'tasks',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'year', 'label': 'This Year'},
        ],
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard",
        'profile': employee,
        'completed_task': completed_task,
        'searchFilterBar': True,
    }

    return render(request, 'Hr_App/pending_task.html', context)


@login_required
def AllTask(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    all_task = list(Task.objects.filter(assigned_by=employee))
    for task in all_task:
        conformTask = TaskProgress.objects.filter(task=task, task__assigned_by=employee).first()

        if conformTask:
            task.task_progress = conformTask.status
            task.completion_date = conformTask.completion_date
            
            if task.task_progress == "Completed":
                task.completion_type = conformTask.completion_type
        else:
            task.task_progress = task.status
            if task.task_progress == "Accepted":
                task.completion_date = conformTask.action_date
            else:
                task.completion_date = "Task is Pending"

    status_order = {"Pending": 1, "Accepted": 2, "Completed": 3}
    all_task.sort(key=lambda task: status_order.get(task.task_progress, 99))

    all_task_count = len(all_task)

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context = {
        'employee_dets': employee,
        'all_tasks': all_task,
        'count': all_task_count,
        'page_title': 'All Tasks',
        'subtitle': companys,
        'unit': 'tasks',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'Pending', 'label': 'Pending'},
            {'value': 'Accepted', 'label': 'Accepted'},
            {'value': 'Completed', 'label': 'Completed'},
            {
                'dropdown': True,
                'label': 'Priority Filter',
                'options': [
                    {'value': 'high', 'label': 'High'},
                    {'value': 'low', 'label': 'Low'},
                    {'value': 'medium', 'label': 'Medium'},
                ]
            }
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to, task created date ...',
        'back_url': next_url,
        'searchFilterBar': True,
    }
    return render(request, 'Hr_App/all_tasks.html', context)


@login_required
def EmployeeOnLeave(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    user_on_leave = WorkLeave.objects.filter(user__company=companys).exclude(status='Reconsidred').select_related('user')
    user_on_leave_count = WorkLeave.objects.filter(user__company=companys).count()

    # Collect user IDs on leave
    on_leave_employees = user_on_leave.values_list('user', flat=True)

    for emp in user_on_leave:
        task = Task.objects.filter(assigned_by=employee, assigned_to=emp.user).all()

        emp.task_count = task.count()
        emp.task_completed = TaskProgress.objects.filter(task__in=task, task__assigned_by=employee, status="Completed").count()
            

    # Aggregate tasks for those users
    employee_task = Task.objects.filter(assigned_by=employee, assigned_to__in=on_leave_employees).count()
    employee_task_completed = TaskProgress.objects.filter(task__assigned_by=employee, task__assigned_to__in=on_leave_employees, task=employee_task, status="Completed").count()

    if 'TeamLead/modify_leave' in request.META.get('HTTP_REFERER'):
        next_url = "HrApp:Dashboard"
    else:
        next_url = next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context = {
        'employee_dets': user_on_leave,
        'employee_task': employee_task,
        'employee_task_completed': employee_task_completed,
        'count': user_on_leave_count,
        'page_title': 'All Leave Requests by Employees',
        'subtitle': companys,
        'unit': 'Employees',
        'filters': [
            {'value': 'month', 'label': 'This Month'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'year', 'label': 'This Year'},
            {'value': 'all', 'label': 'All'},
            {
                'dropdown': True,
                'label': 'Status Filter',
                'options': [
                    {'value': 'pending', 'label': 'Pending'},
                    {'value': 'approved', 'label': 'Approved'},
                    {'value': 'rejected', 'label': 'Rejected'},
                    {'value': 'modified', 'label': 'Modified'},
                    {'value': 'reconsidered', 'label': 'Reconsidered'},
                ]
            }
        ],
        'defaultFilter': 'month',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, start date or end date...',
        'back_url': next_url,
        'profile':employee,
        'searchFilterBar': True,
    }

    return render(request, 'Hr_App/employee_on_leave.html', context)


@login_required
def accept_leave(request, user_id):
    login_user = request.session.get("username")
    profile = TeamLead.objects.filter(username=login_user).first()

    employees = Employee.objects.filter(id=user_id).first()
    leave = get_object_or_404(WorkLeave, user=employees, status="Pending")

    if request.method == "POST":
        leave.approved_by = profile
        leave.leave_balance = (leave.leave_balance or 0) + 1
        leave.status = 'Approved'
        leave.approved_at = current_time.now()
        leave.is_responded = True
        leave.save()
        
        # Optionally notify the employee here
        messages.success(request,f"Leave for {leave.user.full_name} has been approved from {leave.start_date.strftime('%b, %d %Y')} to {leave.end_date.strftime('%b, %d %Y')}!")

        return redirect('HrApp:employees_on_leave')

    return render(request, 'Hr_App/accept_leave.html', {'leave': leave})


@login_required
def reject_leave(request, user_id):
    employees = Employee.objects.filter(id=user_id).first()
    leave = get_object_or_404(WorkLeave, Q(user=employees) & (Q(status="Approved") | Q(status="Pending")))

    if request.method == "POST":
        rejection_note = request.POST.get('opposition_note')
        leave.status = 'Rejected'
        leave.rejection_reason = rejection_note
        leave.is_responded = True
        leave.is_rejected = True
        leave.save()

            
        # Optionally notify the employee here
        messages.error(request, f"Leave for {leave.user.full_name} has been rejected.Reason: \"{rejection_note}\"")      
        return redirect('HrApp:employees_on_leave')
    
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context = {
        'leave': leave,
        'employee': employees,
        'back_url': next_url,
        'title': 'Reject Leave Request for',
        'note_title': 'Rejection Notes',
        'button': 'Confirm Rejection',
        'button_class': 'danger',
    }
    return render(request, 'Hr_App/reject_leave_conformation.html', context)


@login_required
def modify_leave(request, user_id):
    login_user = request.session.get("username")
    profile = TeamLead.objects.filter(username=login_user).first()

    employees = Employee.objects.filter(id=user_id).first()
    leave = get_object_or_404(WorkLeave, user=employees)

    if request.method == "POST":
        new_start_date = request.POST.get('new_start_date')
        new_end_date = request.POST.get('new_end_date')
        modification_note = request.POST.get('modification_note')
        print(f"New Start Date: {new_start_date}, New End Date: {new_end_date}")

        if new_start_date and new_end_date:
            leave.modified_start_date = new_start_date
            leave.modified_end_date = new_end_date
            leave.modification_note = modification_note
            leave.status = 'Modified'
            leave.is_modified = True
            leave.modified_at = current_time.now()
            leave.save()

            # Optionally notify the employee here
            messages.success(request, f"Leave dates for {leave.user.full_name} have been modified!")
        else:
            messages.error(request, "Both start and end dates are required.")
        
        return redirect('HrApp:employees_on_leave')
    
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or "HrApp:Dashboard"

    context ={
        'leave': leave,
        'employee': employees,
        'back_url': next_url,
        'title': 'Modify Leave Request for',
        'note_title': 'Modify the Leave Dates',
        'button': 'Confirm Modification',
        'button_class': 'success',
        'profile': profile,
    }

    return render(request, 'Hr_App/reject_leave_conformation.html', context)


@login_required
def reconsider_leave(request, user_id):
    employees = Employee.objects.filter(id=user_id).first()
    leave = get_object_or_404(WorkLeave, user=employees, status="Rejected")
    if request.method == "POST":
        reconsideration_note = request.POST.get('opposition_note')
        leave.reconsider_note = reconsideration_note
        leave.status = "Reconsidred"
        leave.is_responded = False
        leave.is_rejected = False
        leave.is_reconsidered = True
        leave.reconsidered_at = current_time.now()
        leave.save()

        # Optionally notify the employee here
        messages.success(request, f"Leave for {leave.user.full_name} has been reconsidered!")

        return redirect('HrApp:employees_on_leave')
    context = {
        'title': 'Reconsider Leave Request for',
        'note_title': 'Reconsider Notes',
        'button': 'Confirm Reconsideration',
        'button_class': 'success',
        'leave': leave
    }

    return render(request, 'Hr_App/reject_leave_conformation.html', context)


@login_required
def logout_view(request):
    """ Hr Logout & Deactivation """

    if request.user.is_authenticated:
        employee_user = TeamLead.objects.filter(username__iexact=request.user.username).first()
        if employee_user:
            employee_user.is_active = False  # Mark inactive on logout
            employee_user.save()

         # Delete corresponding User model entry
        user_account = User.objects.filter(username=request.user.username).first()
        if user_account:
            user_account.delete()

        # Clear session and log out
        request.session.flush()
        logout(request)

    return redirect("Myapp:login")

