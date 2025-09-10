from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from .serializers import (
    UserProfileSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    UserFileSerializer,
    ProfileSerializer,
    BookSerializer,
    ReaderSerializer,
)
from .models import UserProfile, UserFile, Profile, Book, Reader

from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
import os
from django.contrib.auth.models import User


# ----------------- User CRUD -----------------
class UserViewset(viewsets.ViewSet):
    """Basic CRUD + custom action for UserProfile"""

    def list(self, request):
        users = UserProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserProfileSerializer)
    def create(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            user = UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserProfileSerializer)
    def update(self, request, pk=None):
        try:
            user = UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            user = UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        try:
            user = UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        user.is_active = True
        user.save()
        return Response({"status": "User activated"})

    # image upload and download feature
    upload_profile_pic_params = [
        openapi.Parameter(
            "profile_pic",
            openapi.IN_FORM,
            description="Upload a profile picture",
            type=openapi.TYPE_FILE,
            required=True,
        ),
    ]

    @swagger_auto_schema(
        method="post",
        manual_parameters=upload_profile_pic_params,
        responses={200: "Profile picture uploaded!"},
    )
    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload_profile_pic(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserFileSerializer(data=request.data)
        if serializer.is_valid():
            user_file, _ = UserFile.objects.get_or_create(user=user)
            user_file.profile_pic = serializer.validated_data["profile_pic"]
            user_file.save()
            return Response({"message": "Profile picture saved!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def download_profile_pic(self, request, pk=None):
        try:
            user_file = UserFile.objects.get(user__pk=pk)
        except UserFile.DoesNotExist:
            return Response(
                {"error": "No file found"}, status=status.HTTP_404_NOT_FOUND
            )
        if not user_file.profile_pic:
            return Response(
                {"error": "No profile picture uploaded"},
                status=status.HTTP_404_NOT_FOUND,
            )
        file_path = user_file.profile_pic.path
        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=os.path.basename(file_path),
        )


# ----------------- Auth APIs -----------------
class AuthViewset(viewsets.ViewSet):
    """Signup, Login, Logout, Refresh, and Me"""

    @swagger_auto_schema(request_body=UserProfileSerializer)
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def signup(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=LogoutSerializer)
    @action(detail=False, methods=["post"])
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out succesfully"}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(request_body=LoginSerializer)
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)
        if user is None:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user=user)
        return Response(
            {
                "user": {"id": user.id, "username": user.username, "email": user.email},
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            }
        )

    @swagger_auto_schema(request_body=RefreshSerializer)
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def refresh(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh"]
            refresh = RefreshToken(refresh_token)
            return Response({"access": str(refresh.access_token)})
        except Exception:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )


# nested and the related fields api responses
# select related and the prefetch realted meaning below
# “Hey, when you fetch Profile, also bring the related author object in the same SQL query.”


class ProfileViewset(viewsets.ViewSet):
    def list(self, request):
        profiles = Profile.objects.select_related("author")
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)


class BookViewset(viewsets.ViewSet):
    def list(self, request):
        books = Book.objects.select_related("author")
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class ReaderViewset(viewsets.ViewSet):
    def list(self, request):
        readers = Reader.objects.prefetch_related("books")
        serializer = ReaderSerializer(readers, many=True)
        return Response(serializer.data)
