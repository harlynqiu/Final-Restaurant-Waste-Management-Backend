# employees/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Employee
from .serializers import EmployeeSerializer, EmployeeRegisterSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-id')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # --------------------------------------------
    # 🧾 REGISTER NEW EMPLOYEE
    # --------------------------------------------
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[permissions.AllowAny])
    def register(self, request):
        data = request.data
        username = data.get("username")
        email = data.get("email", "")
        password = data.get("password", "default123")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Prevent duplicate usernames
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Create linked User object
        user = User.objects.create_user(username=username, password=password, email=email)

        # ✅ Optional coordinates
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # ✅ Create Employee record
        employee = Employee.objects.create(
            user=user,
            name=data.get("name", username),
            email=email,
            position=data.get("position", "Staff"),
            restaurant_name=data.get("restaurant_name", ""),
            address=data.get("address", ""),
            status="active",
            latitude=latitude if latitude not in [None, ""] else None,
            longitude=longitude if longitude not in [None, ""] else None,
        )

        serializer = self.get_serializer(employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # --------------------------------------------
    # 👤 GET or PATCH /employees/me/
    # --------------------------------------------
    @action(detail=False, methods=["get", "patch"], url_path="me", permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        try:
            employee = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ GET → return employee profile
        if request.method == "GET":
            serializer = self.get_serializer(employee)
            return Response(serializer.data)

        # ✅ PATCH → allow latitude/longitude and address updates
        elif request.method == "PATCH":
            print("📍 Received PATCH /employees/me →", request.data)  # For debugging
            serializer = self.get_serializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
