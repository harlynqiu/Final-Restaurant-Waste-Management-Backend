from django.db import models
from django.contrib.auth.models import User
from trash_pickups.models import TrashPickup


# --------------------------------------------
# 🏆 Reward Points Model
# --------------------------------------------
class RewardPoint(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reward_points')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

    def add_points(self, amount):
        """Add or deduct points safely"""
        self.points += amount
        if self.points < 0:
            self.points = 0
        self.save()


# --------------------------------------------
# 🧾 Reward Transaction History
# --------------------------------------------
class RewardTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_transactions')
    pickup = models.ForeignKey(TrashPickup, on_delete=models.CASCADE, null=True, blank=True)
    points = models.IntegerField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} pts - {self.description}"


# --------------------------------------------
# 🧾 Voucher History
# --------------------------------------------
class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        return self.is_active and (not self.expires_at or self.expires_at >= timezone.now())

class RewardRedemption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reward_redemptions")
    item_name = models.CharField(max_length=255)
    points_spent = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("completed", "Completed"),
        ],
        default="pending",
    )

    def __str__(self):
        return f"{self.user.username} - {self.item_name} ({self.status})"