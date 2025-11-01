# trash_pickups/serializers.py
from rest_framework import serializers
from .models import TrashPickup
from donations.models import DonationDrive
from drivers.models import Driver


class TrashPickupSerializer(serializers.ModelSerializer):
    donation_drive_title = serializers.ReadOnlyField(source='donation_drive.title')
    driver_name = serializers.ReadOnlyField(source='driver.full_name', default=None)

    donation_drive = serializers.PrimaryKeyRelatedField(
        queryset=DonationDrive.objects.all(),
        required=False,
        allow_null=True
    )
    driver = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = TrashPickup
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate_donation_drive(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError("Selected donation drive is not active.")
        return value
