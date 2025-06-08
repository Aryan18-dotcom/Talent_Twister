from django.urls import path
from . import views

app_name = "EmployeeApp"

urlpatterns = [
    path('Dashboard/', views.dashboard, name='dashboard'),
    path('accept_task/<int:task_id>/', views.accept_task, name='accept_task'),
    path("LogOutUSer/", views.logout_view, name="logout"),
    path('settings/', views.setting, name="settings"),
    path('Profile_Settings/', views.profile_settings, name="profile_settings"),
    path('update_profile/', views.update_profile, name="update_profile"),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/pending_task_complete/', views.pending_task_complete, name='pending_task_complete'),
    path('dashboard/completed/', views.dashboard, name='complete_task_dashboard'),
    path('team_members/', views.teamMember, name="team_members"),
    path('pending_task/', views.pendingTask, name="pending_task"),
    path('completed_task/', views.completedTask, name="completed_task"),
    path('all_tasks/', views.AllTask, name="all_tasks"),
    path('leave_request/', views.leave_request, name="leave_request"),
    path('leave_history/', views.leave_history, name="leave_history"),
    path('leave_status/', views.leave_status, name="leave_status"),


    path('chats/', views.chat_list, name='chat_list'),
    path('start_chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.view_chat, name='view_chat'),
]

