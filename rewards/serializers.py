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
    image = serializers.SerializerMethodField()

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

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class RewardRedemptionSerializer(serializers.ModelSerializer):
    voucher = VoucherSerializer(read_only=True)

    class Meta:
        model = RewardRedemption
        fields = [
            'id',
            'voucher',
            'item_name',
            'points_spent',
            'status',
            'is_used',
            'created_at',
        ]
