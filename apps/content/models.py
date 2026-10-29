from django.db import models

class Testimonial(models.Model):
    """Customer demo testimonial with clear demo disclaimer label."""
    display_name = models.CharField(max_length=120)
    city = models.CharField(max_length=100, default='Bengaluru')
    designation = models.CharField(max_length=120, default='Homeowner')
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_demo_content = models.BooleanField(default=True, help_text="Always True for fictional demonstration content")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.display_name} ({self.rating}★ - Demo)"


class FAQ(models.Model):
    """Frequently asked questions organized by category."""
    CATEGORY_CHOICES = [
        ('general', 'General & Brand'),
        ('technology', 'Purification Technology & RO/UV/UF'),
        ('installation', 'Installation & Sizing'),
        ('maintenance', 'Maintenance & Filter Service'),
    ]

    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='general')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.question


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber for updates and purifier maintenance tips."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class SiteSetting(models.Model):
    """Singleton site configuration for brand identity, support, and social links."""
    website_name = models.CharField(max_length=100, default="AQUAVERA")
    tagline = models.CharField(max_length=200, default="Pure Water. Thoughtfully Designed.")
    support_email = models.EmailField(default="support@aquavera.com")
    support_phone = models.CharField(max_length=50, default="+91 1800 200 4567")
    address = models.TextField(default="AQUAVERA Water Innovation Center, Sector 62, Noida, NCR 201309")
    announcement_text = models.CharField(max_length=255, default="Discover smarter, multi-stage water purification tailored for every home source.")
    social_links = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.website_name

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'website_name': 'AQUAVERA',
                'tagline': 'Pure Water. Thoughtfully Designed.',
                'support_email': 'support@aquavera.com',
                'support_phone': '+91 1800 200 4567',
                'address': 'AQUAVERA Water Innovation Center, Sector 62, Noida, NCR 201309',
                'announcement_text': 'Discover smarter, multi-stage water purification tailored for every home source.',
                'social_links': {
                    'facebook': 'https://facebook.com',
                    'instagram': 'https://instagram.com',
                    'twitter': 'https://twitter.com',
                    'linkedin': 'https://linkedin.com'
                }
            }
        )
        return obj
