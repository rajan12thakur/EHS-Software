from django.contrib import admin

from .models import ToolboxTalkCategory


@admin.register(ToolboxTalkCategory)
class ToolboxTalkCategoryAdmin(admin.ModelAdmin):

    list_display = [
        'category_name',
        'short_code',
        'is_active',
        'created_at'
    ]

    search_fields = [
        'category_name',
        'short_code'
    ]

    list_filter = [
        'is_active'
    ]