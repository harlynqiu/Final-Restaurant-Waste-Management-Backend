# main/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from drivers.views import DriverViewSet, DriverLocationViewSet
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import LoginView

# DRF Router (Driver-related endpoints)

router = DefaultRouter()
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'driver-locations', DriverLocationViewSet, basename='driver_location')


#  GLOBAL URLS

urlpatterns = [
    path('admin/', admin.site.urls),

    #  JWT Authentication

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('accounts.urls')),  #  /api/accounts/me/

    #  App Routers 

    path('api/rewards/', include('rewards.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/donations/', include('donations.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/users/', include('users.urls')),

    path('api/', include(router.urls)),
    path('api/', include('trash_pickups.urls')),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
