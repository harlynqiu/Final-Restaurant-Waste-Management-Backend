from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import SubscriptionPlan, UserSubscription, SubscriptionPayment
from .serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    SubscriptionPaymentSerializer,
)

# -----------------------------------------
# 1. List active plans (Basic, Premium...)
# -----------------------------------------
class SubscriptionPlanListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True).order_by('price')


# -----------------------------------------
# 2. Get my current subscription (latest)
# -----------------------------------------
class MySubscriptionView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def get_object(self):
        sub = (
            UserSubscription.objects.filter(user=self.request.user)
            .order_by('-start_date')
            .first()
        )
        if sub:
            sub.mark_expired_if_needed()
        return sub


# -----------------------------------------
# 3. Subscribe / Renew a plan
# -----------------------------------------
class SubscribeToPlanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Expected body:
        {
          "plan_id": 2,
          "method": "gcash",
          "voucher_code": "SAVE10"  # optional
        }
        """
        plan_id = request.data.get("plan_id")
        method = request.data.get("method", "gcash")
        voucher_code = request.data.get("voucher_code", None)

        if not plan_id:
            return Response({"error": "plan_id is required"}, status=400)

        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        discount = 0
        applied_voucher = None

        # 🧾 Optional: Check voucher validity
        if voucher_code:
            from rewards.models import Voucher
            try:
                voucher = Voucher.objects.get(code=voucher_code, is_active=True)
                discount = float(voucher.discount_amount)
                applied_voucher = voucher
            except Voucher.DoesNotExist:
                return Response({"error": "Invalid or expired voucher."}, status=400)

        # 🧮 Compute final price
        total_amount = float(plan.price) - discount
        if total_amount < 0:
            total_amount = 0

        # ✅ Create subscription
        new_sub = UserSubscription.create_new_subscription(request.user, plan)

        # 💸 Log payment
        SubscriptionPayment.objects.create(
            user=request.user,
            subscription=new_sub,
            plan_name_snapshot=plan.get_name_display(),
            amount=total_amount,
            method=method,
            status="paid",
        )

        # 🔓 Mark voucher as used if needed
        if applied_voucher:
            applied_voucher.is_active = False
            applied_voucher.save()

        return Response(
            {
                "message": "Subscription activated successfully!",
                "subscription": {
                    "plan_name": plan.get_name_display(),
                    "plan_price": plan.price,
                    "discount_applied": discount,
                    "final_amount": total_amount,
                    "end_date": new_sub.end_date,
                    "voucher_code": voucher_code,
                },
            },
            status=201,
        )


# -----------------------------------------
# 4. Cancel auto-renew
# -----------------------------------------
class CancelSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sub = (
            UserSubscription.objects.filter(user=request.user, status="active")
            .order_by('-start_date')
            .first()
        )

        if not sub:
            return Response(
                {"error": "No active subscription to cancel"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sub.mark_cancelled()

        return Response(
            {"message": "Auto-renew disabled. Subscription will not renew."},
            status=status.HTTP_200_OK,
        )


# -----------------------------------------
# 5. My payment history
# -----------------------------------------
class MyPaymentsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionPaymentSerializer

    def get_queryset(self):
        return SubscriptionPayment.objects.filter(user=self.request.user).order_by('-paid_at')
