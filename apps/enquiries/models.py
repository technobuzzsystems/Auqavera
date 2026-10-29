import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.catalog.models import Product

class ProductEnquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
    ]

    ENQUIRY_TYPE_CHOICES = [
        ('general', 'General Enquiry'),
        ('consultation', 'Product Consultation & Water Assessment'),
        ('quote', 'Price Quote & Offers'),
        ('water_test', 'Free Home Water Test Request'),
        ('bulk', 'Commercial / Corporate Bulk Order'),
    ]

    reference_number = models.CharField(max_length=32, unique=True, editable=False, db_index=True)
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries'
    )
    enquiry_type = models.CharField(max_length=40, choices=ENQUIRY_TYPE_CHOICES, default='general')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    internal_notes = models.TextField(blank=True, help_text="Internal staff notes on customer communication")
    follow_up_date = models.DateField(null=True, blank=True, help_text="Scheduled follow-up date")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_enquiries'
    )
    consent = models.BooleanField(default=True, help_text="Customer consented to contact for enquiry")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Enquiry'
        verbose_name_plural = 'Product Enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.customer_name} ({self.get_enquiry_type_display()})"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            date_str = timezone.now().strftime('%Y%m%d')
            rand_str = uuid.uuid4().hex[:6].upper()
            self.reference_number = f"ENQ-{date_str}-{rand_str}"
        super().save(*args, **kwargs)

    @property
    def status_badge_class(self):
        badges = {
            'new': 'badge bg-primary',
            'contacted': 'badge bg-info text-dark',
            'in_progress': 'badge bg-warning text-dark',
            'converted': 'badge bg-success',
            'closed': 'badge bg-secondary',
        }
        return badges.get(self.status, 'badge bg-secondary')
