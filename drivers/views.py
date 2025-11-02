# drivers/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
    queryset = Driver.objects.filter(is_active=True).select_related("user")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return DriverWriteSerializer
        return DriverSerializer

    def perform_create(self, serializer):
        serializer.save()

    # ✅ /api/drivers/me/
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        if not driver:
            return Response({"detail": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DriverSerializer(driver).data)

    # ✅ /api/drivers/me/status/
    @action(detail=False, methods=['patch'], url_path='me/status')
    def update_my_status(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        if not driver:
            return Response({"detail": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ["available", "on_pickup", "inactive"]:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        driver.status = new_status
        driver.save()
        return Response({"detail": "Status updated.", "status": driver.status}, status=status.HTTP_200_OK)


# -------------------------------------------------
# 📍 Driver Location API
# -------------------------------------------------
class DriverLocationViewSet(viewsets.ModelViewSet):
    queryset = DriverLocation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DriverLocationSerializer

    def perform_create(self, serializer):
        try:
            driver = Driver.objects.get(user=self.request.user)
        except Driver.DoesNotExist:
            return Response({"detail": "You are not registered as a driver."},
                            status=status.HTTP_403_FORBIDDEN)

        DriverLocation.objects.filter(driver=driver, is_current=True).update(is_current=False)
        serializer.save(driver=driver, is_current=True)


# -------------------------------------------------
# 🛰️ Update Driver's Current Location (for live GPS)
# -------------------------------------------------
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_driver_location(request):
    user = request.user
    try:
        driver = Driver.objects.get(user=user)
    except Driver.DoesNotExist:
        return Response({"detail": "You are not registered as a driver."},
                        status=status.HTTP_404_NOT_FOUND)

    lat = request.data.get("latitude")
    lng = request.data.get("longitude")

    if lat is None or lng is None:
        return Response({"detail": "Latitude and longitude are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    DriverLocation.objects.filter(driver=driver, is_current=True).update(is_current=False)

    DriverLocation.objects.create(
        driver=driver,
        latitude=lat,
        longitude=lng,
        is_current=True
    )

    # Optionally store lat/lng directly on the driver model too
    driver.latitude = lat
    driver.longitude = lng
    driver.save(update_fields=["latitude", "longitude"])

    return Response({"message": "Driver location updated successfully."},
                    status=status.HTTP_200_OK)
