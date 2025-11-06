# trash_pickups/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from donations.models import DonationDrive


class TrashPickup(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    # Restaurant User (Owner)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trash_pickups"
    )

    restaurant_name = models.CharField(max_length=255)
    pickup_address = models.CharField(max_length=255)

    waste_type = models.CharField(max_length=50)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)

    scheduled_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    donation_drive = models.ForeignKey(
        DonationDrive,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trash_pickups",
    )

    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_pickups",
    )

    latitude = models.DecimalField(
        max_digits=10,  # e.g., 123.1234567
        decimal_places=7,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=11,  # e.g., 123.1234567 (more digits before the decimal)
        decimal_places=7,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Pickup #{self.id} - {self.restaurant_name} ({self.status})"

    class Meta:
        ordering = ["-created_at"]


# --------------------------------------------------------
# 🎁 Voucher Model
# --------------------------------------------------------
class Voucher(models.Model):
    """
    Represents a discount voucher redeemable using reward points.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_required = models.IntegerField()
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.points_required} pts"


# --------------------------------------------------------
# 🎟️ Reward Redemption Model
# --------------------------------------------------------
class RewardRedemption(models.Model):
    """
    Tracks each redemption of a voucher by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} redeemed {self.voucher.name}"
