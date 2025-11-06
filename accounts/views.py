# accounts/views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OwnerProfile
from .serializers import OwnerProfileSerializer

@api_view(["POST"])
@permission_classes([AllowAny])
def register_owner(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    restaurant_name = request.data.get("restaurant_name")
    address = request.data.get("address")
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    if not username or not password or not restaurant_name or not address:
        return Response(
            {"success": False, "message": "Missing required fields."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"success": False, "message": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if email and User.objects.filter(email=email).exists():
        return Response(
            {"success": False, "message": "Email already in use."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create user
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )

    # Create owner profile
    OwnerProfile.objects.create(
        user=user,
        restaurant_name=restaurant_name,
        address=address,
        latitude=latitude,
        longitude=longitude
    )

    return Response(
        {"success": True, "message": "Restaurant owner registered successfully."},
        status=status.HTTP_201_CREATED
    )

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def owner_profile(request):
    try:
        profile = request.user.owner_profile
    except OwnerProfile.DoesNotExist:
        return Response(
            {"success": False, "message": "Owner profile not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = OwnerProfileSerializer(profile)
    return Response(serializer.data)

@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_owner(request):
    try:
        profile = request.user.owner_profile
    except OwnerProfile.DoesNotExist:
        return Response(
            {"success": False, "message": "Owner profile not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = OwnerProfileSerializer(
        profile, data=request.data, partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"success": True, "message": "Profile updated successfully!",
             "profile": serializer.data}
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        identifier = request.data.get("username")
        password = request.data.get("password")

        if not identifier or not password:
            return Response(
                {"success": False, "message": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if "@" in identifier:
                user = User.objects.get(email__iexact=identifier)
            else:
                user = User.objects.get(username__iexact=identifier)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid username/email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=user.username, password=password)
        if not user:
            return Response(
                {"success": False, "message": "Invalid username/email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = (
            "owner" if hasattr(user, "owner_profile") else
            "driver" if hasattr(user, "driver_profile") else
            "employee" if hasattr(user, "employee_profile") else
            "user"
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "role": role,
                "verified": True,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
