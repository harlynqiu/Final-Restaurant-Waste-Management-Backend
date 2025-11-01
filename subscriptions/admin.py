from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, SubscriptionPayment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "duration_days", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "plan", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("user__username", "plan__name")


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "plan_name_snapshot", "amount", "method", "status", "paid_at")
    list_filter = ("method", "status")
    search_fields = ("user__username", "plan_name_snapshot")
