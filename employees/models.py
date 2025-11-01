from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    position = models.CharField(max_length=100, default="Staff")
    restaurant_name = models.CharField(max_length=255, blank=True, default="")
    address = models.TextField(blank=True, default="Davao City")  # ✅ this avoids prompt
    status = models.CharField(max_length=50, default="active")
    date_started = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
