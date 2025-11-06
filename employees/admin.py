from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "position",
        "restaurant_name",
        "status",
        "created_at",
    )

    list_filter = ("status", "position")
    search_fields = ("name", "email", "position", "restaurant_name")
