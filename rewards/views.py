from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from .models import RewardPoint, RewardTransaction, RewardRedemption, Voucher
from .serializers import (
    RewardPointSerializer,
    RewardTransactionSerializer,
    VoucherSerializer,
    RewardRedemptionSerializer,
)


# 🟢 View Total Points
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

        # 🔴 Invalid or inactive voucher
        if not voucher:
            return Response(
                {"success": False, "message": "Invalid voucher."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🧮 Check user's reward points
        reward, _ = RewardPoint.objects.get_or_create(user=request.user)
        if reward.points < voucher.points_required:
            return Response(
                {"success": False, "message": "Not enough points."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Deduct points
        reward.add_points(-voucher.points_required)

        # ✅ Create redemption record (linked to voucher)
        redemption = RewardRedemption.objects.create(
            user=request.user,
            voucher=voucher,                      # ✅ link to Voucher
            item_name=voucher.name,               # readable name
            points_spent=voucher.points_required,
            status="completed",
            is_used=False,
        )

        # ✅ Log the transaction
        RewardTransaction.objects.create(
            user=request.user,
            points=-voucher.points_required,
            description=f"Redeemed {voucher.name}",
        )

        # ✅ Return full voucher details
        serializer = RewardRedemptionSerializer(redemption, context={"request": request})
        return Response(
            {
                "success": True,
                "message": f"Voucher '{voucher.name}' redeemed successfully!",
                "redemption": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# 🧾 View Redemption History (for admins or user)
class RewardRedemptionListView(generics.ListAPIView):
    serializer_class = RewardRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RewardRedemption.objects.filter(user=self.request.user).order_by('-created_at')


# 🎯 "My Rewards" — user-specific view for dashboard
class MyRewardsListView(generics.ListAPIView):
    serializer_class = RewardRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            RewardRedemption.objects.filter(user=self.request.user)
            .select_related("voucher")  # 🧩 Prefetch voucher to optimize DB calls
            .order_by('-created_at')
        )
