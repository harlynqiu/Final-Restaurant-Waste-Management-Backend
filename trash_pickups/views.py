# trash_pickups/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from .models import TrashPickup
from .serializers import TrashPickupSerializer


class TrashPickupViewSet(viewsets.ModelViewSet):
    serializer_class = TrashPickupSerializer
    permission_classes = [permissions.IsAuthenticated]

    # -----------------------------------------------------------
    # ✅ GET QUERYSET — Auto-detect user type
    # -----------------------------------------------------------
    def get_queryset(self):
        user = self.request.user

        # ✅ Driver sees only assigned tasks
        if hasattr(user, "driver_profile"):
            return TrashPickup.objects.filter(
                driver=user.driver_profile
            ).order_by("-created_at")

        # ✅ Employee sees owner’s tasks
        if hasattr(user, "employee_profile"):
            owner_user = user.employee_profile.owner.user
            return TrashPickup.objects.filter(
                user=owner_user
            ).order_by("-created_at")

        # ✅ Owner sees their own tasks
        return TrashPickup.objects.filter(user=user).order_by("-created_at")

    # -----------------------------------------------------------
    # ✅ CREATE PICKUP — owner or employee submit under owner
    # -----------------------------------------------------------
    def perform_create(self, serializer):
        user = self.request.user

        # ✅ If EMPLOYEE submits, assign to owner
        if hasattr(user, "employee_profile"):
            owner = user.employee_profile.owner.user
            serializer.save(user=owner, status="pending")
            return

        # ✅ If OWNER submits
        serializer.save(user=user, status="pending")

    # -----------------------------------------------------------
    # ✅ DRIVER: List Available Pickups
    # -----------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="available")
    def available_pickups(self, request):

        if not hasattr(request.user, "driver_profile"):
            return Response({"detail": "Drivers only."}, status=403)

        pickups = TrashPickup.objects.filter(
            status="pending",
            driver__isnull=True
        ).order_by("-created_at")

        return Response(TrashPickupSerializer(pickups, many=True).data)

    # -----------------------------------------------------------
    # ✅ ACCEPT PICKUP (Driver)
    # -----------------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="accept")
    def accept_pickup(self, request, pk=None):

        if not hasattr(request.user, "driver_profile"):
            return Response({"detail": "Drivers only."}, status=403)

        pickup = self.get_object()

        if pickup.driver is not None:
            return Response({"detail": "Already assigned."}, status=400)

        if pickup.status != "pending":
            return Response({"detail": "Cannot accept this pickup."}, status=400)

        pickup.driver = request.user.driver_profile
        pickup.status = "accepted"
        pickup.save()

        return Response(TrashPickupSerializer(pickup).data)

    # -----------------------------------------------------------
    # ✅ START PICKUP (Driver)
    # -----------------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="start")
    def start_pickup(self, request, pk=None):

        if not hasattr(request.user, "driver_profile"):
            return Response({"detail": "Drivers only."}, status=403)

        pickup = self.get_object()
        pickup.status = "in_progress"
        pickup.save()

        return Response(TrashPickupSerializer(pickup).data)

    # -----------------------------------------------------------
    # ✅ COMPLETE PICKUP (Driver)
    # -----------------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="complete")
    def complete_pickup(self, request, pk=None):

        if not hasattr(request.user, "driver_profile"):
            return Response({"detail": "Drivers only."}, status=403)

        pickup = self.get_object()
        pickup.status = "completed"
        pickup.save()

        return Response(TrashPickupSerializer(pickup).data)

    # -----------------------------------------------------------
    # ✅ CANCEL PICKUP (Owner)
    # -----------------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel_pickup(self, request, pk=None):

        pickup = self.get_object()

        if pickup.status == "completed":
            return Response({"detail": "Completed pickups cannot be cancelled."}, status=400)

        pickup.status = "cancelled"
        pickup.save()
        return Response({"status": "cancelled"})
