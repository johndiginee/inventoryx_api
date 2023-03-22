from rest_framework.viewsets import ModelViewSet
from .serializers import (
    CreateUserSerializer, CustomUser, LoginSerializer
)
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datatime import datatime
from inventoryx_api.utils import get_access_token


class CreateUserView(ModelViewSet):
    """Class for create user view."""
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer

    def create(self, request):
        """Valid data and create user."""
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        CustomUser.objects.create(**valid_request.validated_data)

        return Response(
            {"success": "User created successfully"},
            status=status.HTTP_201_CREATED
        )

class LoginView(ModelViewSet):
    """Class for user login view."""
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer()

    def create(self, request):
        """Valid data and login user."""
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        new_user = valid_request.validated_data["is_new_user"]
        
        if new_user:
            user = CustomUser.objects.filter(
                email=valid_request.validated_data["email"]
            )

            if user:
                user = user[0]
                if not user.password:
                    return Response({"user_id": user.id})
                else:
                    raise Exception("User has password already")
            else:
                raise Exception("User with email not found")
        
        user = authenticate(
            username=valid_request.validated_data["email"],
            password=valid_request.validated_data.get("password", None)
        )

        if not user:
            return Response(
                {"error": "Invaild email or password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        """Get access token"""
        access = get_access_token({"user_id": user.id}, 1)

        """Update user last login"""
        user.last_login = datatime.now()
        user.save()

        return Response(["access": access])