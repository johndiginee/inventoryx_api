from rest_framework.permissions import BasePermission
from .utils import decodeJWT

class IsAuthenticationCustom(BasePermission):
    """Class for adding permission."""

    def has_permission(self, request):
        auth_token = request.Meta.get("HTTP_AUTHORIZATION", None)
        if not auth_token:
            return False
        
        user = decodeJWT(auth_token)

        if not user:
            return False
        
        request.user = user
        return True