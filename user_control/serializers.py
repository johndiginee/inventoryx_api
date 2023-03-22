from rest_framework import serializers
from .models import CustomUser, Roles


class CreateUserSerializer(serializers.Serializer):
    """Class for create user serializer."""
    email = serializers.EmailField()
    fullname = serializers.CharField()
    role = serializers.ChoiceField(Roles)

class LoginSerializer(serializers.Serializer):
    """Class for user login serializer."""
    email = serializers.EmailField()
    password = serializers.CharField(required=False)
    is_new_user = serializers.BooleanField(default=False, required=False)

class UpdatePasswordSerializer(serializers.Serializer):
    """Class for user password update serializer."""
    user_id = serializers.CharField()
    password = serializers.CharField()

class CustomUserSerializer(serializers.ModelSerializer):
    """Class for convert model data too json."""

    class Meta:
        mdoel = CustomUser
        exclude = ("password", )