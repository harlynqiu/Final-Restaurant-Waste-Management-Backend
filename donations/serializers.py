from rest_framework import serializers
from .models import DonationDrive, DonationParticipation


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


class DonationParticipationSerializer(serializers.ModelSerializer):
    drive_title = serializers.CharField(source="drive.title", read_only=True)

    class Meta:
        model = DonationParticipation
        fields = [
            "id",
            "drive",
            "drive_title",
            "donated_item",
            "quantity",
            "remarks",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]
