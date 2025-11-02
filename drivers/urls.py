# drivers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, DriverLocationViewSet

router = DefaultRouter()
router.register(r'', DriverViewSet, basename='driver')
router.register(r'locations', DriverLocationViewSet, basename='driver-location')

urlpatterns = [
    path('', include(router.urls)),
]
