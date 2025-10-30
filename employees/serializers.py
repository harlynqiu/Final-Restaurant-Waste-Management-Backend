# employees/serializers.py
from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

    # 🧩 Custom email validation (prevents duplicate registration)
    def validate_email(self, value):
        if value and Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value
