from django.contrib import admin
from .models import ProductEnquiry

@admin.register(ProductEnquiry)
class ProductEnquiryAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'customer_name', 'email', 'mobile', 'city', 'product', 'enquiry_type', 'status', 'created_at')
    list_filter = ('status', 'enquiry_type', 'created_at')
    list_editable = ('status',)
    search_fields = ('reference_number', 'customer_name', 'email', 'mobile', 'city', 'message')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
