from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, DriverLocationViewSet
router = DefaultRouter()
router.register(r'drivers', DriverViewSet)
router.register(r'locations', DriverLocationViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
