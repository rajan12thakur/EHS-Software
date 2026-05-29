from django.db import models
from django.utils import timezone

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

