# accounts/urls.py
from django.urls import path
from .views import (register_owner, owner_profile, update_owner,)

urlpatterns = [
    path("register/", register_owner),
    path("me/", owner_profile),
    path("update/", update_owner),
]
