from .models import Inventory, InventoryGroup, Shop, Invoice, InvoiceItem
from user_control.serializers import CustomUserSerializer
from rest_framework import serializers

class InventoryGroupSerializer(serializers.ModelSerializer):
    """Class for inventory group serializer."""
    created_by = CustomUserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    belongs_to = serializers.SerializerMethodField(read_only=True)
    belongs_to_id = serializers.CharField(write_only=True)
    total_items = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = InventoryGroup
        fields = "__all__"

    def get_belongs_to(self, obj):
        if obj.belongs_to is None:
            return InventoryGroupSerializer(obj.belongs_to).data
        return None


class InventorySerializer(serializers.ModelSerializer):
    """Class for inventory serializer."""
    created_by = CustomUserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    group = InventoryGroupSerializer(read_only=True)
    group_id = serializers.CharField(write_only=True)

    class Meta:
        model = Inventory
        fields = "__all__"


class InventoryWithSumSerializer(InventorySerializer):
    """Class for inventory with sum serializer."""
    sum_of_item = serializers.IntegerField()


class ShopSerializer(serializers.ModelSerializer):
    """Class for shop serializer."""
    created_by = CustomUserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    amount_total = serializers.CharField(read_only=True, required=False)
    count_total = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Shop
        fields = "__all__"


class ShopWithAmountSerializer(ShopSerializer):
    """Class for shop with amount serializer."""
    amount_total = serilizer.FloatField()
    month = serializers.CharField(required=False)


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Class for invoice item serializer."""
    invoice = serializers.CharField(read_only=True)
    invoice_id = serializers.CharField(write_only=True)
    item = serializers.CharField(read_only=True)
    item_id = serializers.CharField(write_only=True)

    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceItemDataSerializer(serializers.ModelSerializer):
    """Class for invoice item data serializer."""
    item_id = serializers.CharField()
    quantity = serializers.IntegerField()


class InvoiceSerializer(serializers.ModelSerializer):
    """Class for invoice serializer."""
    created_by = CustomUserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    shop = ShopSerializer(read_only=True)
    shop_id = serializers.CharField(write_only=True)
    invoice_items = InvoiceItemSerializer(read_only=True, many=True)
    invoice_items_data = InvoiceItemDataSerializer(write_only=True, many=True)

    class Meta:
        model = Invoice
        fields = "__all__"

    def create(self, validated_data):
        """Create invoice"""
        invoice_items_data = validated_data.pop("invoice_item_data")

        if not invoice_items_data:
            raise Exception("You need to provide at least one invoice item")

        invoice = super().create(validated_data)

        invoice_items_serializer = InvoiceItemSerializer(data=[
            {"invoice_id": invoice.id, **item} for item in invoice_items_data
        ], many=True)

        if invoice_items_serializer.is_valid():
            invoice_items_serializer.save()
        else:
            invoice.delete()
            raise Exception(invoice_items_serializer.errors)
        
        return invoice