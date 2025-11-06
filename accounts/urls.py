# accounts/urls.py
from django.urls import path
from .views import (
    register_owner,
    owner_profile,
    update_owner,
    LoginView,
)

urlpatterns = [
    path("register/", register_owner, name="register-owner"),
    path("me/", owner_profile, name="owner-profile"),
    path("update/", update_owner, name="update-owner"),
    path("login/", LoginView.as_view(), name="account-login"),
]
