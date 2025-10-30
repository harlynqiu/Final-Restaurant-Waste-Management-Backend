from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import TrashPickup
from .serializers import TrashPickupSerializer
from rewards.models import RewardPoint, RewardTransaction


class TrashPickupViewSet(viewsets.ModelViewSet):
    serializer_class = TrashPickupSerializer
    permission_classes = [permissions.IsAuthenticated]

    # -------------------------------------
    # Return only the logged-in user's pickups
    # -------------------------------------
    def get_queryset(self):
        return TrashPickup.objects.filter(user=self.request.user).order_by('-created_at')

    # -------------------------------------
    # Create a new pickup (auto-assign user)
    # -------------------------------------
    def perform_create(self, serializer):
        scheduled_date = self.request.data.get('scheduled_date')

        # Optional validation — prevent past scheduling
        if scheduled_date:
            try:
                parsed_date = timezone.datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
                if parsed_date < timezone.now():
                    raise ValueError("Scheduled date cannot be in the past.")
            except Exception:
                raise ValueError("Invalid scheduled_date format. Use ISO 8601.")

        serializer.save(user=self.request.user)

    # -------------------------------------
    # Update (for status changes, etc.)
    # -------------------------------------
    def update(self, request, *args, **kwargs):
        scheduled_date = request.data.get('scheduled_date')

        # ✅ Validate scheduled date if present
        if scheduled_date:
            try:
                parsed_date = timezone.datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
                if parsed_date < timezone.now():
                    return Response(
                        {"error": "Scheduled date cannot be in the past."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception:
                return Response(
                    {"error": "Invalid scheduled_date format. Use ISO 8601."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ✅ Save update (e.g. cancelled or completed)
        pickup = self.get_object()
        response = super().update(request, *args, **kwargs)

        # 🟢 Reward logic for completion
        if pickup.status == "completed":
            reward, _ = RewardPoint.objects.get_or_create(user=pickup.user)
            reward.add_points(10)
            RewardTransaction.objects.create(
                user=pickup.user,
                pickup=pickup,
                points=10,
                description="Completed a trash pickup"
            )

        return response

    # -------------------------------------
    # PATCH: Quick status updates (e.g. cancel)
    # -------------------------------------
    def partial_update(self, request, *args, **kwargs):
        pickup = self.get_object()
        status_value = request.data.get("status")

        # ✅ Handle cancellation immediately
        if status_value and status_value.lower() == "cancelled":
            pickup.status = "cancelled"
            pickup.save()
            return Response(
                {"message": "Pickup cancelled successfully", "id": pickup.id},
                status=status.HTTP_200_OK
            )

        return super().partial_update(request, *args, **kwargs)
