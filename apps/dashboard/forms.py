import os
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from apps.catalog.models import Product, Category, ProductImage, StockAdjustment
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest
from apps.content.models import SiteSetting

User = get_user_model()

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_image_file(file):
    """Ensure uploaded image is of valid format and within size constraints."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"Unsupported file format '{ext}'. Permitted formats: JPG, JPEG, PNG, WEBP.")
    if file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError("Image file exceeds the maximum 5MB size limit.")


class AdminLoginForm(forms.Form):
    """Administrator staff login form."""
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter staff username or email',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password',
            'id': 'admin-password-input',
        })
    )


class ProductForm(forms.ModelForm):
    """Complete product management form."""
    class Meta:
        model = Product
        fields = [
            'name',
            'slug',
            'sku',
            'brand',
            'category',
            'short_description',
            'description',
            'technology',
            'storage_capacity_liters',
            'price',
            'original_price',
            'purification_stages',
            'intended_use',
            'warranty_info',
            'maintenance_information',
            'stock_quantity',
            'low_stock_threshold',
            'status',
            'is_featured',
            'image',
            'image_alt_text',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AQUAVERA Crystal Pro RO'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'leave blank to auto-generate'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AQV-RO-101 (or auto-generated)'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AQUAVERA'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief tagline for product cards'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Comprehensive product overview'}),
            'technology': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RO + UV + UF + TDS Control'}),
            'storage_capacity_liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'placeholder': 'Current selling price'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'placeholder': 'Original MRP'}),
            'purification_stages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 7-Stage Multi-Barrier Filtration'}),
            'intended_use': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Home / Apartment'}),
            'warranty_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1 Year Comprehensive Warranty'}),
            'maintenance_information': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Accessibility descriptive text'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'slug' in self.fields:
            self.fields['slug'].required = False
        if 'sku' in self.fields:
            self.fields['sku'].required = False

    def clean_slug(self):
        slug = (self.cleaned_data.get('slug') or '').strip()
        if not slug:
            if self.instance and self.instance.pk and self.instance.slug:
                return self.instance.slug
            name = self.cleaned_data.get('name') or ''
            slug = slugify(name)
        return slug

    def clean_sku(self):
        sku = (self.cleaned_data.get('sku') or '').strip()
        if not sku and self.instance and self.instance.pk and self.instance.sku:
            return self.instance.sku
        return sku

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'file'):
            validate_image_file(image)
        return image

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError("Selling price must be greater than zero.")
        return price

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        original_price = cleaned_data.get('original_price')
        if price and original_price and original_price < price:
            self.add_error('original_price', "Original M.R.P. cannot be lower than the selling price.")
        return cleaned_data


# Backward-compatible alias for existing imports
ProductAdminForm = ProductForm


class ProductImageUploadForm(forms.ModelForm):
    """Upload additional images for product gallery."""
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'display_order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descriptive alt text'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'value': '0'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validate_image_file(image)
        return image


class StockAdjustmentForm(forms.Form):
    """Stock adjustment form with validation."""
    CHANGE_CHOICES = [
        ('restock', 'Restock / Inward Supply (+ units)'),
        ('adjustment', 'Inventory Correction (+ / - units)'),
        ('damaged', 'Damaged / Write-off (- units)'),
        ('dispatched', 'Customer Dispatch (- units)'),
    ]

    change_type = forms.ChoiceField(
        choices=CHANGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity_change = forms.IntegerField(
        label="Quantity Change",
        help_text="Enter positive number for additions, negative for reductions.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +10 or -3'})
    )
    notes = forms.CharField(
        label="Reason / Audit Note",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Received shipment from warehouse batch #402'})
    )

    def __init__(self, *args, current_stock=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_stock = current_stock

    def clean_quantity_change(self):
        qty = self.cleaned_data.get('quantity_change')
        if qty == 0:
            raise ValidationError("Quantity change cannot be zero.")
        new_stock = self.current_stock + qty
        if new_stock < 0:
            raise ValidationError(f"Resulting stock would be negative ({new_stock}). Maximum reduction is -{self.current_stock}.")
        return qty


class CategoryForm(forms.ModelForm):
    """Category management form."""
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'icon', 'sort_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RO Water Purifiers'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'leave blank to auto-generate'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bi-droplet-half'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EnquiryUpdateForm(forms.ModelForm):
    """Staff update form for customer product enquiries."""
    class Meta:
        model = ProductEnquiry
        fields = ['status', 'internal_notes', 'follow_up_date', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Add internal notes regarding customer phone calls, water TDS tests, or requirements...'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)


class EnquiryStatusForm(forms.ModelForm):
    """Quick inline status form for enquiries."""
    class Meta:
        model = ProductEnquiry
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }


class ServiceRequestUpdateForm(forms.ModelForm):
    """Staff update form for customer service tickets."""
    class Meta:
        model = ServiceRequest
        fields = ['status', 'technician_name', 'internal_notes', 'follow_up_date', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'technician_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assigned technician name'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Technician visit notes, parts replaced, TDS readings...'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)


class ServiceStatusForm(forms.ModelForm):
    """Quick inline status form for service tickets."""
    class Meta:
        model = ServiceRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }


class StaffUserCreateForm(forms.ModelForm):
    """Create a new staff user."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Minimum 8 characters'}),
        help_text="Provide a strong initial password."
    )
    role = forms.ChoiceField(
        choices=[('staff', 'Staff Administrator'), ('superuser', 'Superuser / Full Admin')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True
        if self.cleaned_data.get('role') == 'superuser':
            user.is_superuser = True
        else:
            user.is_superuser = False
        user.is_customer = False
        if commit:
            user.save()
        return user


class StaffUserEditForm(forms.ModelForm):
    """Edit existing staff user."""
    role = forms.ChoiceField(
        choices=[('staff', 'Staff Administrator'), ('superuser', 'Superuser / Full Admin')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['role'].initial = 'superuser' if self.instance.is_superuser else 'staff'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if self.cleaned_data.get('role') == 'superuser':
            user.is_superuser = True
        else:
            user.is_superuser = False
        if commit:
            user.save()
        return user


class SiteSettingForm(forms.ModelForm):
    """Edit global website contact and announcement settings."""
    class Meta:
        model = SiteSetting
        fields = ['website_name', 'tagline', 'support_email', 'support_phone', 'address', 'announcement_text']
        widgets = {
            'website_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'support_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'support_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'announcement_text': forms.TextInput(attrs={'class': 'form-control'}),
        }
