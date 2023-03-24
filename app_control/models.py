from django.db import models
from user_control.models import CustomUser
from user_control.views import add_user_activity

class InventoryGroup(models.Model):
    """Class for creating inventory group."""
    created_by = models.ForeignKey(
        CustomUser, null=True, related_name="inventory_groups", 
        on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=100, unique=True)
    belongs_to = models.ForeignKey(
        'self', null=True, on_delete=models.SET_NULL, related_name="group_relations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
    
    def __init__(self, *args, **kwargs):
        sueper().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        action = f"added new group - '{self.name}'"
        if self.pk is not None:
            action = f"updated group from - '{self.old_name}' to '{self.name}'"
        super().save(*args, **kwargs)
        add_user_activity(self.created_by, action=action)
    
    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted group - '{self.name}'"
        super().delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """Class for creating inventory items."""
    created_by = models.ForeignKey(
        CustomUser, null=True, related_name="inventory_items", 
        on_delete=models.SET_NULL
    )
    code = models.CharField(max_length=10, unique=True, null=True)
    photo = models.TextField(blank=True, null=True)
    group = models.ForeignKey(
        InventoryGroup, related_name="inventories", null=True, on_delete=models.
        SET_NULL
    )
    total = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        """Save item"""
        is_new = self.pk is None

        if is_new:
            self.remaining = self.total
        
        super().save(*args, **kwargs)

        if is_new:
            """Generating unique code"""
            id_length = len(str(self.id))
            code_length = 6 - id_length
            zeros = "".join("0" for i in range(code_length))
            self.code = f"INTX{zeros}{self.id}"
            self.save()
        
        action = f"added new inventory item with code - '{self.code}'"

        if not is_new:
            action = f"updated inventory item with code - '{self.code}'"
        
        add_user_activity(self.created_by, action=action)
    
    def delete(self, *args, **kwargs):
        """Delete item"""
        created_by = self.created_by
        action = f"deleted inventory - '{self.code}'"
        super().delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return f"{self.name} - {self.code}"


class Shop(models.Model):
    """Class for creating shop."""
    created_by = models.ForeignKey(
        CustomUser, null=True, related_name="shops", 
        on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
    
    def __init__(self, *args, **kwargs):
        sueper().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        """Save shop"""
        action = f"added new shop - '{self.name}'"
        if self.pk is not None:
            action = f"updated shop from - '{self.old_name}' to '{self.name}'"
        super().save(*args, **kwargs)
        add_user_activity(self.created_by, action=action)
    
    def delete(self, *args, **kwargs):
        """Delete shop"""
        created_by = self.created_by
        action = f"deleted shop - '{self.name}'"
        super().delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    """Class for creating invoice."""
    created_by = models.ForeignKey(
        CustomUser, null=True, related_name="invoices", 
        on_delete=models.SET_NULL
    )
    shop = models.ForeignKey(
        Shop, related_name="sale_shop", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        """Save invoice"""
        action = f"added new invoice"
        super().save(*args, **kwargs)
        add_user_activity(self.created_by, action=action)
    
    def delete(self, *args, **kwargs):
        """Delete invoice"""
        created_by = self.created_by
        action = f"deleted invoice - '{self.id}'"
        super().delete(*args, **kwargs)
        add_user_activity(created_by, action=action)


class InvoiceItem(models.Model):
    """Class for creating invoice items."""
    invoice = models.ForeignKey(
        Invoice, related_name="invoice_items", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
            Inventory, null=True, related_name="inventory_invoices", 
            on_delete=models.SET_NULL
    )
    item_name = models.CharField(max_length=255, null=True)
    item_code = models.CharField(max_length=20, null=True)
    quantity = models.PositiveSmallIntegerField()
    amount = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        """Save invoice item"""
        if self.item.remaining < self.quantity:
            raise Exception(f"item with code {self.item.code} does not have a enough quantity")

        self.item_name = self.item.name
        self.item_code = self.item.code

        self.amount = self.quantity * self.item.price
        self.item.remaining = self.item.remaining - self.quantity
        self.item.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_code} - {self.quantity}"
