from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import DonationDrive, DonationParticipation
from .serializers import DonationDriveSerializer, DonationParticipationSerializer


# ------------------------------------------
# 🌍 List all active donation drives
# ------------------------------------------
class DonationDriveViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DonationDrive.objects.all().order_by("-start_date")
    serializer_class = DonationDriveSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        today = timezone.now().date()
        return DonationDrive.objects.filter(is_active=True, end_date__gte=today)


# ------------------------------------------
# 🤝 Participate in a donation drive
# ------------------------------------------
class DonationParticipationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show only logged-in user's donation history
        return DonationParticipation.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 🟢 Admin can mark donations as completed
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def mark_completed(self, request, pk=None):
        participation = get_object_or_404(DonationParticipation, pk=pk)
        participation.mark_completed()
        return Response({"message": "Donation marked as completed and reward given."})
