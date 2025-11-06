# trash_pickups/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import TrashPickup
from .serializers import TrashPickupSerializer
from drivers.models import Driver
from donations.models import DonationDrive

class TrashPickupViewSet(viewsets.ModelViewSet):
    serializer_class = TrashPickupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "driver_profile"):
            return TrashPickup.objects.filter(
                driver=user.driver_profile
            ).order_by("-created_at")

        return TrashPickup.objects.filter(
            user=user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user

        donation = DonationDrive.objects.filter(
            waste_type=serializer.validated_data["waste_type"]
        ).first()

        serializer.save(
            user=user,
            donation_drive=donation
        )

    @action(detail=False, methods=["get"], url_path="available")
    def available(self, request):
        # Only show pickups without assigned driver
        pickups = TrashPickup.objects.filter(
            status="pending",
            driver__isnull=True
        )
        return Response(TrashPickupSerializer(pickups, many=True).data)

    @action(detail=True, methods=["patch"], url_path="accept")
    def accept(self, request, pk=None):
        user = request.user

        if not hasattr(user, "driver_profile"):
            return Response({"detail": "Only drivers can accept pickups."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            pickup = TrashPickup.objects.get(pk=pk)
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."},
                            status=status.HTTP_404_NOT_FOUND)

        if pickup.driver is not None:
            return Response({"detail": "This pickup is already assigned."},
                            status=status.HTTP_400_BAD_REQUEST)

        pickup.driver = user.driver_profile
        pickup.status = "accepted"
        pickup.save()

        return Response({"detail": "Pickup accepted successfully."})

    @action(detail=True, methods=["patch"], url_path="start")
    def start(self, request, pk=None):
        pickup = TrashPickup.objects.get(pk=pk)

        if pickup.status != "accepted":
            return Response({"detail": "Pickup must be accepted first."},
                            status=status.HTTP_400_BAD_REQUEST)

        pickup.status = "in_progress"
        pickup.save()

        return Response({"detail": "Pickup marked as In Progress."})

    @action(detail=True, methods=["patch"], url_path="complete")
    def complete(self, request, pk=None):
        try:
            pickup = TrashPickup.objects.get(pk=pk)
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."},
                            status=status.HTTP_404_NOT_FOUND)

        if pickup.status not in ["accepted", "in_progress"]:
            return Response({"detail": "Cannot complete this pickup."},
                            status=status.HTTP_400_BAD_REQUEST)

        pickup.status = "completed"
        pickup.save()

        try:
            from rewards.models import RewardPoint, RewardTransaction

            points = int(pickup.weight_kg)
            reward, _ = RewardPoint.objects.get_or_create(user=pickup.user)
            reward.add_points(points)
            
            RewardTransaction.objects.create(
                user=pickup.user,
                pickup=pickup,
                points=points,
                description=f"Completed {pickup.weight_kg}kg pickup"
            )

        except Exception as e:
            print("Reward error:", e)

        return Response({"detail": "Pickup completed successfully."})