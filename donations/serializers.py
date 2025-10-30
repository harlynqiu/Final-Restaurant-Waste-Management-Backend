from rest_framework import serializers
from .models import DonationDrive, DonationParticipation


# --------------------------------------------------------
# 🌍 Donation Drive Serializer
# --------------------------------------------------------
class DonationDriveSerializer(serializers.ModelSerializer):
    is_ongoing = serializers.ReadOnlyField()

    class Meta:
        model = DonationDrive
        fields = [
            "id",
            "title",
            "description",
            "target_item",
            "start_date",
            "end_date",
            "is_active",
            "is_ongoing",
        ]


# --------------------------------------------------------
# 🤝 Donation Participation Serializer
# --------------------------------------------------------
class DonationParticipationSerializer(serializers.ModelSerializer):
    drive_title = serializers.CharField(source="drive.title", read_only=True)
    drive_description = serializers.CharField(source="drive.description", read_only=True)
    drive_target_item = serializers.CharField(source="drive.target_item", read_only=True)

    class Meta:
        model = DonationParticipation
        fields = [
            "id",
            "drive",
            "drive_title",
            "drive_description",
            "drive_target_item",
            "donated_item",
            "quantity",
            "remarks",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def validate_quantity(self, value):
        """Ensure quantity is greater than zero."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_drive(self, value):
        """Ensure selected donation drive is still active."""
        if not value.is_active:
            raise serializers.ValidationError("This donation drive is no longer active.")
        return value
