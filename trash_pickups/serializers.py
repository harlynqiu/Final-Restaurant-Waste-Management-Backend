# trash_pickups/serializers.py
from rest_framework import serializers
from .models import TrashPickup
from donations.models import DonationDrive


class TrashPickupSerializer(serializers.ModelSerializer):
    # 🟢 Include donation drive title for display (read-only)
    donation_drive_title = serializers.ReadOnlyField(source='donation_drive.title')

    # 🟢 Handle donation drive relation properly
    donation_drive = serializers.PrimaryKeyRelatedField(
        queryset=DonationDrive.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = TrashPickup
        fields = '__all__'  # includes donation_drive & donation_drive_title
        read_only_fields = ['user', 'created_at', 'status']

    def validate_donation_drive(self, value):
        """Ensure the donation drive exists and is active."""
        if value and not value.is_active:
            raise serializers.ValidationError("Selected donation drive is not active.")
        return value
