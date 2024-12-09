from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


# Register API
@api_view(["POST"])
@permission_classes([AllowAny])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "Account created successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login API
@api_view(["POST"])
@permission_classes([AllowAny])
def login_request_api(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)  # JWT Token generation
        return Response({
            "message": "Login successful!",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "username": user.username,
                "email": user.email
            }
        })
    return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


# Logout API
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_request_api(request):
    logout(request)
    return Response({"message": "Logged out successfully!"}, status=status.HTTP_200_OK)

# Delete User API
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user_api(request):
    user = request.user
    user.delete()
    return Response({"message": "Account deleted successfully!"}, status=status.HTTP_200_OK)
