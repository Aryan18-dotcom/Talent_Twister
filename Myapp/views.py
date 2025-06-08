from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Company, TeamLead, Employee, JobSeeker, Task
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_protect
import os
from django.conf import settings
from django.contrib import messages
import logging


# User Login and Signup Functions To create(SignUP_User) and Login If User_Signuped(Checks and Login to respective Dashboard)

# SingUp "Create New User In DB Through Models"
def signup(request):
    if request.method == "POST":
        email = request.POST.get("email").strip()
        username = request.POST.get("username").strip()
        full_name = request.POST.get("fullName").strip()
        password = request.POST.get("password").strip()
        role = request.POST.get("role")

        # ✅ Validate input fields
        if not (email and username and full_name and password and role):
            return HttpResponse("<script>alert('All fields are required!'); window.location.href='/signup';</script>")

        password_hashed =password  # Hash the password

        if role == "Admin":
            if TeamLead.objects.filter(username=username).exists() or TeamLead.objects.filter(email=email).exists():
                return HttpResponse(
                    "<script>"
                    "if (confirm('HR account already exists! Do you want to continue to login?')) {"
                    "   window.location.href='/';"
                    "} else {"
                    "   window.location.href='/signup';"
                    "} </script>"
                )

            TeamLead.objects.create(username=username, full_name=full_name, email=email, password=password_hashed)
            return HttpResponse("<script>alert('Admin account created successfully! Please login.'); window.location.href='/';</script>")

        elif role == "JobSeeker":
            if JobSeeker.objects.filter(username=username).exists() or JobSeeker.objects.filter(email=email).exists():
                return HttpResponse(
                    "<script>"
                    "if (confirm('JobSeeker account already exists! Do you want to continue to login?')) {"
                    "   window.location.href='/';"
                    "} else {"
                    "   window.location.href='/signup';"
                    "} </script>"
                )

            JobSeeker.objects.create(username=username, full_name=full_name, email=email, password=password_hashed)
            return HttpResponse("<script>alert('JobSeeker account created successfully! Please login.'); window.location.href='/';</script>")

        return HttpResponse("<script>alert('Invalid role selected!'); window.location.href='/signup';</script>")

    return render(request, "signup.html")

# LogIn User "Checks if User Exists in DB, if then 'REDIRECT' to respective Dashboard, and keeps the 'SESSION' maintained

logger = logging.getLogger(__name__)
def login_view(request):
    # ✅ Redirect logged-in users to their dashboard
    if request.user.is_authenticated:
        role = request.session.get("role", "").lower()
        if role == "hr":
            return redirect("HrApp:Dashboard")
        elif role == "employee":
            return redirect("EmployeeApp:dashboard")
        elif role == "jobseeker":
            return redirect("JobseekerApp:dashboard")

    # ✅ Initialize login attempts counter
    if "login_attempts" not in request.session:
        request.session["login_attempts"] = 0

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        companyName = request.POST.get("companyName", "").strip()
        password = request.POST.get("password", "").strip()

        # ✅ HR (Admin) Login
        # ✅ HR (Admin) Login
        try:
            hr_user = TeamLead.objects.filter(username=username).first()

            if hr_user and password == hr_user.password:
                # Create or get the User model instance
                user, _ = User.objects.get_or_create(username=hr_user.username, email=hr_user.email)
                login(request, user)

                hr_user.is_active = True
                hr_user.save()

                # Attempt to get the company if it exists
                company = Company.objects.filter(created_by=hr_user).first()

                request.session["employee_id"] = hr_user.id
                request.session["username"] = username
                request.session["role"] = "HR"
                request.session["login_attempts"] = 0

                if company:
                    request.session["company_id"] = company.id
                    request.session["company_name"] = company.name
                    return redirect("HrApp:Dashboard")
                else:
                    # Redirect HR to create a company if not found
                    messages.info(request, "Please create your company to continue.")
                    return redirect("HrApp:create_company")  # Replace with your actual view name

        except Exception as e:
            logger.error(f"Error during HR login: {e}")
            messages.error(request, "An error occurred during login.")

        
        # ✅ Employee Login
        try:
            company = Company.objects.get(name=companyName)
            employee_user = Employee.objects.filter(username=username, company=company).first()

            if employee_user and password == employee_user.password:
                unique_user_key = f"{companyName}__{username}"
                user, _ = User.objects.get_or_create(
                    username=unique_user_key,
                    defaults={'email': employee_user.email}
                )

                login(request, user)

                # Mark employee as active
                employee_user.is_active = True
                employee_user.save()

                request.session["employee_id"] = employee_user.id
                request.session["username"] = username
                request.session["company_id"] = company.id
                request.session["company_name"] = company.name
                request.session["role"] = "Employee"
                request.session["login_attempts"] = 0
                return redirect("EmployeeApp:dashboard")

        except Company.DoesNotExist:
            messages.error(request, "Company does not exist.")

        # ✅ JobSeeker Login
        job_seeker_user = JobSeeker.objects.filter(username=username).first()
        if job_seeker_user and password==job_seeker_user.password:
            user, _ = User.objects.get_or_create(username=username)
            login(request, user)

            request.session["JobSeeker_id"] = job_seeker_user.id
            request.session["username"] = username
            request.session["role"] = "JobSeeker"
            request.session["login_attempts"] = 0
            return redirect("JobseekerApp:dashboard")

        # ❌ Invalid credentials
        request.session["login_attempts"] += 1
        attempts_left = 3 - request.session["login_attempts"]
        logger.warning(f"Failed login attempt for user: {username}")

        if request.session["login_attempts"] >= 3:
            request.session["login_attempts"] = 0  # reset counter
            messages.error(request, "Too many failed attempts.")
            return redirect("/signup")

        messages.error(request, f"Invalid credentials! Attempts left: {attempts_left}")
        return redirect("Myapp:login")  # Replace with your actual login page name

    return render(request, "login.html")