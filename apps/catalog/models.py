import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


def product_main_image_upload_path(instance, filename):
    return f"products/{filename}"


def product_gallery_upload_path(instance, filename):
    return f"products/gallery/{filename}"


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
    STATUS_CHOICES = [
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    sku = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    brand = models.CharField(max_length=100, default='AQUAVERA')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    technology = models.CharField(max_length=150, help_text="e.g. RO + UV + UF + TDS Control")
    storage_capacity_liters = models.DecimalField(max_digits=5, decimal_places=1, help_text="Capacity in liters")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price in INR")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Strike-through MRP in INR")
    image = models.ImageField(upload_to=product_main_image_upload_path, max_length=255, null=True, blank=True, help_text="Optional future product image. If blank, CSS placeholder is rendered.")
    image_alt_text = models.CharField(max_length=255, blank=True)
    specifications = models.JSONField(default=dict, blank=True, help_text="Key-value specifications dictionary")
    features = models.JSONField(default=list, blank=True, help_text="List of feature highlights")
    purification_stages = models.CharField(max_length=255, help_text="e.g. 7-Stage Multi-Barrier Purification")
    intended_use = models.CharField(max_length=120, default="Home / Apartment", help_text="e.g. Home, Large Family, Office / Commercial")
    warranty_info = models.CharField(max_length=150, default="1 Year Comprehensive Manufacturer Warranty", blank=True)
    maintenance_information = models.TextField(blank=True, default="Filter replacement recommended every 6-12 months based on raw water TDS levels.")
    
    # Inventory fields
    stock_quantity = models.PositiveIntegerField(default=15, help_text="Available stock units")
    low_stock_threshold = models.PositiveIntegerField(default=5, help_text="Alert threshold for low inventory")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', db_index=True)

    # Source / Import metadata
    source_name = models.CharField(max_length=150, blank=True, default='Official KENT India', help_text="Data source origin reference")
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Original manufacturer / source product URL")
    raw_specifications = models.TextField(blank=True, help_text="Unprocessed official technical specification string")
    manufacturer_availability = models.CharField(max_length=50, blank=True, default='In Stock', help_text="Manufacturer website stock status (e.g. In Stock, Sold Out)")
    import_status = models.CharField(
        max_length=30,
        choices=[
            ('imported', 'Imported'),
            ('pending_review', 'Pending Review'),
            ('verified', 'Verified'),
            ('published', 'Published'),
            ('import_failed', 'Import Failed'),
        ],
        default='verified',
        db_index=True
    )
    last_imported_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when product data was last imported")

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
            models.Index(fields=['status']),
            models.Index(fields=['stock_quantity']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            base_sku = slugify(self.name).upper()[:10]
            rand_code = uuid.uuid4().hex[:4].upper()
            self.sku = f"AQV-{base_sku}-{rand_code}"
        if not self.image_alt_text:
            self.image_alt_text = f"AQUAVERA {self.name}"
        # Synchronize is_active with status
        self.is_active = (self.status == 'published')
        if kwargs.get('update_fields') is not None:
            update_fields = set(kwargs['update_fields'])
            if 'status' in update_fields:
                update_fields.add('is_active')
            kwargs['update_fields'] = update_fields
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

    @property
    def is_out_of_stock(self):
        return self.stock_quantity == 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def stock_badge_class(self):
        if self.stock_quantity == 0:
            return "badge bg-danger"
        elif self.stock_quantity <= self.low_stock_threshold:
            return "badge bg-warning text-dark"
        return "badge bg-success"

    @property
    def stock_status_display(self):
        if self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity <= self.low_stock_threshold:
            return f"Low Stock ({self.stock_quantity} left)"
        return f"In Stock ({self.stock_quantity} units)"

    @property
    def primary_image(self):
        """Returns the primary image from related ProductImage objects, or fallback to first image."""
        if hasattr(self, '_prefetched_objects_cache') and 'images' in self._prefetched_objects_cache:
            imgs = self.images.all()
            for img in imgs:
                if img.is_primary:
                    return img
            return imgs[0] if imgs else None
        primary = self.images.filter(is_primary=True).first()
        if not primary:
            primary = self.images.first()
        return primary

    @property
    def display_image_url(self):
        """Returns the URL of the primary image, or fallback to product.image, or None."""
        prim = self.primary_image
        if prim and prim.image:
            try:
                return prim.image.url
            except ValueError:
                pass
        if self.image:
            try:
                return self.image.url
            except ValueError:
                pass
        return None

    @property
    def display_image_alt(self):
        """Returns the alt text of the primary image or product name."""
        prim = self.primary_image
        if prim and prim.alt_text:
            return prim.alt_text
        if self.image_alt_text:
            return self.image_alt_text
        return self.name

    @property
    def is_kent_product(self):
        """Returns True if the purifier is branded KENT or has KENT in the name."""
        return bool((self.brand and self.brand.upper() == 'KENT') or ('KENT' in self.name.upper()))



class ProductImage(models.Model):
    """Multiple images for a water purifier product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_gallery_upload_path, max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['-is_primary', 'display_order', 'id']

    def __str__(self):
        return f"Image for {self.product.name} ({'Primary' if self.is_primary else 'Gallery'})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one image is primary for this product
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class StockAdjustment(models.Model):
    """Audit log of inventory stock adjustments."""
    CHANGE_TYPES = [
        ('restock', 'Restock / Inward Supply'),
        ('adjustment', 'Manual Inventory Correction'),
        ('damaged', 'Damaged / Write-off'),
        ('dispatched', 'Customer Dispatch / Order'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_adjustments')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES, default='adjustment')
    quantity_change = models.IntegerField(help_text="Positive for additions, negative for reductions")
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stock Adjustment'
        verbose_name_plural = 'Stock Adjustments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name}: {self.quantity_change:+d} units ({self.get_change_type_display()})"
