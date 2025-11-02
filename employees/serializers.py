# employees/serializers.py
from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User


class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id", "username", "email", "name", "position",
            "restaurant_name", "address", "status",
            "latitude", "longitude", "created_at",
        ]


class EmployeeRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = Employee
        fields = [
            "username", "password", "email", "name", "position",
            "restaurant_name", "address", "latitude", "longitude",
        ]

    def create(self, validated_data):
        from django.contrib.auth.models import User
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        email = validated_data.pop("email", "")

        user = User.objects.create_user(username=username, password=password, email=email)
        employee = Employee.objects.create(user=user, **validated_data)
        return employee
