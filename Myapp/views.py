from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Company, TeamLead, Employee, JobSeeker
from django.contrib import messages
import logging
from datetime import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from types import SimpleNamespace


current_time = datetime.now()


# User Login and Signup Functions To create(SignUP_User) and Login If User_Signuped(Checks and Login to respective Dashboard)

# SingUp "Create New User In DB Through Models"

# Custom Token Generator

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) + text_type(user.is_active)
        )

account_activation_token = CustomTokenGenerator()

def generate_activation_token(user):
    return account_activation_token.make_token(user)

def verify_activation_token(user, token):
    return account_activation_token.check_token(user, token)


def signup(request):
    if request.method == "POST":
        email = request.POST.get("email").strip()
        username = request.POST.get("username").strip()
        full_name = request.POST.get("fullName").strip()
        password = request.POST.get("password").strip()
        role = request.POST.get("role")

        if not (email and username and full_name and password and role):
            messages.error(request, "All fields are required!")
            return redirect("Myapp:signup")

        password_hashed = password  # NOTE: Replace with secure hash later

        if role == "Admin":
            if TeamLead.objects.filter(username=username).exists() or TeamLead.objects.filter(email=email).exists():
                return HttpResponse("<script>if (confirm('HR account already exists! Do you want to login?')){window.location.href='/';}else{window.location.href='/signup';}</script>")
            
            user = TeamLead.objects.create(
                username=username,
                full_name=full_name,
                persional_email=email,
                password=password_hashed,
                is_active=False,
            )

            send_activation_email(request, user, role)
            messages.success(request, "Admin account created! An activation link has been sent to your Personal email.")
            return redirect("Myapp:login")

        elif role == "JobSeeker":
            if JobSeeker.objects.filter(username=username).exists() or JobSeeker.objects.filter(email=email).exists():
                return HttpResponse("<script>if (confirm('JobSeeker account already exists! Do you want to login?')){window.location.href='/';}else{window.location.href='/signup';}</script>")
            
            user = JobSeeker.objects.create(
                username=username,
                full_name=full_name,
                email=email,
                password=password_hashed,
                is_active=False,
            )
            print(f"User created: {user.username}, Email: {user.email}, Role: {role}")  # Debugging line
            send_activation_email(request, user, role)
            messages.success(request, "JobSeeker account created! An activation link has been sent to your email.")
            return redirect("Myapp:login")

        messages.error(request, "Invalid role selected!")
        return redirect("Myapp:signup")

    return render(request, "signup.html")


def send_activation_email(request, user, role):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_activation_token(user)
    domain = get_current_site(request).domain
    activation_link = f"http://{domain}/activate/{role}/{uid}/{token}/"

    try:
        email_subject = "Activate Your Talent Twister Account"
        email_body = render_to_string('emails/account_activation.html', {
            'name': user.full_name,
            'activation_link': activation_link,
            'role': role,
        })

        email = EmailMessage(
            email_subject,
            email_body,
            to=[user.persional_email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)

    except Exception as e:
        print("Email send error:", e)


def activate_account(request, role, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        if role == "Admin":
            user = get_object_or_404(TeamLead, pk=uid)
        elif role == "JobSeeker":
            user = get_object_or_404(JobSeeker, pk=uid)
        else:
            messages.error(request, "Invalid role specified!")
            return redirect("Myapp:login")
        
        if user.is_active:
            messages.info(request, "Account already activated!")
            return redirect("Myapp:login")

        if account_activation_token.check_token(user, token):
            # Activate the account
            user.is_active = True
            user.save()
            
            # Create Django auth user and log them in
            auth_user, _ = User.objects.get_or_create(
                username=user.username,
                defaults={'email': user.persional_email}
            )
            login(request, auth_user)
            
            # Set up session variables based on role
            if role == "Admin":
                request.session["employee_id"] = user.id
                request.session["username"] = user.username
                request.session["role"] = "HR"
                return redirect("HrApp:Dashboard")
                    
            elif role == "JobSeeker":
                request.session["JobSeeker_id"] = user.id
                request.session["username"] = user.username
                request.session["role"] = "JobSeeker"
                return redirect("JobseekerApp:dashboard")
                
            messages.success(request, "Your account has been activated successfully")
            
        else:
            messages.error(request, "Activation link is invalid or has expired.")
            return redirect("Myapp:login")

    except Exception as e:
        user.is_active = False
        user.save()
        print("Activation Error:", e)
        messages.error(request, "An error occurred during activation. Please try again.")
        return redirect("Myapp:login")


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
        try:
            hr_user = TeamLead.objects.filter(username=username).first()

            if hr_user and password == hr_user.password:
                # Create or get the User model instance
                user, _ = User.objects.get_or_create(username=hr_user.username, email=hr_user.persional_email)
                login(request, user)

                hr_user.is_active = True

                # Proceed only if last login was not today
                if hr_user.last_login is None or hr_user.last_login.date() != current_time.date():
                    company = hr_user.created_companies.first()

                    if company:  # Ensure the company exists
                        if hr_user.days_worked < company.total_days_to_work:
                            hr_user.days_worked += 1
                        else:
                            hr_user.days_worked = 1

                    hr_user.last_login = current_time
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
                    return redirect("HrApp:Dashboard")  # Replace with your actual view name
                
            

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

                if employee_user.last_login is None or employee_user.last_login.date() != current_time.date():

                    if employee_user.company:  # Ensure the company exists
                        if employee_user.days_worked < employee_user.company.total_days_to_work:
                            employee_user.days_worked += 1
                        else:
                            employee_user.days_worked = 1

                    employee_user.last_login = current_time
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

    return render(request, "index.html")