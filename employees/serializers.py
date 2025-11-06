from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "name",
            "email",
            "position",
            "restaurant_name",
            "address",
            "status",
            "latitude",
            "longitude",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "status"]


class EmployeeRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "name",
            "email",
            "position",
            "restaurant_name",
            "address",
            "latitude",
            "longitude",
        ]
        extra_kwargs = {
            "restaurant_name": {"required": False},
            "address": {"required": False},
            "latitude": {"required": False},
            "longitude": {"required": False},
        }
