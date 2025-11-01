# main/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from drivers.views import DriverViewSet, DriverLocationViewSet

router = DefaultRouter()
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'driver-locations', DriverLocationViewSet, basename='driver_location')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Main APIs
    path('api/', include('trash_pickups.urls')),   # ✅ correct
    path('api/rewards/', include('rewards.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/donations/', include('donations.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/users/', include('users.urls')),
    path('api/drivers/', include('drivers.urls')),
]
