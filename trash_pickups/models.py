# trash_pickups/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from donations.models import DonationDrive


class TrashPickup(models.Model):
    """
    Represents a waste pickup request from a restaurant.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),          # Created by restaurant
        ("accepted", "Accepted"),        # Driver accepted
        ("in_progress", "In Progress"),  # Driver currently picking up
        ("completed", "Completed"),      # Finished
        ("cancelled", "Cancelled"),      # Cancelled by user/admin
    ]

    # ----------------------------------------------------
    # 🔹 Restaurant Info
    # ----------------------------------------------------
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trash_pickups"
    )
    restaurant_name = models.CharField(
        max_length=255, help_text="Name of the restaurant that requested the pickup"
    )
    pickup_address = models.CharField(
        max_length=255, help_text="Address where the driver should pick up the waste"
    )

    # ----------------------------------------------------
    # 🔹 Waste Details
    # ----------------------------------------------------
    waste_type = models.CharField(max_length=50)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    scheduled_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # ----------------------------------------------------
    # 🔹 Optional Donation Drive
    # ----------------------------------------------------
    donation_drive = models.ForeignKey(
        DonationDrive,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trash_pickups",
        help_text="If the pickup contributes to a donation drive",
    )

    # ----------------------------------------------------
    # 🔹 Assigned Driver
    # ----------------------------------------------------
    driver = models.ForeignKey(
        'drivers.Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pickups'
    )

    # ----------------------------------------------------
    # 🔹 Additional Data (Optional Fields)
    # ----------------------------------------------------
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Latitude of the pickup location"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude of the pickup location"
    )

    # ----------------------------------------------------
    # 🔹 Custom Save Logic
    # ----------------------------------------------------
    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            from employees.models import Employee
            try:
                emp = Employee.objects.get(user=self.user)
                if emp.latitude and emp.longitude:
                    self.latitude = emp.latitude
                    self.longitude = emp.longitude
            except Employee.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        driver_name = self.driver.full_name if self.driver else "Unassigned"
        return f"{self.restaurant_name} ({self.status}) - Driver: {driver_name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Trash Pickup"
        verbose_name_plural = "Trash Pickups"


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
