from django.db import models
from apps.accounts.models import User


class ToolboxTalkCategory(models.Model):
    """
    Toolbox Talk Category Master

    Developed by Rajan
    """

    category_name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Category Name'
    )

    short_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Short Code'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Status'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_toolbox_categories'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        db_table = 'toolbox_talk_categories'

        ordering = ['category_name']

        verbose_name = 'Toolbox Talk Category'

        verbose_name_plural = 'Toolbox Talk Categories'

    def __str__(self):

        return f"{self.short_code} - {self.category_name}"