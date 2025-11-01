from django.contrib import admin
from .models import Driver, DriverLocation

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "vehicle_type",
        "plate_number",
        "status",
        "is_active",
        "date_hired",
    )
    list_filter = ("status", "is_active", "vehicle_type")
    search_fields = ("full_name", "plate_number", "phone_number", "user__username")

@admin.register(DriverLocation)
class DriverLocationAdmin(admin.ModelAdmin):
    list_display = (
        "driver",
        "latitude",
        "longitude",
        "timestamp",
        "is_current",
    )
    list_filter = ("is_current", "timestamp")
    search_fields = ("driver__full_name", "driver__plate_number")
