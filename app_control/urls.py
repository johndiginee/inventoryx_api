from django.urls import path, include
from .views import (
    InventoryView, ShopView, SummaryView, PurchaseView, SaleByShopView,
    InventoryGroupView, SalePerformanceView, InvoiceView, InventoryCSVLoaderView
)
from rest_framework.routers import DefaultRouter

# Disable trailing slash
routers = DefaultRouter(trailing_slash=False)

# Register the view
routers.register("inventory", InventoryView, 'inventory')
routers.register("inventory-csv", InventoryCSVLoaderView, 'inventory-csv')
routers.register("shop", ShopView, 'shop')
routers.register("summary", SummaryView, 'summary')
routers.register("purchase-summary", PurchaseView, 'purchase-summary')
routers.register("sales-by-shop", SaleByShopView, 'sales-by-shop')
routers.register("group", InventoryGroupView, 'group')
routers.register("top-selling", SalePerformanceView, 'top-selling')
routers.register("invoice", InvoiceView, 'invoice')

# Register the urls
urlpatterns = [
    path("", include(router.urls))
]