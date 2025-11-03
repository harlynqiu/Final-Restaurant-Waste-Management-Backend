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

    # ✅ VALIDATE: Donation drive must be active
    def validate_donation_drive(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError("Selected donation drive is not active.")
        return value

    # ✅ VALIDATE: Weight must be between 1 and 50 kg
    def validate_weight_kg(self, value):
        """Ensure trash weight is realistic for motorcycle pickup."""
        if value is None:
            raise serializers.ValidationError("Weight is required.")
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0 kg.")
        if value > 50:
            raise serializers.ValidationError(
                "Weight exceeds the 50 kg limit. Please split your waste into smaller pickups."
            )
        return value
