from django.urls import path
from django.views.generic import TemplateView

from .views import DeleteAccountView

app_name = "accounts"

urlpatterns = [
    path(
        "profile/",
        TemplateView.as_view(template_name="profile.html"),
        name="profile",
    ),
    path(
        "delete-account/", DeleteAccountView.as_view(), name="delete_account"
    ),
]
