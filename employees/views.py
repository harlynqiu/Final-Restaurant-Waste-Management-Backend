from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Employee
from .serializers import EmployeeSerializer, EmployeeRegisterSerializer
from accounts.models import OwnerProfile


class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # ✅ Only employees belonging to this owner 
        try:
            owner = self.request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Employee.objects.none()

        return Employee.objects.filter(owner=owner).order_by("-id")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return EmployeeRegisterSerializer
        return EmployeeSerializer

    def perform_create(self, serializer):
        owner = self.request.user.owner_profile

        serializer.save(
            owner=owner,
            restaurant_name=owner.restaurant_name,
            address=owner.address
        )

    def perform_update(self, serializer):
        owner = self.request.user.owner_profile
        serializer.save(
            restaurant_name=owner.restaurant_name,
            address=owner.address,
        )



    # ✅ FIXED: Return ALL employees under this owner
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        try:
            owner = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response({"detail": "Not an owner"}, status=404)

        employees = Employee.objects.filter(owner=owner)

        if not employees.exists():
            return Response({"detail": "No employees"}, status=404)

        # ✅ Return ONLY THE FIRST EMPLOYEE
        emp = employees.first()

        return Response(EmployeeSerializer(emp).data)
