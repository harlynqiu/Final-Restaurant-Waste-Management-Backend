# trash_pickups/serializers.py
from rest_framework import serializers
from .models import TrashPickup
from donations.models import DonationDrive
from drivers.models import Driver


class TrashPickupSerializer(serializers.ModelSerializer):
    donation_drive_title = serializers.ReadOnlyField(source='donation_drive.title')
    driver_name = serializers.ReadOnlyField(source='driver.full_name', default=None)

    # ✅ Allow only donation drive to be submitted
    donation_drive = serializers.PrimaryKeyRelatedField(
        queryset=DonationDrive.objects.all(),
        required=False,
        allow_null=True
    )

    # ✅ Driver is read-only and returns only driver ID, NOT Driver object
    driver = serializers.SerializerMethodField(read_only=True)

    def get_driver(self, obj):
        return obj.driver.id if obj.driver else None

    class Meta:
        model = TrashPickup
        fields = '__all__'
        read_only_fields = ["id", "user", "created_at", "status"]

    def validate_donation_drive(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError("Selected donation drive is not active.")
        return value

    def validate_weight_kg(self, value):
        if value is None:
            raise serializers.ValidationError("Weight is required.")
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0 kg.")
        if value > 50:
            raise serializers.ValidationError("Weight exceeds 50 kg.")
        return value
