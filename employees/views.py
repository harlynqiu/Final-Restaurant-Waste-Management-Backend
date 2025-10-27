from rest_framework import viewsets, permissions
from .models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by("name")
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
