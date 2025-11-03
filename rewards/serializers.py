from rest_framework import serializers
from .models import RewardPoint, RewardTransaction, Voucher, RewardRedemption


class RewardPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPoint
        fields = ['points']


class RewardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardTransaction
        fields = ['points', 'description', 'created_at']


class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = [
            "id",
            "code",
            "name",
            "description",
            "discount_amount",
            "points_required",
            "image",
            "is_active",
            "created_at",
            "expires_at",
        ]


class RewardRedemptionSerializer(serializers.ModelSerializer):
    voucher = VoucherSerializer(read_only=True)

    class Meta:
        model = RewardRedemption
        fields = ['id', 'voucher', 'created_at', 'is_used']
