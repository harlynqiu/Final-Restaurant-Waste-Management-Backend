from django.db import models
from django.contrib.auth.models import User
from donations.models import DonationDrive  # ✅ Import directly (safe — no circular link)
from django.utils import timezone

class TrashPickup(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trash_pickups")
    restaurant_name = models.CharField(max_length=255)
    pickup_address = models.TextField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    waste_type = models.CharField(max_length=50)
    scheduled_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    # 🟢 NEW FIELD
    donation_drive = models.ForeignKey(
        DonationDrive,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trash_pickups"
    )

    def __str__(self):
        return f"{self.restaurant_name} ({self.status})"

    # ✅ Restaurant address (also used as pickup address)
    pickup_address = models.CharField(max_length=255)

    # ✅ Optional scheduled date and time
    scheduled_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.pickup_address:
            self.pickup_address = self.restaurant_name
        else:
            # Always ensure both match
            self.restaurant_name = self.pickup_address

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.restaurant_name} - {self.status}"


# --------------------------------------------
# 🎁 Voucher Model
# --------------------------------------------
class Voucher(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_required = models.IntegerField()
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.points_required} pts"

# --------------------------------------------
# 🎟️ Reward Redemption Record
# --------------------------------------------
class RewardRedemption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} redeemed {self.voucher.name}"
