from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RewardPoint, RewardTransaction, RewardRedemption
from .serializers import (
    RewardPointSerializer,
    RewardTransactionSerializer,
    VoucherSerializer,
    RewardRedemptionSerializer
)
from rewards.models import Voucher
from django.db import models
#from django.contrib.auth.models import User

# 🟢 View Points
class RewardPointView(generics.RetrieveAPIView):
    serializer_class = RewardPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        reward, _ = RewardPoint.objects.get_or_create(user=self.request.user)
        return reward


# 🟡 View Transactions
class RewardTransactionListView(generics.ListAPIView):
    serializer_class = RewardTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RewardTransaction.objects.filter(user=self.request.user).order_by('-created_at')



# 🎁 View Available Vouchers
class VoucherListView(generics.ListAPIView):
    serializer_class = VoucherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Voucher.objects.filter(is_active=True).order_by('points_required')


# 🎟️ Redeem a Voucher
class RedeemVoucherView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        voucher_id = request.data.get("voucher_id")
        voucher = Voucher.objects.filter(id=voucher_id, is_active=True).first()

        if not voucher:
            return Response(
                {"success": False, "message": "Invalid voucher."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reward, _ = RewardPoint.objects.get_or_create(user=request.user)
        if reward.points < voucher.points_required:
            return Response(
                {"success": False, "message": "Not enough points."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Deduct points
        reward.add_points(-voucher.points_required)

        # ✅ Create redemption (use item_name and points_spent, not voucher FK)
        RewardRedemption.objects.create(
            user=request.user,
            item_name=voucher.code,
            points_spent=voucher.points_required,
            status="completed",
        )

        # ✅ Log the transaction
        RewardTransaction.objects.create(
            user=request.user,
            points=-voucher.points_required,
            description=f"Redeemed {voucher.code}",
        )

        return Response(
            {
                "success": True,
                "message": f"Voucher '{voucher.code}' redeemed successfully!",
            },
            status=status.HTTP_200_OK,
        )

# 🧾 View Redemption History
class RewardRedemptionListView(generics.ListAPIView):
    serializer_class = RewardRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RewardRedemption.objects.filter(user=self.request.user).order_by('-created_at')


class MyRewardsListView(generics.ListAPIView):
    serializer_class = RewardRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RewardRedemption.objects.filter(user=self.request.user).order_by('-created_at')

