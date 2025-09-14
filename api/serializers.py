from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserFile, Profile, Book, Reader


class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]

    def create(self, validated_data):
        # create user with hashed password
        return User.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            password=validated_data.get("password"),
        )


# ---- Auth related request bodies ----
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ["profile_pic"]


##Now learning about the nested and the related data api's


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


# Profile serializer (nested user )


class ProfileSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "bio", "website", "author"]


# Book Serializer (Nested is user )


class BookSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ["id", "title", "author"]


# Reader Serializer (nested Books)
class ReaderSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Reader
        fields = ["id", "name", "books"]


# versioning serializers


class UserSerializerV1(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]  # basic info


class UserSerializerV2(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
