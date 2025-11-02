# trash_pickups/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import TrashPickup
from .serializers import TrashPickupSerializer


class TrashPickupViewSet(viewsets.ModelViewSet):
    serializer_class = TrashPickupSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ------------------------------------------------
    # 🔍 GET QUERYSET (Driver or Regular User)
    # ------------------------------------------------
    def get_queryset(self):
        user = self.request.user

        # Drivers see only their assigned pickups
        if hasattr(user, "driver_profile"):
            return TrashPickup.objects.filter(driver=user.driver_profile).order_by("-created_at")

        # Regular users see their own pickups
        return TrashPickup.objects.filter(user=user).order_by("-created_at")

    # ------------------------------------------------
    # 🧱 CREATE PICKUP (auto-fill missing address or coords)
    # ------------------------------------------------
    def perform_create(self, serializer):
        user = self.request.user
        data = self.request.data

        latitude = data.get("latitude")
        longitude = data.get("longitude")
        pickup_address = data.get("pickup_address")

        # ✅ If user has employee_profile, copy location info from there
        if hasattr(user, "employee_profile"):
            employee = user.employee_profile
            if not pickup_address:
                pickup_address = getattr(employee, "address", None)
            if not latitude or not longitude:
                latitude = getattr(employee, "latitude", None)
                longitude = getattr(employee, "longitude", None)

        # ✅ Default fallback (avoid Flutter null geocoding crash)
        if not pickup_address:
            pickup_address = "Davao City"
        if not latitude or not longitude:
            latitude = 7.0731
            longitude = 125.6128  # Center of Davao City

        serializer.save(
            user=user,
            pickup_address=pickup_address,
            latitude=latitude,
            longitude=longitude,
        )

    # ------------------------------------------------
    # 🔐 GET OBJECT (allow drivers to view unassigned pickups)
    # ------------------------------------------------
    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if hasattr(user, "driver_profile"):
            # Drivers can access any unassigned or their own pickup
            if obj.driver is None or obj.driver == user.driver_profile:
                return obj
        elif obj.user == user:
            return obj

        # Deny access otherwise
        self.permission_denied(self.request, message="You are not allowed to access this pickup.")

    # ------------------------------------------------
    # 🚗 AVAILABLE PICKUPS (for drivers)
    # ------------------------------------------------
    @action(detail=False, methods=["get"], url_path="available")
    def available_pickups(self, request):
        """Return all unassigned pending pickups."""
        pickups = TrashPickup.objects.filter(driver__isnull=True, status="pending")
        serializer = self.get_serializer(pickups, many=True)
        return Response(serializer.data)

    # ------------------------------------------------
    # 🚚 ACCEPT PICKUP
    # ------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="accept")
    def accept_pickup(self, request, pk=None):
        """Driver accepts a pending pickup."""
        user = request.user
        if not hasattr(user, "driver_profile"):
            return Response(
                {"detail": "You are not registered as a driver."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            pickup = TrashPickup.objects.get(pk=pk)
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."}, status=status.HTTP_404_NOT_FOUND)

        if pickup.driver:
            return Response(
                {"detail": "This pickup has already been accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Auto-fix missing coordinates or address for old pickups
        if not pickup.latitude or not pickup.longitude or not pickup.pickup_address:
            pickup.latitude = pickup.latitude or 7.0731
            pickup.longitude = pickup.longitude or 125.6128
            pickup.pickup_address = pickup.pickup_address or "Davao City"

        pickup.driver = user.driver_profile
        pickup.status = "in_progress"
        pickup.save()

        return Response(
            {"success": True, "message": f"Pickup #{pickup.id} accepted successfully."},
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------
    # ✅ COMPLETE PICKUP
    # ------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="complete")
    def complete_pickup(self, request, pk=None):
        """Driver marks a pickup as completed."""
        try:
            pickup = TrashPickup.objects.get(pk=pk)
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."}, status=status.HTTP_404_NOT_FOUND)

        if pickup.status not in ["in_progress", "accepted"]:
            return Response(
                {"detail": "This pickup cannot be completed yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pickup.status = "completed"
        pickup.save()

        return Response(
            {"success": True, "message": f"Pickup #{pickup.id} marked completed."},
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------
    # ❌ CANCEL PICKUP
    # ------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel_pickup(self, request, pk=None):
        try:
            pickup = self.get_object()
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found"}, status=status.HTTP_404_NOT_FOUND)

        pickup.status = "cancelled"
        pickup.save(update_fields=["status"])
        return Response({"message": "Pickup cancelled successfully"}, status=status.HTTP_200_OK)
