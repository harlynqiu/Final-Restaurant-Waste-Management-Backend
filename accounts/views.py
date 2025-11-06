# accounts/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .models import OwnerProfile
from .serializers import OwnerProfileSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register_owner(request):
    print("DEBUG REGISTER OWNER DATA:", request.data)

    data = request.data

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    restaurant_name = data.get("restaurant_name")
    address = data.get("address", "")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # ✅ Required fields
    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Create User
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    # ✅ Parse coordinates safely
    try:
        latitude = float(latitude) if latitude not in ["", None] else None
        longitude = float(longitude) if longitude not in ["", None] else None
    except:
        return Response({"error": "Invalid latitude/longitude"}, status=400)

    # ✅ Create Owner Profile
    try:
        owner = OwnerProfile.objects.create(
            user=user,
            restaurant_name=restaurant_name,
            address=address,
            latitude=latitude,
            longitude=longitude,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    return Response(
        OwnerProfileSerializer(owner).data,
        status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def owner_profile(request):
    try:
        owner = request.user.owner_profile
    except OwnerProfile.DoesNotExist:
        return Response({"error": "Owner profile not found"}, status=404)

    return Response(OwnerProfileSerializer(owner).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_owner(request):
    try:
        owner = request.user.owner_profile
    except OwnerProfile.DoesNotExist:
        return Response({"error": "Owner profile not found"}, status=404)

    serializer = OwnerProfileSerializer(
        owner,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)
