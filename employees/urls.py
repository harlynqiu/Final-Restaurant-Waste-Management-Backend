from rest_framework import routers
from .views import EmployeeViewSet

router = routers.DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = router.urls
