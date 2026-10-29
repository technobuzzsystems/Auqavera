import re
from django import forms
from .models import ProductEnquiry
from apps.catalog.models import Product

class ProductEnquiryForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ProductEnquiry
        fields = [
            'customer_name',
            'email',
            'mobile',
            'city',
            'product',
            'enquiry_type',
            'message',
            'consent',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'required': True,
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit mobile number',
                'required': True,
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City / Location (e.g. Pune, Delhi)',
                'required': True,
            }),
            'product': forms.Select(attrs={
                'class': 'form-select',
            }),
            'enquiry_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about your requirement or water source TDS (optional)...',
                'required': True,
            }),
            'consent': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by('name')
        self.fields['product'].empty_label = "-- Select Product (Optional) --"
        self.fields['consent'].label = "I agree to receive a callback or communication regarding this enquiry."

    def clean_honeypot(self):
        val = self.cleaned_data.get('honeypot')
        if val:
            raise forms.ValidationError("Spam detected.")
        return val

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile', '').strip()
        cleaned_mobile = re.sub(r'[\s\-\(\)\+]', '', mobile)
        if len(cleaned_mobile) < 10 or not cleaned_mobile.isdigit():
            raise forms.ValidationError("Please enter a valid 10-digit mobile number.")
        return mobile
