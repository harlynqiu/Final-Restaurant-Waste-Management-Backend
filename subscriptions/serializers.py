from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, SubscriptionPayment
from django.utils import timezone

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'display_name', 'description', 'price', 'duration_days']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.get_name_display', read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'plan_name',
            'status',
            'auto_renew',
            'start_date',
            'end_date',
            'is_active',
        ]

    def get_is_active(self, obj):
        return obj.status == "active" and obj.end_date >= timezone.now()


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPayment
        fields = [
            'id',
            'plan_name_snapshot',
            'amount',
            'method',
            'status',
            'paid_at',
        ]
