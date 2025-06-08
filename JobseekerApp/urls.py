from django.urls import path
from . import views

app_name="JobseekerApp"

urlpatterns = [
    path('Dashboard/', views.Dashboard, name="dashboard"),
    path('Find_Job/', views.Find_Job, name="find_job"),
    path('Saved_Jobs/', views.Saved_Jobs, name="saved_jobs"),
    path('Resume/', views.Resume, name="resume"),
    path('Ai_Chat_Bot/', views.Ai_Chat_Bot, name="ai_chat_bot"),
    path('Messages/', views.Messages, name="messages"),
    path("LogOutUSer/", views.logout_view, name="logout"),
]