from rest_framework.viewsets import ModelViewSet
from .serializers import (
    Inventory, InventoryGroup, InventorySerializer, InventoryGroupSerializer,
    Shop, ShopSerializer, Invoice, InvoiceSerializer, InventoryWithSumSerializer,
    ShopWithAmountSerializer, InvoiceItem
)
from rest_framework.response import Response
from inventoryx_api.custom_methods import IsAuthenticationCustom
from inventoryx_api.utils import CustomPagination, get_query
from django.db.models import Count, Sum, F
from django.db.models.functions import Coalesce, TruncMonth
from user_control.models import CustomUser
import csv
import codecs


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


class SalePerformanceView(ModelViewSet):
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

        response_data = InventoryWithSumSerializer(items, many=True).data
        return Response(response_data)


class SaleByShopView(ModelViewSet):
    """Class for sale by shop view."""
    http_method_names = ('get',)
    permission_classes = (IsAuthenticationCustom,)
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        """Show sale show list."""
        query_data = request.query_params.dict()
        total = query_data.get('total', None)
        monthly = query_data.get('monthly', None)
        query = ShopView.queryset

        if not total:
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)

            if start_date:
                query = query.filter(
                    sale_shop__created_at__range=[start_date, end_date]
                )
        
        if monthly:
            shops = query.annotate(month=TruncMonth('created_at')).values(
                'month', 'name').annotate(amount_total=Sum(
                    F("sale_shop__invoice_items__quantity") *
                    F("sale_shop__invoice_items__amount")
                ))

        else:
            shops = query.annotate(amount_total=Sum(
                    F("sale_shop__invoice_items__quantity") *
                    F("sale_shop__invoice_items__amount")
                )).order_by("-amount_total")

        response_data = ShopWithAmountSerializer(shops, many=True).data
        return Response(response_data)


class PurchaseView(ModelViewSet):
    """Class for purchase view."""
    http_method_names = ('get',)
    permission_classes = (IsAuthenticationCustom,)
    queryset = InvoiceView.queryset

    def list(self, request, *args, **kwargs):
        """Get the list of purchase items."""
        query_data = request.query_params.dict()
        total = query_data.get('total', None)
        query = InvoiceItem.objects.select_related("invoice", "item")

        if not total: #Check for date range items
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)

            if start_date:
                query = query.filter(
                    created_at__range=[start_date, end_date]
                )
        
        query = query.aggregate(
            amount_total=Sum(F('amount') * F('quantity')), total=Sum('quanttity')
            )
        
        return Response({
            "price": "0.00" if not query.get("amount_total") else query.get("amount_total"),
            "count": 0 if not query.get("total") else query.get("total"),
        })


class InventoryCSVLoaderView(ModelViewSet):
    """Class for loading CSV files."""
    http_method_names = ('post',)
    queryset = InventoryView.queryset
    permission_classes = (IsAuthenticationCustom,)
    serializer_class = InventorySerializer

    def create(self, request, *args, **kwargs):
        """Adding csv data."""
        try:
            data = request.FILES['data']
        except Exception as e:
            raise Exception("You need to provide inventory CSV 'data'")

        inventory_items = []

        try:
            csv_reader = csv.reader(codecs.iterencode(data, 'utf-8'))
            for row in csv_reader:
                if not row[0]:
                    continue
                inventory_items.append(
                    {
                        "group_id": row[0],
                        "total": row[1],
                        "name": row[2],
                        "price": row[3],
                        "photo": row[4],
                        "added_by_id": request.user.id,
                    }
                )
        except csv.Error as e:
            raise Exception(e)
        
        if not inventory_items:
            raise Exception("CSV file cannot be empty")

        data_validation = self.serializer_class(data=inventory_items, many=True)
        data_validation.is_valid(raise_exception=True)
        data_validation.save()

        return Response({"success": "Inventory items added successfully"})