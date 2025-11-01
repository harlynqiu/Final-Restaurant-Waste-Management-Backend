from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Driver, DriverLocation
from .serializers import (
    DriverSerializer,
    DriverWriteSerializer,
    DriverLocationSerializer,
)

# -------------------------------------------------
# 👤 Driver API
# -------------------------------------------------
class DriverViewSet(viewsets.ModelViewSet):
    """
    /api/drivers/           GET list of drivers (admin/dispatcher use)
    /api/drivers/<id>/      GET single driver
    /api/drivers/<id>/      PATCH driver status (ex: mark as on_pickup)
    """
    queryset = Driver.objects.filter(is_active=True).select_related("user")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # Read vs Write serializers
        if self.action in ["create", "update", "partial_update"]:
            return DriverWriteSerializer
        return DriverSerializer

    def perform_create(self, serializer):
        # Admin creates driver and links to existing User account
        serializer.save()

    # -------------------------------------------------
    # GET /api/drivers/me/
    # Driver checks their own profile
    # -------------------------------------------------
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return Response(
                {"detail": "You are not registered as a driver."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = DriverSerializer(driver).data
        return Response(data, status=status.HTTP_200_OK)

    # -------------------------------------------------
    # PATCH /api/drivers/me/status/
    # driver can update their own availability
    # -------------------------------------------------
    @action(detail=False, methods=["patch"], url_path="me/status")
    def update_my_status(self, request):
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return Response(
                {"detail": "You are not registered as a driver."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")
        if new_status not in ["available", "on_pickup", "inactive"]:
            return Response(
                {"detail": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        driver.status = new_status
        driver.save()
        return Response(
            {"detail": "Status updated.", "status": driver.status},
            status=status.HTTP_200_OK,
        )


# -------------------------------------------------
# 📍 Driver Location API
# -------------------------------------------------
class DriverLocationViewSet(viewsets.ModelViewSet):
    """
    /api/driver-locations/          GET (admin/dispatcher: see all)
    /api/driver-locations/          POST (driver sends a ping)
    /api/driver-locations/<id>/     GET specific ping
    """
    queryset = DriverLocation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DriverLocationSerializer

    def perform_create(self, serializer):
        """
        When driver sends a new location ping:
        - Find driver by request.user
        - Mark old pings as not current
        - Save the new ping as current
        """
        try:
            driver = Driver.objects.get(user=self.request.user)
        except Driver.DoesNotExist:
            raise PermissionError("User is not registered as a driver.")

        # Mark all old current pings as inactive
        DriverLocation.objects.filter(driver=driver, is_current=True).update(is_current=False)

        serializer.save(driver=driver, is_current=True)
