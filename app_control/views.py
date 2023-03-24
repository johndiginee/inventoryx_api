from rest_framework.viewsets import ModelViewSet
from .serializer import (
    Inventory, InventoryGroup, InventorySerializer, InventoryGroupSerializer,
    Shop, ShopSerializer, Invoice, InvoiceSerializer
)
from rest_framework.response import Response
from inventoryx_api.custom_methods import IsAuthenticationCustom
from inventoryx_api.utils import CustomPagination, get_query
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from user_control.models import CustomUser


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


class InvoiceView(ModelViewSet):
    """Class for invoice view."""
    queryset = Invoice.objects.select_related(
        "created_by", "shop").prefetch_related("invoice_items")
    serializer_class = InvoiceSerializer
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
                "created_by__fullname", "created_by__email", "shop__name"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)


        return results

    def create(self, request, *args, **kwargs):
        """Over ride data"""
        request.data.update({"created_by_id":request.user.id})
        return super().create(request, *args, **kwargs)


class SummaryView(ModelViewSet):
    """Class for summary view."""
    http_method_names = ('get',)
    permission_classes = (IsAuthenticationCustom,)
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        """Get the summary list."""
        total_inventory = InventoryView.queryset.filter(
            remaining_gt=0
        ).count()
        total_group = InventoryGroupView.queryset.count()
        total_shop = ShopView.queryset.count()
        total_users = CustomUser.objects.filter(is_superuser=False).count()

        return Response({
            "total_inventory": total_inventory,
            "total_group": total_group,
            "total_shop": total_shop,
            "total_users": total_users
        })


class SalePerformance(ModelViewSet):
    """Class for sale performace."""
    http_method_names = ('get',)
    permission_classes = (IsAuthenticationCustom,)
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        """Get the list of top performing items."""
        query_data = request.query_params.dict()
        total = query_data.get('total', None)
        query = self.queryset

        if not total: #Check for date range items
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)

            if start_date:
                query = query.filter(
                    inventory_invoices__created_at__range=[start_date, end_date]
                )

        items = query.annotate(
            sum_of_item=Coalesce(
                Sum("inventory_invoices__quantity")
            )
        ).order('-sum_of_item')[0:10]
