# users/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Returns the currently authenticated user's details and role.
    """
    user = request.user
    role = "owner"

    # Determine role based on related models
    if hasattr(user, "driver_profile"):
        role = "driver"
    elif hasattr(user, "employeeprofile"):
        role = "restaurant"

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role,
    }, status=status.HTTP_200_OK)
