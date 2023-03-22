from django.urls import path, include
from rest_framework import routers, urlpatterns
from .views import (
    CreateUserView, LoginView, UpdatePasswordView, MeView
)
from rest_framework.routers import DefaultRouter

# Disable trailing slash
routers = DefaultRouter(trailing_slash=False)

# Register the view
routers.register("create-user", CreateUserView, 'create user')
routers.register("login", LoginView, 'login')
routers.register("update-password", UpdatePasswordView, 'update password')
routers.register("me", MeView, 'me')

# Include in a url patterns
urlpatterns = [
    path("", include(routers.urls))
]
