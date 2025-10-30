from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import TrashPickup
from .serializers import TrashPickupSerializer
from rewards.models import RewardPoint, RewardTransaction
from donations.models import DonationDrive


class TrashPickupViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for Trash Pickups.
    Automatically associates the logged-in user and optional donation drive.
    Includes reward logic for completed pickups.
    """
    serializer_class = TrashPickupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return pickups belonging only to the logged-in user."""
        return TrashPickup.objects.filter(user=self.request.user).order_by('-created_at')

    # --------------------------------------------------------
    # 🟢 CREATE PICKUP
    # --------------------------------------------------------
    def perform_create(self, serializer):
        """When creating a pickup, include the user and donation drive if provided."""
        donation_drive_id = self.request.data.get("donation_drive")
        donation_drive = None

        if donation_drive_id:
            try:
                donation_drive = DonationDrive.objects.get(id=donation_drive_id, is_active=True)
            except DonationDrive.DoesNotExist:
                return Response(
                    {"error": f"Donation Drive with id {donation_drive_id} not found or inactive."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer.save(user=self.request.user, donation_drive=donation_drive)

    # --------------------------------------------------------
    # 🟢 UPDATE PICKUP (REWARD LOGIC)
    # --------------------------------------------------------
    def perform_update(self, serializer):
        """When pickup is marked completed, reward points are given."""
        pickup = serializer.save()

        if pickup.status == "completed":
            # 🏆 Add points to user's total
            reward, _ = RewardPoint.objects.get_or_create(user=pickup.user)
            reward.add_points(10)  # Example: 10 pts per completed pickup

            # 💰 Record transaction
            RewardTransaction.objects.create(
                user=pickup.user,
                pickup=pickup,
                points=10,
                description=f"Completed pickup ({pickup.waste_type})"
            )

    # --------------------------------------------------------
    # 🟢 OVERRIDE CREATE TO HANDLE INVALID DRIVE SAFELY
    # --------------------------------------------------------
    def create(self, request, *args, **kwargs):
        """
        Override create() to safely handle invalid donation drives
        and ensure proper HTTP responses.
        """
        donation_drive_id = request.data.get("donation_drive")

        # Validate donation drive first
        if donation_drive_id:
            try:
                DonationDrive.objects.get(id=donation_drive_id)
            except DonationDrive.DoesNotExist:
                return Response(
                    {"donation_drive": [f"Invalid pk '{donation_drive_id}' - object does not exist."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return super().create(request, *args, **kwargs)
