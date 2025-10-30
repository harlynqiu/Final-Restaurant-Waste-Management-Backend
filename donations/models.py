from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# --------------------------------------------------------
# 🌍 Donation Drive (public campaigns)
# --------------------------------------------------------
class DonationDrive(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_item = models.CharField(max_length=255, help_text="e.g. Surplus Food, Recyclables")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        """Automatically mark active if within start/end date."""
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date and self.is_active


# --------------------------------------------------------
# 🤝 Restaurant Participation / Donation Entry
# --------------------------------------------------------
class DonationParticipation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donations")
    drive = models.ForeignKey(DonationDrive, on_delete=models.CASCADE, related_name="participants")
    donated_item = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, help_text="e.g. 5.0 kg")
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.drive.title} ({self.status})"

    def mark_completed(self):
        """Mark as completed and award reward points."""
        self.status = "completed"
        self.save()

        # 🏆 Lazy import to avoid circular dependency
        try:
            from rewards.models import RewardPoint  # 👈 import inside method
            reward, _ = RewardPoint.objects.get_or_create(user=self.user)
            reward.add_points(
                amount=20,  # 🎁 Default reward for each donation
                description=f"Donation completed for {self.drive.title}",
                transaction_type="earn",
            )
        except Exception as e:
            print("⚠️ Error awarding reward points:", e)
