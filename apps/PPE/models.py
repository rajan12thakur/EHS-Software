from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from apps.accounts.models import User

class PPECategory(models.Model):
    """Categories for create form which take input like name,code,description,status"""
    
    category_name = models.CharField(
        max_length=200, 
        unique=True,
        verbose_name="Category Name",
        help_text="Ex:-Head Protection,Eye Protection"
    )
    category_code = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="Short Code",
        help_text="Short code like HP,EP,FP"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Description"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active Status"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_ppecategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ppe_categories'
        verbose_name = "PPE Category"
        verbose_name_plural = "PPE Categories"




class PPECategory(models.Model):
    """Master PPE Categories"""

    category_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Category Name"
    )

    category_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Category Code",
        help_text="Example: HEL, GLO, SHOE"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active Status"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ppe_categories"
        ordering = ['category_name']
        verbose_name = "PPE Category"
        verbose_name_plural = "PPE Categories"

    def __str__(self):
        return self.category_name



from django.db import models


class PPEItem(models.Model):
    """Master PPE Items"""

    YES_NO_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
    ]

    ppe_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="PPE Code"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="PPE Name"
    )

    category = models.ForeignKey(
        'PPECategory',
        on_delete=models.PROTECT,
        related_name='ppe_items',
        verbose_name="Category"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )

    manufacturer_brand = models.CharField(
        max_length=255,
        verbose_name="Manufacturer / Brand"
    )

    model_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Model Number"
    )

    manufacturing_date = models.DateField(
        verbose_name="Manufacturing Date"
    )

    expiry_date = models.DateField(
        verbose_name="Expiry Date"
    )

    expiry_days = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Expiry Days"
    )

    inspection_required = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='NO',
        verbose_name="Inspection Required"
    )

    replacement_required = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='NO',
        verbose_name="Replacement Required"
    )

    size_applicable = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='NO',
        verbose_name="Size Applicable"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active Status"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ppe_items"
        ordering = ['ppe_code']
        verbose_name = "PPE Item"
        verbose_name_plural = "PPE Items"

        indexes = [
            models.Index(fields=['ppe_code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.ppe_code} - {self.name}"

    def save(self, *args, **kwargs):
        # Auto-generate PPE code
        if not self.ppe_code:
            self.ppe_code = self.generate_ppe_code()

        # Calculate expiry days
        if self.manufacturing_date and self.expiry_date:
            self.expiry_days = (
                self.expiry_date - self.manufacturing_date
            ).days
        else:
            self.expiry_days = 0

        super().save(*args, **kwargs)

    @classmethod
    def generate_ppe_code(cls):
        last_item = cls.objects.order_by('-id').first()

        if last_item and last_item.ppe_code:
            try:
                last_number = int(last_item.ppe_code.replace('PPE', ''))
                new_number = last_number + 1
            except ValueError:
                new_number = 1
        else:
            new_number = 1

        return f"PPE{new_number:04d}"


class PPESizeQuantity(models.Model):
    """Stores size-wise PPE mapping"""

    ppe_item = models.ForeignKey(
        PPEItem,
        on_delete=models.CASCADE,
        related_name='size_quantities',
        verbose_name="PPE Item"
    )

    size = models.CharField(
        max_length=50,
        verbose_name="Size"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ppe_size_quantities"
        unique_together = ('ppe_item', 'size')
        ordering = ['ppe_item', 'size']

        indexes = [
            models.Index(fields=['ppe_item']),
            models.Index(fields=['size']),
        ]

    def __str__(self):
        return f"{self.ppe_item.name} - {self.size}"