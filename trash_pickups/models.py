# trash_pickups/models.py
from django.db import models
from django.contrib.auth.models import User



class TrashPickup(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trash_pickups')
    restaurant_name = models.CharField(max_length=255)
    waste_type = models.CharField(max_length=100)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    pickup_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

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