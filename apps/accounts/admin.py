from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'city', 'is_staff', 'is_customer')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_customer')
    fieldsets = UserAdmin.fieldsets + (
        ('Customer Profile Info', {
            'fields': ('phone_number', 'city', 'address', 'is_customer')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Customer Profile Info', {
            'fields': ('phone_number', 'city', 'address', 'is_customer')
        }),
    )
