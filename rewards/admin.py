# rewards/admin.py
from django.contrib import admin
from .models import RewardPoint, RewardTransaction, Voucher, RewardRedemption

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "points_required", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")

@admin.register(RewardPoint)
class RewardPointAdmin(admin.ModelAdmin):
    list_display = ("user", "points")

@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "description", "created_at")

@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ("user", "item_name", "points_spent", "status", "created_at")
