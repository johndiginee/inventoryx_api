from rest_framework.viewsets import ModelViewSet
from .serializer import (
    Inventory, InventoryGroup, InventorySerializer, InventoryGroupSerializer
)
from rest_framework.response import Response
from inventoryx_api.custom_methods import IsAuthenticationCustom


class InventoryView(ModelViewSet):
    """Class for inventory view."""
    queryset = Inventory.objects.select_related("group", "created_by")
    serializer_class = InventorySerializer
    permission_classes = (IsAuthenticationCustom,)

    def create(self, request, *args, **kwargs):
        """Over ride data"""
        request.data.update({"created_by_id":request.user.id})
        return super().create(request, *args, **kwargs)

class InventoryGroupView(ModelViewSet):
    """Class for inventory group view."""
    queryset = InventoryGroup.objects.select_related(
        "belongs_to", "created_by").prefetch_related("Inventories")
    serializer_class = InventoryGroupSerializer
    permission_classes = (IsAuthenticationCustom,)

    def create(self, request, *args, **kwargs):
        """Over ride data"""
        request.data.update({"created_by_id":request.user.id})
        return super().create(request, *args, **kwargs)