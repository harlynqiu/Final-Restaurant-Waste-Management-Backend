from rest_framework import viewsets, permissions
from .models import TrashPickup
from .serializers import TrashPickupSerializer
from rewards.models import RewardPoint, RewardTransaction

class TrashPickupViewSet(viewsets.ModelViewSet):
    queryset = TrashPickup.objects.all().order_by('-created_at')
    serializer_class = TrashPickupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrashPickup.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        pickup = serializer.save()

        # 🟢 Reward logic: Add points when completed
        if pickup.status == "completed":
            reward, _ = RewardPoint.objects.get_or_create(user=pickup.user)
            reward.add_points(10)  # e.g. 10 pts per completed pickup

            RewardTransaction.objects.create(
                user=pickup.user,
                pickup=pickup,
                points=10,
                description="Completed a trash pickup"
            )
