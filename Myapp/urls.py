from django.urls import path
from . import views

app_name = "Myapp"

urlpatterns = [
    #Login Logut User to App Connection
    path("", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path('activate/<str:role>/<uidb64>/<token>/', views.activate_account, name='activate'),
]

