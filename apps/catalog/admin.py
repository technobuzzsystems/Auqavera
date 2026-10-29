from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'technology', 'storage_capacity_liters', 'price', 'original_price', 'is_featured', 'is_active')
    list_filter = ('category', 'technology', 'is_featured', 'is_active')
    list_editable = ('price', 'original_price', 'is_featured', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'technology', 'purification_stages', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'short_description', 'description')
        }),
        ('Purification & Specs', {
            'fields': ('technology', 'purification_stages', 'storage_capacity_liters', 'intended_use', 'maintenance_information', 'specifications')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'original_price', 'is_featured', 'is_active')
        }),
        ('Media (Optional future product image)', {
            'fields': ('image', 'image_alt_text'),
            'description': 'Leave image blank to automatically render the attractive CSS water gradient placeholder.'
        }),
    )
