# employees/admin.py
from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "restaurant_name", "position", "status", "latitude", "longitude")
    search_fields = ("name", "restaurant_name", "position")
