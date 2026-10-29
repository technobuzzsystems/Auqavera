from django import forms
from apps.catalog.models import Product, Category
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'slug',
            'category',
            'short_description',
            'description',
            'technology',
            'storage_capacity_liters',
            'price',
            'original_price',
            'image',
            'image_alt_text',
            'purification_stages',
            'intended_use',
            'maintenance_information',
            'is_featured',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'leave blank to auto-generate'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'technology': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RO + UV + UF + TDS Control'}),
            'storage_capacity_liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'purification_stages': forms.TextInput(attrs={'class': 'form-control'}),
            'intended_use': forms.TextInput(attrs={'class': 'form-control'}),
            'maintenance_information': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EnquiryStatusForm(forms.ModelForm):
    class Meta:
        model = ProductEnquiry
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }


class ServiceStatusForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }
