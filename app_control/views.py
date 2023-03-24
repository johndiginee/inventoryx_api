from rest_framework.viewsets import ModelViewSet
from .serializer import (
    Inventory, InventoryGroup, InventorySerializer, InventoryGroupSerializer,
    Shop, ShopSerializer
)
from rest_framework.response import Response
from inventoryx_api.custom_methods import IsAuthenticationCustom
from inventoryx_api.utils import CustomPagination, get_query
from django.db.models import Count


class InventoryView(ModelViewSet):
    """Class for inventory view."""
    queryset = Inventory.objects.select_related("group", "created_by")
    serializer_class = InventorySerializer
    permission_classes = (IsAuthenticationCustom,)
    pagination_class = CustomPagination

    def get_query(self):
        """Implementing search."""
        if self.request.method.lower() != "get":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)

        results = self.queryset(**data)

        if keyword:
            search_fields = (
                "code", "created_by__fullname", "created_by__email", 
                "group__name", "name"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)

        return results

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
    pagination_class = CustomPagination

    def get_query(self):
        """Implementing search."""
        if self.request.method.lower() != "get":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)

        results = self.queryset(**data)

        if keyword:
            search_fields = (
                "created_by__fullname", "created_by__email", "name"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)


        return results.annotate(
            total_items = Count('inventories')
        )


    def create(self, request, *args, **kwargs):
        """Over ride data"""
        request.data.update({"created_by_id":request.user.id})
        return super().create(request, *args, **kwargs)


class ShopView(ModelViewSet):
    """Class for shop view."""
    queryset = Shop.objects.select_related("created_by")
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticationCustom,)
    pagination_class = CustomPagination

    def get_query(self):
        """Implementing search."""
        if self.request.method.lower() != "get":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)

        results = self.queryset(**data)

        if keyword:
            search_fields = (
                "created_by__fullname", "created_by__email", "name"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)


        return results

    def create(self, request, *args, **kwargs):
        """Over ride data"""
        request.data.update({"created_by_id":request.user.id})
        return super().create(request, *args, **kwargs)