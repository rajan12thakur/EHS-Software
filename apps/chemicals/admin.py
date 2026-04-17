from django.contrib import admin
from .models import Chemical, ChemicalRequest


@admin.register(Chemical)
class ChemicalAdmin(admin.ModelAdmin):
    list_display = (
        'chemical_name',
        'cas_number',
        'plant',
        'zone',
        'location',
        'quantity',
        'quantity_unit',
        'status',
        'expiration_date',
    )

    list_filter = (
        'status',
        'plant',
        'zone',
        'location',
        'quantity_unit',
        'expiration_date',
    )

    search_fields = (
        'chemical_name',
        'trade_name',
        'cas_number',
        'un_number',
        'supplier',
        'lot_number',
    )

    readonly_fields = ('created_at',)

    fieldsets = (
        ('Chemical Identification', {
            'fields': (
                'chemical_name',
                'trade_name',
                'cas_number',
                'un_number',
            )
        }),
        ('Sourcing & Inventory', {
            'fields': (
                'supplier',
                'lot_number',
                'receipt_date',
                'expiration_date',
            )
        }),
        ('Location Hierarchy', {
            'fields': (
                'plant',
                'zone',
                'location',
                'sublocation',
                'department',
            )
        }),
        ('Storage & Quantity', {
            'fields': (
                'quantity',
                'quantity_unit',
                'storage_location',
                'owner',
                'status',
            )
        }),
        ('EHS & SDS', {
            'fields': (
                'ehs_compliance',
                'sds_file',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'created_at',
            )
        }),
    )


@admin.register(ChemicalRequest)
class ChemicalRequestAdmin(admin.ModelAdmin):
    list_display = (
        'chemical_name',
        'cas_number',
        'quantity',
        'quantity_unit',
        'urgency',
        'status',
        'plant',
        'requester_name',
        'created_at',
    )

    list_filter = (
        'status',
        'urgency',
        'plant',
        'zone',
        'location',
        'quantity_unit',
        'created_at',
    )

    search_fields = (
        'chemical_name',
        'cas_number',
        'requester_name',
        'supplier_name',
        'catalog_number',
    )

    readonly_fields = ('created_at', 'approved_at')

    fieldsets = (
        ('Chemical Details', {
            'fields': (
                'chemical_name',
                'cas_number',
                'chemical_formula',
                'purity_grade',
            )
        }),
        ('Supplier Info', {
            'fields': (
                'supplier_name',
                'catalog_number',
            )
        }),
        ('Quantity & Urgency', {
            'fields': (
                'quantity',
                'quantity_unit',
                'urgency',
            )
        }),
        ('Location Hierarchy', {
            'fields': (
                'plant',
                'zone',
                'location',
                'sublocation',
                'department',
                'storage_location',
            )
        }),
        ('Requester Info', {
            'fields': (
                'requester_user',
                'requester_name',
                'justification',
            )
        }),
        ('Attachments', {
            'fields': (
                'attachment',
            )
        }),
        ('Approval', {
            'fields': (
                'status',
                'approved_by',
                'approved_at',
                'rejection_reason',
            )
        }),
        ('Inventory Link', {
            'fields': (
                'chemical',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
            )
        }),
    )