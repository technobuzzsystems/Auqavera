from django.contrib import admin
from .models import ServiceRequest

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'customer_name', 'mobile', 'city', 'product_model', 'service_type', 'preferred_date', 'status', 'created_at')
    list_filter = ('status', 'service_type', 'preferred_date')
    list_editable = ('status',)
    search_fields = ('reference_number', 'customer_name', 'mobile', 'city', 'product_model', 'issue_description')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
