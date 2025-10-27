from rest_framework import serializers
from .models import RewardPoint, RewardTransaction, Voucher, RewardRedemption


class RewardPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPoint
        fields = ['points']


class RewardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardTransaction
        fields = ['points', 'description', 'transaction_type', 'created_at']


class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ['id', 'name', 'description', 'points_required', 'discount_value']


class RewardRedemptionSerializer(serializers.ModelSerializer):
    voucher = VoucherSerializer(read_only=True)

    class Meta:
        model = RewardRedemption
        fields = ['id', 'voucher', 'redeemed_at', 'is_used']
