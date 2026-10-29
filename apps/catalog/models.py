from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """Product category: RO, UV, UF, Gravity, Commercial, etc."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-droplet', help_text="Bootstrap icon class name, e.g. bi-droplet-half")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('catalog:product_list')}?category={self.slug}"


class Product(models.Model):
    """Water Purifier product model with full specifications and demo pricing."""
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    technology = models.CharField(max_length=150, help_text="e.g. RO + UV + UF + TDS Control")
    storage_capacity_liters = models.DecimalField(max_digits=5, decimal_places=1, help_text="Capacity in liters")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Demo selling price in INR")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Demo strike-through MRP in INR")
    image = models.ImageField(upload_to='products/', null=True, blank=True, help_text="Optional future product image. If blank, CSS placeholder is rendered.")
    image_alt_text = models.CharField(max_length=255, blank=True)
    specifications = models.JSONField(default=dict, blank=True, help_text="Key-value specifications dictionary")
    purification_stages = models.CharField(max_length=255, help_text="e.g. 7-Stage Multi-Barrier Purification")
    intended_use = models.CharField(max_length=120, default="Home / Apartment", help_text="e.g. Home, Large Family, Office / Commercial")
    maintenance_information = models.TextField(blank=True, default="Filter replacement recommended every 6-12 months based on raw water TDS levels.")
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Water Purifier Product'
        verbose_name_plural = 'Water Purifier Products'
        ordering = ['-is_featured', 'price']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['price']),
            models.Index(fields=['is_active', 'is_featured']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.image_alt_text:
            self.image_alt_text = f"AQUAVERA {self.name} Demo Placeholder"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return int(round(discount))
        return 0

    @property
    def formatted_price(self):
        return f"₹{self.price:,.0f}"

    @property
    def formatted_original_price(self):
        if self.original_price:
            return f"₹{self.original_price:,.0f}"
        return ""
