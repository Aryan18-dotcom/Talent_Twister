from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

# Example department choices — you can modify as needed
DEPARTMENT_CHOICES = [
    ('General', 'General'),
    ('HR', 'Human Resources'),
    ('Engineering', 'Engineering'),
    ('Sales', 'Sales'),
    ('Marketing', 'Marketing'),
    ('Support', 'Customer Support'),
    ('Finance', 'Finance'),
    ('IT', 'Information Technology'),
    ('Legal', 'Legal'),
    ('Operations', 'Operations'),
    ('Product', 'Product Management'),
    ('Design', 'Design'),
    ('Research', 'Research and Development'),
    ('Quality Assurance', 'Quality Assurance'),
    ('Administration', 'Administration'),
    ('Logistics', 'Logistics'),
    ('Public Relations', 'Public Relations'),
    ('Training', 'Training and Development'),
    ('Procurement', 'Procurement'),
    ('Compliance', 'Compliance'),
    ('Data Science', 'Data Science'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

USER_STATUS_CHOICES = [
    ('active', 'Active'),
    ('onleave', 'On Leave'),
    ('inactive', 'Inactive'),
    ('terminated', 'Terminated'),
]

# ✅ TeamLead Model
class TeamLead(models.Model):
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Hashed password
    image = models.ImageField(upload_to="hr_pics/", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Undisclosed", null=True, blank=True)
    teamLead_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default="Team Leader")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default="General")
    joining_date = models.DateField(default=timezone.now)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True)
    leave = models.IntegerField(default=0)  # Corrected spelling
    about = models.TextField(null=True, blank=True, max_length=175)
    status = models.CharField(max_length=20, choices=USER_STATUS_CHOICES, default='Inactive')
    days_worked = models.IntegerField(default=0)  # Days worked in the current month


    def save(self, *args, **kwargs):
        # Auto-generate email if not provided
        if not self.email and self.company:
            self.email = f"{self.username}@{self.company.domain}"

        # Auto-generate employee ID if not set
        if not self.teamLead_id:
            self.teamLead_id = f"TMLED{uuid.uuid4().hex[:6].upper()}"


        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"
    

# ✅ Company Model
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(TeamLead, on_delete=models.SET_NULL, related_name="created_companies", null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


# ✅ Employee Model
class Employee(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name="employees")
    username = models.CharField(max_length=150)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True)  # Allow blank email, auto-generated
    password = models.CharField(max_length=255)  # Hashed password
    image = models.ImageField(upload_to="employee_pics/", null=True, blank=True)
    is_active = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default="Employee")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default="General")
    joining_date = models.DateField(default=timezone.now)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True)
    leave = models.IntegerField(default=0)  # Corrected spelling
    about = models.TextField(null=True, blank=True, max_length=175)
    skills = models.TextField(blank=True, null=True)  # Comma-separated
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Undisclosed", null=True, blank=True)
    employee_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=20, choices=USER_STATUS_CHOICES, default='Inactive')
    days_worked = models.IntegerField(default=0)  # Days worked in the current month


    def get_skills_list(self):
        """Returns a list of skills from a comma-separated string"""
        return [skill.strip() for skill in self.skills.split(',')] if self.skills else []

    def save(self, *args, **kwargs):
        # Auto-generate email if not provided
        if not self.email and self.company:
            self.email = f"{self.username}@{self.company.domain}"

        # Auto-generate employee ID if not set
        if not self.employee_id:
            self.employee_id = f"EMP{uuid.uuid4().hex[:6].upper()}"


        super().save(*args, **kwargs)

    def __str__(self):
        return self.username




# ✅ JobSeeker Model
class JobSeeker(models.Model):
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Hashed password
    image = models.ImageField(upload_to="jobseeker_pics/", null=True, blank=True)

    def __str__(self):
        return f"{self.username} (Job Seeker)"


# ✅ Task Model (HR Assigns Tasks to Employees)
class Task(models.Model):
    assigned_by = models.ForeignKey(TeamLead, on_delete=models.CASCADE, related_name="assigned_tasks")
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    task_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"{self.title} → {self.assigned_to.username} ({self.status})"


# ✅ Task Progress Model (Combining TaskStatus & TaskCompletion)
class TaskProgress(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='progress')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="task_progress")

    action_date = models.DateTimeField(default=timezone.now, null=True, blank=True)  # When the employee accepts the task
    completion_date = models.DateTimeField(null=True, blank=True) # When completed

    STATUS_CHOICES = [
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="Pending")

    COMPLETION_STATUS_CHOICES = [
        ('early', 'Completed Early'),
        ('ontime', 'Completed On Time'),
        ('late', 'Completed Late'),
    ]
    completion_type = models.CharField(max_length=10, choices=COMPLETION_STATUS_CHOICES, null=True, blank=True)

    days_difference = models.IntegerField(null=True, blank=True)  # Difference between due_date & completion_date
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.task.title} - {self.status} by {self.employee.username}"


class WorkLeave(models.Model):
    user = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=50, choices=[
        ('Sick Leave', 'sick'),
        ('Casual Leave', 'casual'),
        ('Vacation Leave', 'vacation'),
        ('Earned Leave', 'earned'),
        ('Unpaid Leave', 'unpaid'),
        ('Emergency Leave', 'emergency')
    ], default='Earned Leave')

    start_date = models.DateField()
    end_date = models.DateField()

    modified_start_date = models.DateField(null=True, blank=True)
    modified_end_date = models.DateField(null=True, blank=True)

    reason_title = models.TextField()  # Employee's reason_title
    reason_discription = models.TextField()  # Employee's reason_discription
    contact_info = models.CharField(max_length=20, null=True, blank=True)# Employee's phonenumber for the leave
    rejection_reason = models.TextField(null=True, blank=True)  # HR's rejection note
    reconsider_note = models.TextField(null=True, blank=True)   # HR reconsideration explanation
    modification_note = models.TextField(null=True, blank=True)   # HR reconsideration explanation

    approved_by = models.ForeignKey('TeamLead', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')

    leave_balance = models.IntegerField(default=20)

    status=models.CharField(max_length=50, choices=[
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Modified','Modified'),
        ('Reconsidered','Reconsidered'),
        ('Rejected','Rejected'),
    ], default='Pending')
    

    duration = models.FloatField(null=True, blank=True)
    modified_duration = models.IntegerField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_responded = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    is_reconsidered = models.BooleanField(default=False)
    is_half_day = models.BooleanField(default=False)
    half_day_period = models.CharField(max_length=20, choices=[
        ('First Half', 'First Half'),
        ('Second Half', 'Second Half'),
    ], default='First Half') 
    notify_team = models.BooleanField(default=True) #Send notification to your team about your absence
    out_of_office = models.BooleanField(default=False) #Automatically reply to emails during your absence
    delegate_tasks = models.BooleanField(default=False) #Assign your tasks to team members during leave

    reconsidered_at = models.DateTimeField(null=True, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)

    def total_days(self):
        start = self.modified_start_date or self.start_date
        end = self.modified_end_date or self.end_date
        return (end - start).days + 1

    # def save(self, *args, **kwargs):
    #     start = self.start_date or self.modified_start_date
    #     end =  self.end_date or self.modified_end_date
    #     self.duration = (end - start).days + 1
    #     self.modified_duration = (end - start).days + 1
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.start_date} to {self.end_date})"

    


class Chat(models.Model):
    members = models.ManyToManyField(User, related_name='chats')
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name if self.name else ", ".join(user.username for user in self.members.all())

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        receivers = ", ".join(user.username for user in self.chat.members.exclude(id=self.sender.id))
        return f"{self.sender.username} to {receivers}"
    
