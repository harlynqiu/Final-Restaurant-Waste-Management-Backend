# trash_pickups/serializers.py
from rest_framework import serializers
from .models import TrashPickup

class TrashPickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrashPickup
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status']
