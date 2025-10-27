from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# ------------------------------------------------
# 📦 Available Plans (Basic / Premium / etc.)
# ------------------------------------------------
class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("enterprise", "Enterprise"),
    ]

    name = models.CharField(max_length=100, choices=PLAN_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()  # e.g. 30, 90, 365
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_name_display()} ({self.price} PHP)"


# ------------------------------------------------
# 🧾 A user's current (or past) subscription
# ------------------------------------------------
class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    auto_renew = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} -> {self.plan.get_name_display()} ({self.status})"

    @property
    def is_active(self):
        return self.status == "active" and self.end_date >= timezone.now()

    def mark_cancelled(self):
        self.auto_renew = False
        self.status = "cancelled"
        self.save()

    def mark_expired_if_needed(self):
        if self.end_date < timezone.now() and self.status == "active":
            self.status = "expired"
            self.save()

    @classmethod
    def create_new_subscription(cls, user, plan: SubscriptionPlan):
        start = timezone.now()
        end = start + timedelta(days=plan.duration_days)
        return cls.objects.create(
            user=user,
            plan=plan,
            start_date=start,
            end_date=end,
            status="active",
            auto_renew=True,
        )


# ------------------------------------------------
# 💳 Payment Log (GCash / Card / Cash)
# ------------------------------------------------
class SubscriptionPayment(models.Model):
    PAYMENT_METHODS = [
        ("gcash", "GCash"),
        ("card", "Card"),
        ("bank", "Bank Transfer"),
        ("cash", "Cash"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscription_payments")
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name="payments")
    plan_name_snapshot = models.CharField(max_length=100)            # freeze plan name at time of payment
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="paid")
    paid_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} paid {self.amount} via {self.method} ({self.status})"
