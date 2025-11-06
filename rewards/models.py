# rewards/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class RewardPoint(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='reward_points'
    )
    points = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Reward Point"
        verbose_name_plural = "Reward Points"

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

    def add_points(self, amount: int) -> None:
        """Safely add or deduct points (floors at 0)."""
        self.points += amount
        if self.points < 0:
            self.points = 0
        self.save(update_fields=["points"])

class RewardTransaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reward_transactions'
    )
   
    pickup = models.ForeignKey(
        "trash_pickups.TrashPickup",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reward_transactions",
    )
    points = models.IntegerField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.points} pts - {self.description or 'Transaction'}"

class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)                      # Readable name
    description = models.TextField(blank=True, default="")       # Optional description
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    points_required = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='vouchers/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["points_required", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def is_valid(self) -> bool:
        """Check if voucher is active and not expired."""
        return self.is_active and (not self.expires_at or self.expires_at >= timezone.now())

class RewardRedemption(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reward_redemptions"
    )

    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="redemptions",
        help_text="Voucher at the time of redemption (nullable if deleted).",
    )

    item_name = models.CharField(
        max_length=255,
        help_text="Human-friendly name snapshot at redemption time (e.g., '₱50 Discount Voucher').",
    )

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

    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["is_used"]),
        ]

    def __str__(self):
        base = self.item_name or (self.voucher.name if self.voucher else "Reward")
        return f"{self.user.username} - {base} [{self.status}]"

    def mark_used(self) -> None:
        """Mark the redemption as used."""
        if not self.is_used:
            self.is_used = True
            self.save(update_fields=["is_used"])

    def display_name(self) -> str:
        """Prefer saved snapshot; fallback to linked voucher name/code."""
        if self.item_name:
            return self.item_name
        if self.voucher:
            return self.voucher.name or self.voucher.code
        return "Reward"

    def can_be_used(self) -> bool:
        """Simple gate: completed and not yet used."""
        return self.status == "completed" and not self.is_used
