from django.urls import path
from . import views

app_name = "Myapp"

urlpatterns = [
    #Login Logut User to App Connection
    path("", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
]

