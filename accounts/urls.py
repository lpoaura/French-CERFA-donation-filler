from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login_page.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
