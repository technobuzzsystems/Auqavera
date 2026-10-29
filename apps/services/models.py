import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('scheduled', 'Service Scheduled'),
        ('in_progress', 'Technician Dispatched / In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    SERVICE_TYPE_CHOICES = [
        ('installation', 'New Purifier Installation'),
        ('maintenance', 'Routine Maintenance & Sanitization'),
        ('repair', 'Breakdown / Leakage Repair'),
        ('filter_replacement', 'Filter & Membrane Replacement'),
        ('other', 'Water Quality Audit / Other'),
    ]

    reference_number = models.CharField(max_length=32, unique=True, editable=False, db_index=True)
    customer_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests'
    )
    product_model = models.CharField(max_length=150, help_text="e.g. AQUAVERA Crystal Pro RO or Serial Number")
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPE_CHOICES, default='maintenance')
    preferred_date = models.DateField(help_text="Preferred technician visit date")
    issue_description = models.TextField(help_text="Description of issue, filtration behavior, or specific service needed")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    internal_notes = models.TextField(blank=True, help_text="Staff or technician field notes")
    technician_name = models.CharField(max_length=150, blank=True, help_text="Assigned field technician name")
    follow_up_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_service_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.customer_name} ({self.get_service_type_display()})"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            date_str = timezone.now().strftime('%Y%m%d')
            rand_str = uuid.uuid4().hex[:6].upper()
            self.reference_number = f"SRV-{date_str}-{rand_str}"
        super().save(*args, **kwargs)

    @property
    def status_badge_class(self):
        badges = {
            'pending': 'badge bg-warning text-dark',
            'scheduled': 'badge bg-info text-dark',
            'in_progress': 'badge bg-primary',
            'completed': 'badge bg-success',
            'cancelled': 'badge bg-secondary',
        }
        return badges.get(self.status, 'badge bg-secondary')
