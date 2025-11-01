from django.contrib import admin
from .models import DonationDrive

@admin.register(DonationDrive)
class DonationDriveAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'created_at')
