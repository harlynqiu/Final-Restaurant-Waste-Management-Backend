# main/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from drivers.views import DriverViewSet, DriverLocationViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'driver-locations', DriverLocationViewSet, basename='driver_location')

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ✅ MUST INCLUDE ROUTER — THIS FIXES THE 404 ON ACCEPT/START/COMPLETE
    path('api/', include(router.urls)),

    # ✅ App routers
    path('api/', include('trash_pickups.urls')),
    path('api/rewards/', include('rewards.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/donations/', include('donations.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/users/', include('users.urls')),
    path("api/accounts/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
