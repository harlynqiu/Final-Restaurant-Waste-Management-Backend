# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OwnerProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class OwnerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = OwnerProfile
        fields = [
            "id",
            "user",
            "restaurant_name",
            "address",
            "latitude",
            "longitude",
            "status",
        ]
