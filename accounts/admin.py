# accounts/admin.py
from django.contrib import admin
from .models import OwnerProfile


class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurant_name", "status")
    search_fields = ("user__username", "restaurant_name")
    list_filter = ("status",)


admin.site.register(OwnerProfile, OwnerProfileAdmin)
