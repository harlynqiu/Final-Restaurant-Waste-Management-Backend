# trash_pickups/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import TrashPickup
from .serializers import TrashPickupSerializer
from employees.models import Employee
import datetime


class TrashPickupViewSet(viewsets.ModelViewSet):
    serializer_class = TrashPickupSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ------------------------------------------------
    # 🔍 GET QUERYSET (Driver or Regular User)
    # ------------------------------------------------
    def get_queryset(self):
        user = self.request.user

        # Drivers see only their assigned pickups
        if hasattr(user, "driver_profile"):
            return TrashPickup.objects.filter(driver=user.driver_profile).order_by("-created_at")

        # Regular users (restaurants) see their own pickups
        return TrashPickup.objects.filter(user=user).order_by("-created_at")

    # ------------------------------------------------
    # 🧱 CREATE PICKUP (auto-fill address + coordinates)
    # ------------------------------------------------
    def perform_create(self, serializer):
        user = self.request.user
        data = self.request.data

        employee = getattr(user, "employee_profile", None)
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        pickup_address = data.get("pickup_address")

        # ✅ Auto-fill from Employee if available
        if employee:
            pickup_address = pickup_address or getattr(employee, "address", None)
            latitude = latitude or getattr(employee, "latitude", None)
            longitude = longitude or getattr(employee, "longitude", None)
        else:
            try:
                emp = Employee.objects.get(user=user)
                pickup_address = pickup_address or emp.address
                latitude = latitude or emp.latitude
                longitude = longitude or emp.longitude
            except Employee.DoesNotExist:
                pass

        # ✅ Fallbacks
        if not pickup_address:
            pickup_address = "Davao City"
        if not latitude or not longitude:
            latitude, longitude = 7.0731, 125.6128

        # ✅ Flexible date parsing
        scheduled_date = data.get("scheduled_date")
        if not scheduled_date:
            scheduled_date = timezone.now()
        else:
            parsed_date = None
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ]:
                try:
                    parsed_date = datetime.datetime.strptime(scheduled_date, fmt)
                    break
                except ValueError:
                    continue
            parsed_date = parsed_date or timezone.now()
            if parsed_date < timezone.now():
                parsed_date = timezone.now()
            scheduled_date = parsed_date

        serializer.save(
            user=user,
            pickup_address=pickup_address,
            latitude=latitude,
            longitude=longitude,
            scheduled_date=scheduled_date,
        )

    # ------------------------------------------------
    # 🔐 GET OBJECT (allow drivers or creators)
    # ------------------------------------------------
    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if hasattr(user, "driver_profile"):
            if obj.driver is None or obj.driver == user.driver_profile:
                return obj
        elif obj.user == user:
            return obj

        self.permission_denied(self.request, message="You are not allowed to access this pickup.")

    # ------------------------------------------------
    # 🚗 AVAILABLE PICKUPS
    # ------------------------------------------------
    @action(detail=False, methods=["get"], url_path="available")
    def available_pickups(self, request):
        pickups = TrashPickup.objects.filter(driver__isnull=True, status="pending")
        serializer = self.get_serializer(pickups, many=True)
        return Response(serializer.data)

    # ------------------------------------------------
    # 🚚 ACCEPT PICKUP
    # ------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="accept")
    def accept_pickup(self, request, pk=None):
        user = request.user
        if not hasattr(user, "driver_profile"):
            return Response({"detail": "You are not registered as a driver."}, status=403)

        try:
            pickup = TrashPickup.objects.get(pk=pk)
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."}, status=404)

        if pickup.driver:
            return Response({"detail": "This pickup has already been accepted."}, status=400)

        pickup.driver = user.driver_profile
        pickup.status = "accepted"
        pickup.save(update_fields=["driver", "status"])

        return Response(
            {"success": True, "message": f"Pickup #{pickup.id} accepted successfully."},
            status=200,
        )

    # ------------------------------------------------
    # 🚀 START PICKUP
    # ------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="start")
    def start_pickup(self, request, pk=None):
        try:
            pickup = TrashPickup.objects.get(pk=pk)
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."}, status=404)

        if pickup.status not in ["accepted", "in_progress"]:
            return Response({"detail": "Pickup must be accepted before starting."}, status=400)

        pickup.status = "in_progress"
        pickup.save(update_fields=["status"])
        return Response(
            {"success": True, "message": f"Pickup #{pickup.id} marked as In Progress."}, status=200
        )

    # ------------------------------------------------
    # ✅ COMPLETE PICKUP (Reward → Restaurant User)
    # ------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="complete")
    def complete_pickup(self, request, pk=None):
        from rewards.models import RewardPoint, RewardTransaction
        from drivers.models import Driver

        try:
            pickup = TrashPickup.objects.get(pk=pk)
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."}, status=404)

        # ✅ Allow only restaurant user or assigned driver
        user = request.user
        if not (
            pickup.user == user or
            (hasattr(user, "driver_profile") and pickup.driver == user.driver_profile)
        ):
            return Response(
                {"detail": "You are not authorized to complete this pickup."},
                status=403,
            )

        if pickup.status not in ["in_progress", "accepted"]:
            return Response({"detail": "This pickup cannot be completed yet."}, status=400)

        # ✅ Mark as completed
        pickup.status = "completed"
        pickup.save(update_fields=["status"])

        # ✅ Reward the restaurant user
        restaurant_user = pickup.user
        if not restaurant_user:
            return Response(
                {"success": False, "message": "No restaurant user linked to this pickup."},
                status=400,
            )

        reward, _ = RewardPoint.objects.get_or_create(user=restaurant_user)
        reward.add_points(10)

        RewardTransaction.objects.create(
            user=restaurant_user,
            pickup=pickup,
            points=10,
            description=f"Pickup #{pickup.id} completed successfully (+10 pts to {restaurant_user.username})",
        )

        # ✅ Update driver stats
        driver = pickup.driver
        if driver:
            driver.total_completed_pickups += 1
            driver.status = "available"
            driver.save(update_fields=["total_completed_pickups", "status"])

        print(f"🎯 Reward added for restaurant {restaurant_user.username}: now has {reward.points} points")

        return Response(
            {
                "success": True,
                "message": f"Pickup #{pickup.id} completed. +10 points added to restaurant {restaurant_user.username}.",
                "points_added": 10,
                "total_points": reward.points,
            },
            status=200,
        )

    # ------------------------------------------------
    # ❌ CANCEL PICKUP
    # ------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel_pickup(self, request, pk=None):
        try:
            pickup = self.get_object()
        except TrashPickup.DoesNotExist:
            return Response({"detail": "Pickup not found."}, status=404)

        pickup.status = "cancelled"
        pickup.save(update_fields=["status"])
        return Response({"message": "Pickup cancelled successfully"}, status=200)
