from rest_framework import serializers
from .models import Driver, DriverLocation

# -------------------------
# DriverLocation Serializer
# -------------------------
class DriverLocationSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)

    class Meta:
        model = DriverLocation
        fields = [
            'id',
            'driver_name',
            'latitude',
            'longitude',
            'timestamp',
            'is_current',
        ]

# -------------------------
# Driver Serializer
# -------------------------
class DriverSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    current_location = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = [
            "id",
            "username",
            "full_name",
            "phone_number",
            "vehicle_type",
            "plate_number",
            "status",
            "is_active",
            "date_hired",
            "current_location",
        ]

    def get_current_location(self, obj):
        """
        Returns the most recent location ping for this driver.
        We'll expose this to Flutter so you can show driver pin on map.
        """
        latest = obj.locations.filter(is_current=True).order_by("-timestamp").first()
        if not latest:
            return None
        return {
            "lat": float(latest.latitude),
            "lng": float(latest.longitude),
            "timestamp": latest.timestamp,
        }


# -------------------------
# Driver Create/Update Serializer
# (for admin-side create/edit)
# -------------------------
class DriverWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "user",
            "full_name",
            "phone_number",
            "vehicle_type",
            "plate_number",
            "status",
            "is_active",
            "date_hired",
        ]
