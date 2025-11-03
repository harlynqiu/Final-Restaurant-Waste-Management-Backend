# rewards/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# --------------------------------------------
# 🏆 Reward Points Model
# --------------------------------------------
class RewardPoint(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reward_points')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

    def add_points(self, amount):
        """Safely add or deduct points"""
        self.points += amount
        if self.points < 0:
            self.points = 0
        self.save()


# --------------------------------------------
# 🧾 Reward Transaction History
# --------------------------------------------
class RewardTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_transactions')
    # ✅ Use string-based FK to avoid circular import
    pickup = models.ForeignKey(
        "trash_pickups.TrashPickup",   # ← string reference, no direct import
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reward_transactions"
    )
    points = models.IntegerField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} pts - {self.description}"


# --------------------------------------------
# 🎟️ Voucher Model
# --------------------------------------------
class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    points_required = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        """Check if the voucher is still active and not expired"""
        return self.is_active and (not self.expires_at or self.expires_at >= timezone.now())


# --------------------------------------------
# 🎁 Reward Redemption Model
# --------------------------------------------
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
