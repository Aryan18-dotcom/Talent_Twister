from django.urls import path
from . import views

app_name = "HrApp"

urlpatterns = [
    path("Dashbord/", views.Dashboard, name="Dashboard"),
    path("Dashbord/Completed_Task", views.Dashboard, name="Completed_Task"),
    path("Dashbord/Accepted_Task", views.Dashboard, name="Accepted_Task"),
    path("CreateCompany/", views.create_company, name="CreateCompany"),
    path("Post_Task/", views.Post_Task, name="Post_Task"),
    path("Manage_Team/", views.Manage_Team, name="Manage_Team"),
    path('view_employee/<int:employee_id>/', views.view_employee, name='view_employee'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path("Build_Team/", views.Build_Team, name="Build_Team"),
    path('settings/', views.setting, name="settings"),
    path('Profile_Settings/', views.profile_settings, name="profile_settings"),
    path('update_profile/', views.update_profile, name="update_profile"),
    path('active_members/', views.active_memebrs, name="active_members"),
    path('active_teams/', views.active_teams, name="active_teams"),
    path('edit_active_teams/<int:team_id>', views.edit_active_teams, name="edit_active_teams"),
    path('pending_task/', views.pendingTask, name="pending_task"),
    path('completed_task/', views.completedTask, name="completed_task"),
    path('accepted_task/', views.acceptedTask, name="accepted_task"),
    path('all_tasks/', views.AllTask, name="all_tasks"),
    path('delete_company/<int:company_id>/', views.delete_company, name='delete_company'),
    path('employees_status/', views.EmployeeStatus, name="EmployeeStatus"),
    path('accept_leave/<int:user_id>/', views.accept_leave, name='accept_leave'),
    path('reject_leave/<int:user_id>/', views.reject_leave, name='reject_leave'),
    path('modify_leave/<int:user_id>/', views.modify_leave, name='modify_leave'),
    path('reconsider_leave/<int:user_id>/', views.reconsider_leave, name='reconsider_leave'),
    path('view_team/<int:team_id>/<str:deletion>', views.view_team, name='view_team'),
    path('all_users/', views.all_users, name='all_users'),
    path('profile_details/<int:userId>/', views.feth_users_dets, name='feth_users_dets'),
    path('personal_details/', views.personal_details, name='personal_details'),
    path('user_settings/', views.user_settings, name='user_settings'),
    path('skill_preferences/', views.skill_preferences, name='skill_preferences'),

    path("LogOutUSer/", views.logout_view, name="logout"),
]