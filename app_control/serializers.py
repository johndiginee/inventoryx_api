from .models import Inventory, InventoryGroup, Shop
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


class ShopSerializer(serializers.ModelSerializer):
    """Class for shop serializer."""
    created_by = CustomUserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    amount_total = serializers.CharField(read_only=True, required=False)
    count_total = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Shop
        fields = "__all__"