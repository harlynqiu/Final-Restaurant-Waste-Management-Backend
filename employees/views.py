# employees/views.py
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Employee
from .serializers import EmployeeSerializer


# -------------------------------------------
# Public Registration View (no auth required)
# -------------------------------------------
class EmployeeRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmployeeSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        restaurant_name = data.get("restaurant_name", "")
        address = data.get("address", "")
        name = data.get("name", username)  # fallback if not provided

        # 1️⃣ Validate required fields
        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if email and Employee.objects.filter(email=email).exists():
            return Response(
                {"detail": "An account with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2️⃣ Try creating the user and employee safely
        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            employee = Employee.objects.create(
                user=user,
                name=name,
                position=data.get("position", "Staff"),
                date_started=data.get("date_started", "2025-01-01"),
                restaurant_name=restaurant_name,
                address=address,
                email=email,
            )

            serializer = EmployeeSerializer(employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # 🧩 Handles duplicate email or DB integrity errors
            if "email" in str(e):
                return Response(
                    {"error": "An account with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": "Database integrity error."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# -------------------------------------------
# Employee ViewSet (for authenticated users)
# -------------------------------------------
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Return details of the logged-in employee"""
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
