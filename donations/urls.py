from rest_framework.routers import DefaultRouter
from .views import DonationDriveViewSet, DonationParticipationViewSet

router = DefaultRouter()
router.register(r"drives", DonationDriveViewSet, basename="donation-drive")
router.register(r"participations", DonationParticipationViewSet, basename="donation-participation")

urlpatterns = router.urls
