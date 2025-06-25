from django.shortcuts import render, redirect, get_object_or_404
from Myapp.models import Company, TeamLead, Employee, Task, TaskProgress, WorkLeave, Team, HR, Co_Curricular
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
import json

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
            task__in=tasks,
            action_date__date=today,
            status="Accepted",
        ).all()

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
    Companys_On_Going = Team.objects.filter(created_by=profile, is_active=True).count()

    company_for_user = Company.objects.filter(created_by=profile).first()
    company_link = True if company_for_user else False

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

    employee_dets = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee_dets).first()
    local_now = current_time.now()

    if not profile:
        return redirect("/")

    # Initialize empty dictionary for team-employee mapping
    all_teams_data = {}
    teams_queryset = Team.objects.filter(created_by=profile, is_active=True)

    # Build team-employee mapping with trimmed team names
    for team in teams_queryset:
        team_members = []
        for member in team.members.all():
            team_members.append({
                'id': member.id,
                'username': member.full_name,
                'role': member.role
            })
        # Use strip() to ensure no leading/trailing spaces
        all_teams_data[team.name.strip()] = team_members

    print(all_teams_data)

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
                messages.success(request, f'Task successfully assigned to {assigned_employee.full_name}!')
                return redirect('HrApp:Post_Task')
            except Employee.DoesNotExist:
                messages.error(request, "Error assigning task. Selected employee does not exist!")
            except Exception as e:
                messages.error(request, f"Error assigning task: {str(e)}")

    task_by_user = Task.objects.filter(assigned_by=profile, created_at__date=local_now).count()
    next_url = "/TeamLead/Dashbord/"

    context = {
        'employee_dets': employee_dets,
        'count': task_by_user,
        'page_title': 'Assign New Task',
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
        'profile': profile,
        'searchFilterBar': False,
        'current_time': current_time.date(),
        'teams': teams_queryset,
        'all_teams_employees_json': json.dumps(all_teams_data),
    }

    return render(request, "Hr_App/PostTask.html", context)


@login_required
def Manage_Team(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    employee_dets = get_object_or_404(TeamLead, username=login_user)
    admin_count = TeamLead.objects.filter(created_companies__created_by=employee_dets).count()
    manager_count = TeamLead.objects.filter(created_companies__created_by=employee_dets, role="Manager").count()

    teams = Team.objects.filter(created_by=employee)
    

    next_url = "/TeamLead/Dashbord/"

    context ={
        'teams': teams,
        'profile': employee,
        'company_name': companys,
        'employee_dets': employee,
        'count': teams.count(),
        'page_title': 'Manage Your Team',
        'subtitle': companys,
        'unit': 'Employees',
        'search_id': 'employeeSearch',
        'search_placeholder': 'Search employees by name, user name, email or role...',
        'back_url': next_url,
        'profile':employee,
        'admin_count': admin_count,
        'manager_count': manager_count,

    }
    return render(request, "Hr_App/manageTeam.html", context)


@login_required
def view_employee(request, employee_id):
    login_user = request.session.get("username")
    profile = TeamLead.objects.filter(username=login_user).first()
    company_employee = get_object_or_404(Employee, id=employee_id)
    total_days_in_company = (current_time.date() - company_employee.joining_date).days
    company_id = request.session.get("company_id")

    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    # Calculate work status
    if company_employee:
        total_tasks = Task.objects.filter(assigned_to=company_employee, status="Accepted").count()
        completed_tasks = TaskProgress.objects.filter(task__assigned_to=company_employee, status="Completed").count()
        if total_tasks > 0:
            completion_percent = int((completed_tasks / total_tasks) * 100)
        else:
            completion_percent = 0

        # Status message based on completion %
        if completion_percent >= 90:
            status_message = "🔥 Outstanding performance! Keep leading the way."
            bar_color = "bg-green-600"
        elif completion_percent >= 70:
            status_message = "✅ Great job! Stay consistent."
            bar_color = "bg-lime-500"
        elif completion_percent >= 40:
            status_message = "🕒 Decent progress, but you can do better."
            bar_color = "bg-yellow-500"
        elif completion_percent > 0:
            status_message = "⚠️ Needs improvement. Try to focus more."
            bar_color = "bg-amber-500"
        else:
            status_message = "❌ No task activity yet. Let's get started!"
            bar_color = "bg-red-600"

        work_status = {
            "completion_percent": completion_percent,
            "status_message": status_message,
            "bar_color": bar_color
        }


    next_url = request.META.get('HTTP_REFERER', '')

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
        "company_employee": company_employee,
        "employee": company_employee,
        "work_status": work_status,

    }
    return render(request, "view_employee.html", context)


@login_required
@csrf_protect
def delete_employee(request, employee_id):
    if request.method == "POST":
        employee = get_object_or_404(Employee, id=employee_id)
        company_name = employee.company.name
        username = employee.username
        employee.delete()
        messages.success(
            request,
            f"✅ Employee '{username}' from company '{company_name}' was deleted successfully!"
        )
    else:
        messages.error(request, "❌ Invalid request method. Please try again.")

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
    user_dets = get_object_or_404(TeamLead, username=login_user)

    companys = Company.objects.filter(created_by=user_dets).first()
    members_count = Employee.objects.filter(company=companys).count()

    teams = Team.objects.filter(created_by=user_dets)
    # emp_ids = teams.values_list('members__id', flat=True).distinct()
    # unassigned_employees = Employee.objects.filter(company=companys).exclude(id__in=emp_ids)
    unassigned_employees = Employee.objects.filter(company=companys)

    if request.method == 'POST':
        team_name = request.POST.get("team_name")
        team_description = request.POST.get("team_description")
        team_slogan = request.POST.get("team_slogan")
        team_members = request.POST.getlist("team_members")

        if not team_members:
            messages.error(request, "Please provide at least one employee entry.")
            return redirect("HrApp:Build_Team")
        teams_created = Team.objects.all()
        for teams in teams_created:
            if teams.name == team_name:
                try:
                    # Step 1: Create the team without members
                    team = Team.objects.create(
                        name=team_name,
                        description=team_description,
                        slogan=team_slogan,
                        created_by=user_dets,
                        company=companys,
                        is_active=True,
                    )

                    # Step 2: Add members using .set()
                    team.members.set(team_members)

                    messages.success(request, f'Team "{team_name}" created successfully with {len(team_members)} members.')
                    return redirect("HrApp:Manage_Team")
                except Exception as e:
                    messages.error(request, f'Error for creating Team {team_name}, Sorrry of the in convinence plese create again.')
                    return redirect("HrApp:Build_Team")
            else:
                messages.error(request, f'Team with the name {team_name} is already created so use some other name.')
                return redirect("HrApp:Build_Team")


                
    context = {
        'employee_dets': user_dets,
        'company': companys,
        "show_company_form": not Company.objects.exists(),
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
        # 'back_url': next_url,
        'profile': user_dets,
        'searchFilterBar': False,
        'teams': teams,
        'unassigned_employees':unassigned_employees,
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
def active_memebrs(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=profile).first()

    teams = Team.objects.filter(created_by=profile, is_active=True)
    team_members = []
    team_members_count = 0
    for team in teams:
        team_members += team.members.all()
        team_members_count += team.total_members()


    next_url = "/TeamLead/Dashbord/"

    context = {
        'employee_dets': profile,
        'count': team_members_count,
        'team_members': team_members,
        'page_title': 'Active Members',
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
    return render(request, 'Hr_App/active_members.html', context)


@login_required
def active_teams(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=profile).first()

    teams = Team.objects.filter(created_by=profile, is_active=True).all()

    teams_count = teams.count()
    

    next_url = '/TeamLead/Dashbord/'

    context = {
        'employee_dets': profile,
        'count': teams_count,
        'Teams': teams,
        'page_title': "Active Team's",
        'subtitle': companys,
        'unit': 'Team',
        'defaultFilter': 'all',
        'search_id': 'employeeSearch',
        'search_placeholder': 'Search Team by its name ...',
        'back_url': next_url,
        'profile':profile,
        'searchFilterBar': True,
    }
    return render(request, 'Hr_App/active_teams.html', context)


@login_required
def edit_active_teams(request, team_id):
    team = Team.objects.get(id=team_id)
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    all_employees = Employee.objects.filter(company=team.company)

    if request.method == "POST":
        # Get incoming values
        selected_ids = request.POST.getlist('teamMembers')
        new_name = request.POST.get('teamName')
        new_description = request.POST.get('teamDescription')
        new_status = 'teamStatus' in request.POST  # Checkbox presence means it's checked (i.e., active)

        # Track changes
        has_changes = False

        # Check for name change
        if new_name != team.name:
            team.name = new_name
            has_changes = True

        # Check for description change
        if new_description != team.description:
            team.description = new_description
            has_changes = True

        # Check for team status change (Active/Inactive)
        if new_status != team.is_active:
            team.is_active = new_status
            has_changes = True

        # Check for team members change
        current_member_ids = list(team.members.values_list('id', flat=True))
        selected_ids_int = list(map(int, selected_ids))  # Ensure both lists are int

        if sorted(current_member_ids) != sorted(selected_ids_int):
            team.members.set(Employee.objects.filter(id__in=selected_ids_int))
            has_changes = True

        # Save if anything changed
        if has_changes:
            team.save()
            messages.success(request, f'Team updates were applied successfully to "{team.name}".')
        else:
            messages.info(request, f'There were no changes or major updates in the team "{team.name}".')

        return redirect('HrApp:active_teams')


    referer = request.META.get('HTTP_REFERER')

    context = {
        'page_title':"Update Team",
        'subtitle':team.name,
        'count':team.total_members(),
        'unit':'Members',
        'team':team,
        'all_employees': all_employees,
        'back_url': referer,
        'profile':profile,
    }
    return render(request, 'Hr_App/edit_active_team.html', context)


@login_required
def pendingTask(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")

    employee = get_object_or_404(TeamLead, username=login_user, created_companies=company_id)
    companys = Company.objects.filter(created_by=employee).first()

    pending_task = Task.objects.filter(assigned_by=employee, status="Pending").order_by("-due_date")

    for task in pending_task:
        if task.due_date:
            today = current_time.date()
            task.daysLeft = (task.due_date - today).days
        else:
            task.daysLeft = None
    pending_task_count = pending_task.count()
    next_url = request.META.get('HTTP_REFERER') or "/TeamLead/Dashboard/"

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
    return render(request, 'Hr_App/pending_task.html', context)


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
    next_url = "/TeamLead/Dashbord/"

    context = {
        'employee_dets': employee,
        'pending_tasks': pending_task,
        'count': pending_task_count,
        'page_title': 'All Completed Tasks',
        'subtitle': companys,
        'unit': 'tasks',
        'filters': [
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
            {'value': 'all', 'label': 'All Time'},
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
    current_time = now()

    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    if not employee:
        messages.error(request, "Employee not found.")
        return redirect("HrApp:Dashboard")
    
    companys = Company.objects.filter(created_by=employee).first()

    # Get tasks created today
    today_tasks = Task.objects.filter(assigned_by=employee, created_at__date=current_time.date())
    
    # Fetch progress related to today's tasks
    progress_queryset = TaskProgress.objects.filter(task__in=today_tasks)

    # Store all unique tasks being tracked (to avoid duplicates)
    pending_task = list(set(progress_queryset.values_list("task", flat=True))) if progress_queryset.exists() else list(today_tasks)

    # Prepare mapping of completed tasks
    completed_task = progress_queryset.filter(status="Completed")
    completed_task_ids = set(completed_task.values_list("task_id", flat=True))

    # Add status to each task
    # for task in today_tasks:
    #     task.updateStatus = 'Accepted & Completed' if task.id in completed_task_ids else 'Accepted'

    for task in pending_task:
        if task.status == "Accepted":
            for task in today_tasks:
                task.updateStatus = 'Accepted & Completed' if task.id in completed_task_ids else 'Accepted'
        else:
            task.updateStatus = 'Pending' 

    context = {
        'employee_dets': employee,
        'pending_tasks': today_tasks,
        'count': today_tasks.count(),
        'page_title': 'All Accepted Tasks',
        'page_subTitle': f"Displaying tasks created on {current_time.date()}",
        'subtitle': companys,
        'unit': 'tasks',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, due date or assigned to...',
        'back_url': "/TeamLead/Dashbord/",
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

    next_url = "/TeamLead/Dashbord/"

    context = {
        'profile':employee,
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
def EmployeeStatus(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    companys = Company.objects.filter(created_by=employee).first()

    # user_on_leave = WorkLeave.objects.filter(user__company=companys, user__status="onleave")
    user_on_leave = Employee.objects.filter(company=companys)
    user_on_leave_count = user_on_leave.count()


    if 'TeamLead/modify_leave' in request.META.get('HTTP_REFERER'):
        next_url = "HrApp:Dashboard"
    else:
        next_url = next_url = "/TeamLead/Dashbord/"

    context = {
        'employee_dets': user_on_leave,
        'count': user_on_leave_count,
        'page_title': 'Employees Currently on Leave',
        'subtitle': companys,
        'unit': 'Employees',
        'filters': [
            {'value': 'all', 'label': 'All'},
            {'value': 'week', 'label': 'This Week'},
            {'value': 'month', 'label': 'This Month'},
            {'value': 'year', 'label': 'This Year'},
        ],
        'defaultFilter': 'all',
        'search_id': 'taskSearch',
        'search_placeholder': 'Search tasks by name, username, full name or employee id...',
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
    
    next_url = "/TeamLead/Dashbord/"

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
    
    next_url = "/TeamLead/Dashbord/"

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
def view_team(request, team_id, deletion):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    employee = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()

    team = get_object_or_404(Team, id=team_id)
    employees = team.members.all()

    # Set the default back URL
    referer = request.META.get('HTTP_REFERER')

    context = {
        'employee_dets': employee,
        'count': team.total_members(),
        'unit': 'Employees',
        'page_title': 'Team Members',
        'subtitle': team.name,
        'team': team,
        'employees': employees,
        'back_url': referer,
        'searchFilterBar': True,
        'search_id': 'employeeSearch',
        'search_placeholder': 'Search Employee by name, contact, department or position...',
        'profile':employee,
        'deletion':deletion
    }

    return render(request, 'Hr_App/view_team.html', context)


@login_required
def all_users(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    # Get the company and all its members
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    company = Company.objects.filter(created_by=profile).first()

    user_count =  company.total_members()
    
    # Get all users in the company except the current user
    all_employees = Employee.objects.filter(company=company).exclude(username=login_user)
    all_hr = HR.objects.filter(company=company).exclude(username=login_user)
    all_team_leads = TeamLead.objects.filter(company=company).exclude(username=login_user)
    

    # Counts for each category
    hr_count = all_hr.count()
    team_leads_count = all_team_leads.count()
    employees_count = all_employees.count()
    
    # Set the default back URL
    back_url = '/TeamLead/Dashbord/' if '/TeamLead/profile_details/' in request.META.get('HTTP_REFERER', '') else request.META.get('HTTP_REFERER', '')


    meta = request.META

    context = {
        'company': company,
        'hr_users': all_hr,
        'team_leads': all_team_leads,
        'employees': all_employees,
        'hr_count': hr_count,
        'team_leads_count': team_leads_count,
        'employees_count': employees_count,
        'page_title': 'Company Directory',
        'subtitle': f'View your all colleagues in {company.name}',
        'profile': profile,
        'back_url': back_url,
        'count': user_count,
        'unit': 'User',
        'meta':meta
    }
    return render(request, 'Hr_App/all_users.html', context)


@login_required
def feth_users_dets(request, userId):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    # Get the company and all its members
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    company = Company.objects.filter(created_by=profile).first()
    user = None

    try:
        user = HR.objects.get(id=userId)
    except HR.DoesNotExist:
        try:
            user = TeamLead.objects.get(id=userId)
        except TeamLead.DoesNotExist:
            try:
                user = Employee.objects.get(id=userId)
            except Exception as e:
                messages.error(request, f'Error to find user:- {e}')
                return redirect('HrApp:all_users')
            
        # Set the default back URL
    back_url = request.META.get('HTTP_REFERER')
    meta = request.META


    context = {

        'user': user,
        'profile':profile,
        'back_url':back_url,
        'page_title': f"Profile of {user.username}",
        'subtitle': f'Employee of company {company.name}',
        'count':company.total_members(),
        'unit':'Member',
        'meta':meta
    }
    return render(request, 'user_profile_modal_content.html', context)


@login_required
def user_settings(request):
    return render(request, 'Hr_App/Settings/user_settings.html')


@login_required
def personal_details(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")
    
    # Get the company and all its members
    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    company = Company.objects.filter(created_by=profile).first()
    return render(request, 'Hr_App/Settings/personal_details.html')


# @login_required
# def skill_preferences(request):
#     login_user = request.session.get("username")
#     company_id = request.session.get("company_id")
    
#     # Get the company and all its members
#     profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
#     company = Company.objects.filter(created_by=profile).first()

#     context = {
#         'user':profile,
#     }
#     return render(request, 'Hr_App/Settings/skill_preferences.html', context)

@login_required
def skill_preferences(request):
    login_user = request.session.get("username")
    company_id = request.session.get("company_id")

    profile = TeamLead.objects.filter(username=login_user, created_companies=company_id).first()
    company = Company.objects.filter(created_by=profile).first()

    if request.method == 'POST':
        try:
            # Check if this is the final form submission (not the AJAX one)
            if 'skills_data' in request.POST:
                skills_data = json.loads(request.POST.get('skills_data', '[]'))
                
                # Add new skills
                for skill in skills_data:
                    name = skill.get('name')
                    proficiency = int(skill.get('proficiency', 1))
                    
                    if name and 1 <= proficiency <= 5:
                        Co_Curricular.objects.create(
                            name=name,
                            proficiency=proficiency,
                            Hr=profile
                        )
                
                messages.success(request, 'Skills saved successfully!')
                return redirect('HrApp:skill_preferences')
                
        except json.JSONDecodeError:
            messages.error(request, 'Invalid skills data format')
        except Exception as e:
            messages.error(request, f'Error saving skills: {str(e)}')
            return redirect('HrApp:skill_preferences')

    # Get existing skills for display
    existing_skills = Co_Curricular.objects.filter(Hr=profile).order_by('name')
    
    context = {
        'user': profile,
        'existing_skills': existing_skills,
    }
    return render(request, 'Hr_App/Settings/skill_preferences.html', context)



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



