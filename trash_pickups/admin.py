from django.contrib import admin
from .models import TrashPickup, Voucher, RewardRedemption

@admin.register(TrashPickup)
class TrashPickupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "restaurant_name",
        "pickup_address",
        "waste_type",
        "weight_kg",
        "status",
        "scheduled_date",
        "driver",
        "created_at",
    )
    list_filter = ("status", "waste_type", "scheduled_date", "created_at")
    search_fields = ("restaurant_name", "pickup_address", "driver__full_name")
    ordering = ("-created_at",)

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "points_required", "discount_value", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "voucher", "is_used", "redeemed_at")
    list_filter = ("is_used", "redeemed_at")
    search_fields = ("user__username", "voucher__name")
