import re
from datetime import date
from django import forms
from .models import ServiceRequest

class ServiceRequestForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ServiceRequest
        fields = [
            'customer_name',
            'mobile',
            'email',
            'city',
            'product_model',
            'service_type',
            'preferred_date',
            'issue_description',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True,
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit mobile number',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com (Optional)',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Service Location / City',
                'required': True,
            }),
            'product_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. AQUAVERA Pristine RO or Serial Number',
                'required': True,
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
            }),
            'issue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe symptoms (e.g., taste change, low water flow, beeping alarm, routine filter change)...',
                'required': True,
            }),
        }

    def clean_honeypot(self):
        val = self.cleaned_data.get('honeypot')
        if val:
            raise forms.ValidationError("Spam detected.")
        return val

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile', '').strip()
        cleaned_mobile = re.sub(r'[\s\-\(\)\+]', '', mobile)
        if len(cleaned_mobile) < 10 or not cleaned_mobile.isdigit():
            raise forms.ValidationError("Please provide a valid 10-digit mobile number.")
        return mobile

    def clean_preferred_date(self):
        pref_date = self.cleaned_data.get('preferred_date')
        if pref_date and pref_date < date.today():
            raise forms.ValidationError("Preferred service date cannot be in the past.")
        return pref_date
