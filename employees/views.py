# employees/views.py
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
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

        # 1️⃣ Create user first
        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists."}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)

        # 2️⃣ Create employee profile
        employee = Employee.objects.create(
            user=user,
            name=name,
            position=data.get("position", "Staff"),
            date_started=data.get("date_started", "2025-01-01"),
            restaurant_name=restaurant_name,
            address=address,
        )

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
