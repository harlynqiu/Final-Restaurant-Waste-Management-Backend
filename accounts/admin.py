# accounts/admin.py
from django.contrib import admin
from .models import OwnerProfile

@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurant_name", "address", "latitude", "longitude")
    search_fields = ("user__username", "restaurant_name", "address")
    list_filter = ("user__is_active",)
