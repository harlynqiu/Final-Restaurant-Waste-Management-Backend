# drivers/urls.py
from rest_framework import routers
from django.urls import path
from .views import DriverViewSet, DriverLocationViewSet, update_driver_location

router = routers.DefaultRouter()
router.register(r"", DriverViewSet, basename="driver")  # ✅ no extra "drivers"
router.register(r"locations", DriverLocationViewSet, basename="driverlocation")

urlpatterns = [
    path("update_location/", update_driver_location, name="update_driver_location"),  # ✅ no "drivers/" prefix
]

urlpatterns += router.urls
