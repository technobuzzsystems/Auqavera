import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction, models
from django.db.models import Q, F, Sum, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import Product, Category, ProductImage, StockAdjustment
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest
from django.core.exceptions import ValidationError
from apps.content.models import SiteSetting
from .forms import (
    AdminLoginForm,
    ProductForm,
    ProductImageUploadForm,
    validate_image_file,
    StockAdjustmentForm,
    CategoryForm,
    EnquiryUpdateForm,
    EnquiryStatusForm,
    ServiceRequestUpdateForm,
    ServiceStatusForm,
    StaffUserCreateForm,
    StaffUserEditForm,
    SiteSettingForm,
)

User = get_user_model()


def staff_required(view_func):
    """Ensure user is logged in and marked as staff or superuser."""
    def check_user(user):
        return user.is_authenticated and user.is_staff
    decorated = user_passes_test(check_user, login_url='dashboard:login')
    return decorated(view_func)


# ==========================================
# AUTHENTICATION
# ==========================================

def admin_login_view(request):
    """Dedicated administrative login portal."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')

    redirect_to = request.GET.get('next', 'dashboard:home')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # Support login by username or email
            user = authenticate(request, username=username_or_email, password=password)
            if user is None and '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    user = None

            if user is not None:
                if user.is_active and user.is_staff:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                    return redirect(redirect_to)
                elif not user.is_staff:
                    messages.error(request, "Access denied. Administrative staff credentials are required.")
                else:
                    messages.error(request, "Your administrative account is currently inactive. Contact your administrator.")
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = AdminLoginForm()

    return render(request, 'dashboard/login.html', {'form': form, 'next': redirect_to})


def admin_logout_view(request):
    """Secure administrative logout."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out securely.")
    return redirect('dashboard:login')


# ==========================================
# DASHBOARD OVERVIEW
# ==========================================

@staff_required
def dashboard_home(request):
    """Executive administrative overview with KPIs and live metrics."""
    # Product & Inventory KPIs
    total_products = Product.objects.count()
    published_products = Product.objects.filter(status='published').count()
    draft_products = Product.objects.filter(status='draft').count()
    archived_products = Product.objects.filter(status='archived').count()

    # Stock metrics
    low_stock_products = Product.objects.filter(
        stock_quantity__gt=0,
        stock_quantity__lte=F('low_stock_threshold')
    ).count()
    out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
    healthy_stock_products = Product.objects.filter(stock_quantity__gt=F('low_stock_threshold')).count()
    total_inventory_units = Product.objects.aggregate(total=Sum('stock_quantity'))['total'] or 0

    # Enquiry & Service KPIs
    total_enquiries = ProductEnquiry.objects.count()
    new_enquiries = ProductEnquiry.objects.filter(status='new').count()
    total_services = ServiceRequest.objects.count()
    pending_services = ServiceRequest.objects.filter(status='pending').count()

    # Category distribution
    categories_stat = Category.objects.annotate(product_count=Count('products')).values('name', 'product_count')
    category_labels = [c['name'] for c in categories_stat]
    category_data = [c['product_count'] for c in categories_stat]

    # Query Status distribution
    enquiry_status_counts = ProductEnquiry.objects.values('status').annotate(count=Count('id'))
    status_dict = {item['status']: item['count'] for item in enquiry_status_counts}

    # Recent lists
    recent_products = Product.objects.select_related('category').order_by('-created_at')[:5]
    recent_enquiries = ProductEnquiry.objects.select_related('product').order_by('-created_at')[:6]
    recent_services = ServiceRequest.objects.order_by('-created_at')[:5]
    recent_stock_adjustments = StockAdjustment.objects.select_related('product', 'created_by').order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'published_products': published_products,
        'draft_products': draft_products,
        'archived_products': archived_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'healthy_stock_products': healthy_stock_products,
        'total_inventory_units': total_inventory_units,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        'total_services': total_services,
        'pending_services': pending_services,
        'category_labels_json': json.dumps(category_labels),
        'category_data_json': json.dumps(category_data),
        'stock_labels_json': json.dumps(['Healthy Stock', 'Low Stock', 'Out of Stock']),
        'stock_data_json': json.dumps([healthy_stock_products, low_stock_products, out_of_stock_products]),
        'query_labels_json': json.dumps(['New', 'In Progress', 'Contacted', 'Converted', 'Closed']),
        'query_data_json': json.dumps([
            status_dict.get('new', 0),
            status_dict.get('in_progress', 0),
            status_dict.get('contacted', 0),
            status_dict.get('converted', 0),
            status_dict.get('closed', 0),
        ]),
        'recent_products': recent_products,
        'recent_enquiries': recent_enquiries,
        'recent_services': recent_services,
        'recent_stock_adjustments': recent_stock_adjustments,
    }
    return render(request, 'dashboard/index.html', context)


# ==========================================
# PRODUCT MANAGEMENT (FULL CRUD)
# ==========================================

@staff_required
def dashboard_products(request):
    """List, search, filter, and paginate products."""
    queryset = Product.objects.select_related('category').prefetch_related('images')

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(technology__icontains=q) |
            Q(short_description__icontains=q)
        )

    # Category filter
    category_id = request.GET.get('category', '').strip()
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Status filter
    status = request.GET.get('status', '').strip()
    if status:
        queryset = queryset.filter(status=status)

    # Stock filter
    stock_status = request.GET.get('stock', '').strip()
    if stock_status == 'out':
        queryset = queryset.filter(stock_quantity=0)
    elif stock_status == 'low':
        queryset = queryset.filter(stock_quantity__gt=0, stock_quantity__lte=F('low_stock_threshold'))
    elif stock_status == 'in':
        queryset = queryset.filter(stock_quantity__gt=F('low_stock_threshold'))

    # Sorting
    sort = request.GET.get('sort', '-created_at').strip()
    sort_options = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'name_asc': 'name',
        'name_desc': '-name',
        'price_asc': 'price',
        'price_desc': '-price',
        'stock_asc': 'stock_quantity',
        'stock_desc': '-stock_quantity',
    }
    queryset = queryset.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'current_q': q,
        'current_category': category_id,
        'current_status': status,
        'current_stock': stock_status,
        'current_sort': sort,
        'total_count': paginator.count,
    }
    return render(request, 'dashboard/products.html', context)


@staff_required
def dashboard_product_create(request):
    """Add a new product with specifications and multiple image upload support."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        new_images = request.FILES.getlist('new_images')
        primary_choice = request.POST.get('primary_image_choice', '')

        # Validate new images
        image_errors = []
        for f in new_images:
            try:
                validate_image_file(f)
            except ValidationError as e:
                image_errors.append(f"{f.name}: {e.message}")

        if image_errors:
            for err in image_errors:
                messages.error(request, err)

        if form.is_valid() and not image_errors:
            with transaction.atomic():
                product = form.save()
                # Create initial stock adjustment log if stock > 0
                if product.stock_quantity > 0:
                    StockAdjustment.objects.create(
                        product=product,
                        change_type='restock',
                        quantity_change=product.stock_quantity,
                        previous_stock=0,
                        new_stock=product.stock_quantity,
                        notes='Initial inventory stock recorded during product creation.',
                        created_by=request.user
                    )

                # Process multiple uploaded images
                created_images = []
                for idx, img_file in enumerate(new_images):
                    alt_text = request.POST.get(f'new_image_alt_{idx}', '').strip() or product.name
                    is_prim = (primary_choice == f'new_{idx}') or (not primary_choice and idx == 0 and not product.image)
                    img_obj = ProductImage.objects.create(
                        product=product,
                        image=img_file,
                        alt_text=alt_text,
                        is_primary=is_prim,
                        display_order=idx
                    )
                    created_images.append(img_obj)

                # If legacy single image was uploaded and no new_images were selected, register it
                if product.image and not created_images:
                    ProductImage.objects.create(
                        product=product,
                        image=product.image,
                        alt_text=product.image_alt_text or product.name,
                        is_primary=True,
                        display_order=0
                    )

                # Synchronize product.image with the primary gallery image
                prim = ProductImage.objects.filter(product=product, is_primary=True).first()
                if not prim and ProductImage.objects.filter(product=product).exists():
                    prim = ProductImage.objects.filter(product=product).first()
                    ProductImage.objects.filter(id=prim.id).update(is_primary=True)
                if prim:
                    Product.objects.filter(pk=product.pk).update(image=prim.image)
                    product.image = prim.image

            messages.success(request, f"Product '{product.name}' was created successfully (SKU: {product.sku})!")
            return redirect('dashboard:products')
        else:
            if not image_errors:
                messages.error(request, "Failed to create product. Please correct the highlighted errors.")
    else:
        form = ProductForm(initial={'status': 'published', 'stock_quantity': 15, 'low_stock_threshold': 5})

    return render(request, 'dashboard/product_form.html', {
        'form': form,
        'title': 'Add New Water Purifier',
        'button_label': 'Create Product',
    })


@staff_required
def dashboard_product_edit(request, pk):
    """Edit existing product details and manage its images."""
    product = get_object_or_404(Product, pk=pk)
    old_stock = product.stock_quantity

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        new_images = request.FILES.getlist('new_images')
        primary_choice = request.POST.get('primary_image_choice', '')
        delete_image_ids = request.POST.getlist('delete_image_ids')

        # Validate new images
        image_errors = []
        for f in new_images:
            try:
                validate_image_file(f)
            except ValidationError as e:
                image_errors.append(f"{f.name}: {e.message}")

        if image_errors:
            for err in image_errors:
                messages.error(request, err)

        if form.is_valid() and not image_errors:
            with transaction.atomic():
                updated_product = form.save()
                # If stock was changed via product form, log the adjustment
                if updated_product.stock_quantity != old_stock:
                    qty_diff = updated_product.stock_quantity - old_stock
                    StockAdjustment.objects.create(
                        product=updated_product,
                        change_type='adjustment',
                        quantity_change=qty_diff,
                        previous_stock=old_stock,
                        new_stock=updated_product.stock_quantity,
                        notes='Stock updated via product edit form.',
                        created_by=request.user
                    )

                # Parse delete IDs safely as integers
                delete_ids_set = set()
                if delete_image_ids:
                    for d_id in delete_image_ids:
                        try:
                            delete_ids_set.add(int(d_id))
                        except (ValueError, TypeError):
                            pass

                # 1. Delete requested images from database
                if delete_ids_set:
                    ProductImage.objects.filter(product=updated_product, id__in=delete_ids_set).delete()

                # Clear prefetched cache on product so relation queries are always fresh
                if hasattr(updated_product, '_prefetched_objects_cache'):
                    updated_product._prefetched_objects_cache.clear()

                # 2. Update alt texts for existing remaining images
                remaining_images = ProductImage.objects.filter(product=updated_product).exclude(id__in=delete_ids_set)
                for existing_img in remaining_images:
                    alt_val = request.POST.get(f'existing_alt_{existing_img.id}')
                    if alt_val is not None:
                        trimmed_alt = alt_val.strip()
                        if existing_img.alt_text != trimmed_alt:
                            ProductImage.objects.filter(id=existing_img.id).update(alt_text=trimmed_alt)

                # 3. Create newly uploaded images
                max_order = (ProductImage.objects.filter(product=updated_product).aggregate(m=models.Max('display_order'))['m'] or 0)
                for idx, img_file in enumerate(new_images):
                    alt_text = request.POST.get(f'new_image_alt_{idx}', '').strip() or updated_product.name
                    is_prim = (primary_choice == f'new_{idx}')
                    ProductImage.objects.create(
                        product=updated_product,
                        image=img_file,
                        alt_text=alt_text,
                        is_primary=is_prim,
                        display_order=max_order + idx + 1
                    )

                # 4. Handle primary choice on existing images
                if primary_choice.startswith('existing_'):
                    try:
                        chosen_id = int(primary_choice.replace('existing_', ''))
                        if chosen_id not in delete_ids_set:
                            ProductImage.objects.filter(product=updated_product).exclude(id=chosen_id).update(is_primary=False)
                            ProductImage.objects.filter(product=updated_product, id=chosen_id).update(is_primary=True)
                    except (ValueError, TypeError):
                        pass
                elif primary_choice.startswith('new_'):
                    new_prim_idx = None
                    try:
                        new_prim_idx = int(primary_choice.replace('new_', ''))
                    except (ValueError, TypeError):
                        pass
                    if new_prim_idx is not None:
                        ProductImage.objects.filter(product=updated_product).exclude(
                            id__in=[img.id for img in ProductImage.objects.filter(product=updated_product, is_primary=True)]
                        ).update(is_primary=False)

                # 5. Ensure exactly one image is primary if images exist
                remaining_qs = ProductImage.objects.filter(product=updated_product)
                if remaining_qs.exists():
                    if not remaining_qs.filter(is_primary=True).exists():
                        first_img = remaining_qs.order_by('display_order', 'id').first()
                        if first_img:
                            ProductImage.objects.filter(id=first_img.id).update(is_primary=True)

                # 6. Synchronize product.image with primary ProductImage
                prim = ProductImage.objects.filter(product=updated_product, is_primary=True).first()
                if prim:
                    Product.objects.filter(pk=updated_product.pk).update(image=prim.image)
                    updated_product.image = prim.image
                elif not ProductImage.objects.filter(product=updated_product).exists():
                    if not request.FILES.get('image'):
                        Product.objects.filter(pk=updated_product.pk).update(image=None)
                        updated_product.image = None

                # Invalidate in-memory cache
                if hasattr(updated_product, '_prefetched_objects_cache'):
                    updated_product._prefetched_objects_cache.clear()

            messages.success(request, f"Product '{updated_product.name}' updated successfully!")
            return redirect('dashboard:products')
        else:
            if not image_errors:
                messages.error(request, "Failed to update product. Please correct errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/product_form.html', {
        'form': form,
        'product': product,
        'existing_images': ProductImage.objects.filter(product=product).order_by('-is_primary', 'display_order', 'id'),
        'title': f'Edit Product: {product.name}',
        'button_label': 'Save Changes',
    })


@staff_required
def dashboard_product_detail(request, pk):
    """Staff preview and audit summary of an individual product."""
    product = get_object_or_404(Product.objects.select_related('category').prefetch_related('images'), pk=pk)
    stock_history = product.stock_adjustments.select_related('created_by').order_by('-created_at')[:10]
    recent_enquiries = product.enquiries.order_by('-created_at')[:5]

    return render(request, 'dashboard/product_detail.html', {
        'product': product,
        'stock_history': stock_history,
        'recent_enquiries': recent_enquiries,
    })


@staff_required
def dashboard_product_toggle_status(request, pk):
    """Toggle product publication status between Published and Draft."""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        if product.status == 'published':
            product.status = 'draft'
            messages.info(request, f"Product '{product.name}' was unpublished and set to Draft.")
        else:
            product.status = 'published'
            messages.success(request, f"Product '{product.name}' was published to the public catalogue!")
        product.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:products'))


@staff_required
def dashboard_product_toggle_featured(request, pk):
    """Toggle whether product is featured on the homepage."""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.is_featured = not product.is_featured
        product.save(update_fields=['is_featured', 'updated_at'])
        state = "marked as Featured on the homepage" if product.is_featured else "removed from homepage Featured section"
        messages.success(request, f"Product '{product.name}' was {state}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:products'))


@staff_required
def dashboard_product_delete(request, pk):
    """Safe archival or deletion of a product."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action', 'archive')
        if action == 'delete':
            try:
                name = product.name
                product.delete()
                messages.success(request, f"Product '{name}' was permanently deleted.")
                return redirect('dashboard:products')
            except models.ProtectedError:
                messages.error(request, "Cannot delete product because it has linked customer enquiries or service tickets. Product was archived instead.")
                product.status = 'archived'
                product.save()
                return redirect('dashboard:products')
        else:
            # Archival
            product.status = 'archived'
            product.save()
            messages.success(request, f"Product '{product.name}' was archived and hidden from public catalogue.")
            return redirect('dashboard:products')

    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


# ==========================================
# MULTIPLE PRODUCT IMAGE MANAGEMENT
# ==========================================

@staff_required
def dashboard_product_images(request, pk):
    """Manage multiple gallery images for a product."""
    product = get_object_or_404(Product, pk=pk)
    images = product.images.all().order_by('-is_primary', 'display_order', 'id')

    if request.method == 'POST':
        form = ProductImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.product = product
            # If this is the only image, automatically make it primary
            if not images.exists():
                new_image.is_primary = True
            new_image.save()
            if new_image.is_primary:
                Product.objects.filter(pk=product.pk).update(image=new_image.image)
                product.image = new_image.image
            messages.success(request, "Product image uploaded successfully!")
            return redirect('dashboard:product_images', pk=product.pk)
        else:
            messages.error(request, "Failed to upload image. Please verify file format and size.")
    else:
        form = ProductImageUploadForm()

    return render(request, 'dashboard/product_images.html', {
        'product': product,
        'images': images,
        'form': form,
    })


@staff_required
def dashboard_image_set_primary(request, image_id):
    """Set an image as the primary featured image for its product."""
    if request.method == 'POST':
        image = get_object_or_404(ProductImage, id=image_id)
        product = image.product
        with transaction.atomic():
            ProductImage.objects.filter(product=product).update(is_primary=False)
            ProductImage.objects.filter(id=image.id).update(is_primary=True)
            Product.objects.filter(pk=product.pk).update(image=image.image)
            product.image = image.image
        messages.success(request, "Primary featured image updated.")
        return redirect('dashboard:product_images', pk=product.pk)
    return redirect('dashboard:products')


@staff_required
def dashboard_image_delete(request, image_id):
    """Remove a product image."""
    if request.method == 'POST':
        image = get_object_or_404(ProductImage, id=image_id)
        product = image.product
        was_primary = image.is_primary
        image.delete()

        # If deleted image was primary, designate the first remaining image as primary
        if was_primary:
            next_primary = ProductImage.objects.filter(product=product).first()
            if next_primary:
                ProductImage.objects.filter(id=next_primary.id).update(is_primary=True)
                Product.objects.filter(pk=product.pk).update(image=next_primary.image)
            else:
                Product.objects.filter(pk=product.pk).update(image=None)

        messages.success(request, "Product image removed.")
        return redirect('dashboard:product_images', pk=product.pk)
    return redirect('dashboard:products')


# ==========================================
# INVENTORY MANAGEMENT
# ==========================================

@staff_required
def dashboard_inventory(request):
    """Inventory overview and stock adjustment workspace."""
    queryset = Product.objects.select_related('category').order_by('stock_quantity', 'name')

    # Stock status filter
    stock_filter = request.GET.get('stock', '').strip()
    if stock_filter == 'out':
        queryset = queryset.filter(stock_quantity=0)
    elif stock_filter == 'low':
        queryset = queryset.filter(stock_quantity__gt=0, stock_quantity__lte=F('low_stock_threshold'))
    elif stock_filter == 'healthy':
        queryset = queryset.filter(stock_quantity__gt=F('low_stock_threshold'))

    # Category filter
    category_id = request.GET.get('category', '').strip()
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(sku__icontains=q))

    # Stats
    total_units = Product.objects.aggregate(total=Sum('stock_quantity'))['total'] or 0
    low_stock_count = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=F('low_stock_threshold')).count()
    out_of_stock_count = Product.objects.filter(stock_quantity=0).count()
    healthy_count = Product.objects.filter(stock_quantity__gt=F('low_stock_threshold')).count()

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'total_units': total_units,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'healthy_count': healthy_count,
        'current_stock': stock_filter,
        'current_category': category_id,
        'current_q': q,
    }
    return render(request, 'dashboard/inventory.html', context)


@staff_required
def dashboard_inventory_adjust(request, product_id):
    """Adjust stock quantity with audit logging and non-negative constraints."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST, current_stock=product.stock_quantity)
        if form.is_valid():
            change_type = form.cleaned_data['change_type']
            qty_change = form.cleaned_data['quantity_change']
            notes = form.cleaned_data['notes']

            with transaction.atomic():
                prev_stock = product.stock_quantity
                new_stock = prev_stock + qty_change

                if new_stock < 0:
                    messages.error(request, "Stock cannot be negative.")
                    return redirect('dashboard:inventory')

                product.stock_quantity = new_stock
                product.save(update_fields=['stock_quantity', 'updated_at'])

                StockAdjustment.objects.create(
                    product=product,
                    change_type=change_type,
                    quantity_change=qty_change,
                    previous_stock=prev_stock,
                    new_stock=new_stock,
                    notes=notes,
                    created_by=request.user
                )

            messages.success(request, f"Stock for '{product.name}' updated from {prev_stock} to {new_stock} units ({qty_change:+d}).")
            return redirect('dashboard:inventory')
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{err}")
    return redirect('dashboard:inventory')


@staff_required
def dashboard_inventory_history(request):
    """Audit log of stock movements."""
    queryset = StockAdjustment.objects.select_related('product', 'created_by').order_by('-created_at')

    product_id = request.GET.get('product', '').strip()
    if product_id:
        queryset = queryset.filter(product_id=product_id)

    change_type = request.GET.get('type', '').strip()
    if change_type:
        queryset = queryset.filter(change_type=change_type)

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    products = Product.objects.all().order_by('name')

    return render(request, 'dashboard/inventory_history.html', {
        'page_obj': page_obj,
        'adjustments': page_obj.object_list,
        'products': products,
        'current_product': product_id,
        'current_type': change_type,
    })


# ==========================================
# CUSTOMER QUERIES AND ENQUIRIES
# ==========================================

@staff_required
def dashboard_enquiries(request):
    """List and filter customer enquiries."""
    queryset = ProductEnquiry.objects.select_related('product', 'user', 'assigned_to').order_by('-created_at')

    # Filters
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    enquiry_type = request.GET.get('type', '').strip()
    if enquiry_type:
        queryset = queryset.filter(enquiry_type=enquiry_type)

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(customer_name__icontains=q) |
            Q(email__icontains=q) |
            Q(mobile__icontains=q) |
            Q(reference_number__icontains=q) |
            Q(city__icontains=q)
        )

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/enquiries.html', {
        'page_obj': page_obj,
        'enquiries': page_obj.object_list,
        'current_status': status_filter,
        'current_type': enquiry_type,
        'current_q': q,
        'status_choices': ProductEnquiry.STATUS_CHOICES,
        'type_choices': ProductEnquiry.ENQUIRY_TYPE_CHOICES,
        'new_count': ProductEnquiry.objects.filter(status='new').count(),
    })


@staff_required
def dashboard_enquiry_detail(request, pk):
    """View full customer enquiry details and update staff notes."""
    enquiry = get_object_or_404(ProductEnquiry.objects.select_related('product', 'user', 'assigned_to'), pk=pk)

    if request.method == 'POST':
        form = EnquiryUpdateForm(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            messages.success(request, f"Enquiry #{enquiry.reference_number} updated successfully.")
            return redirect('dashboard:enquiry_detail', pk=enquiry.pk)
    else:
        form = EnquiryUpdateForm(instance=enquiry)

    return render(request, 'dashboard/enquiry_detail.html', {
        'enquiry': enquiry,
        'form': form,
    })


@staff_required
def dashboard_enquiry_update_status(request, pk):
    """Quick update enquiry status."""
    enquiry = get_object_or_404(ProductEnquiry, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ProductEnquiry.STATUS_CHOICES):
            enquiry.status = new_status
            enquiry.save(update_fields=['status', 'updated_at'])
            messages.success(request, f"Enquiry #{enquiry.reference_number} marked as {enquiry.get_status_display()}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:enquiries'))


# ==========================================
# SERVICE REQUESTS
# ==========================================

@staff_required
def dashboard_service_requests(request):
    """Staff management for service tickets."""
    queryset = ServiceRequest.objects.select_related('user', 'assigned_to').order_by('-created_at')

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    service_type = request.GET.get('type', '').strip()
    if service_type:
        queryset = queryset.filter(service_type=service_type)

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(customer_name__icontains=q) |
            Q(mobile__icontains=q) |
            Q(reference_number__icontains=q) |
            Q(product_model__icontains=q) |
            Q(city__icontains=q)
        )

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/service_requests.html', {
        'page_obj': page_obj,
        'services': page_obj.object_list,
        'current_status': status_filter,
        'current_type': service_type,
        'current_q': q,
        'status_choices': ServiceRequest.STATUS_CHOICES,
        'service_type_choices': ServiceRequest.SERVICE_TYPE_CHOICES,
        'pending_count': ServiceRequest.objects.filter(status='pending').count(),
    })


@staff_required
def dashboard_service_detail(request, pk):
    """View and update service ticket details."""
    service_req = get_object_or_404(ServiceRequest.objects.select_related('user', 'assigned_to'), pk=pk)

    if request.method == 'POST':
        form = ServiceRequestUpdateForm(request.POST, instance=service_req)
        if form.is_valid():
            form.save()
            messages.success(request, f"Service Request #{service_req.reference_number} updated successfully.")
            return redirect('dashboard:service_detail', pk=service_req.pk)
    else:
        form = ServiceRequestUpdateForm(instance=service_req)

    return render(request, 'dashboard/service_detail.html', {
        'service_req': service_req,
        'form': form,
    })


@staff_required
def dashboard_service_update_status(request, pk):
    """Quick update service ticket status."""
    service_req = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ServiceRequest.STATUS_CHOICES):
            service_req.status = new_status
            service_req.save(update_fields=['status', 'updated_at'])
            messages.success(request, f"Service Request #{service_req.reference_number} updated to {service_req.get_status_display()}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:service_requests'))


# ==========================================
# CATEGORIES MANAGEMENT
# ==========================================

@staff_required
def dashboard_categories(request):
    """Manage product categories."""
    categories = Category.objects.annotate(product_count=Count('products')).order_by('sort_order', 'name')
    return render(request, 'dashboard/categories.html', {'categories': categories})


@staff_required
def dashboard_category_create(request):
    """Add a new product category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created successfully!")
            return redirect('dashboard:categories')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_required
def dashboard_category_edit(request, pk):
    """Edit existing category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully!")
            return redirect('dashboard:categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {'form': form, 'category': category, 'title': f'Edit Category: {category.name}'})


@staff_required
def dashboard_category_delete(request, pk):
    """Delete or deactivate category safely."""
    category = get_object_or_404(Category, pk=pk)
    product_count = category.products.count()

    if request.method == 'POST':
        if product_count > 0:
            category.is_active = False
            category.save(update_fields=['is_active'])
            messages.warning(request, f"Category '{category.name}' contains {product_count} products and was deactivated instead of deleted.")
        else:
            category.delete()
            messages.success(request, f"Category '{category.name}' was deleted.")
        return redirect('dashboard:categories')

    return render(request, 'dashboard/category_confirm_delete.html', {'category': category, 'product_count': product_count})


# ==========================================
# STAFF USER MANAGEMENT
# ==========================================

@staff_required
def dashboard_users(request):
    """List staff and administrator accounts."""
    staff_users = User.objects.filter(is_staff=True).order_by('-is_superuser', 'username')
    return render(request, 'dashboard/users.html', {'staff_users': staff_users})


@staff_required
def dashboard_user_create(request):
    """Create a new staff user."""
    if not request.user.is_superuser:
        messages.error(request, "Only superusers can create staff members.")
        return redirect('dashboard:users')

    if request.method == 'POST':
        form = StaffUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Staff user '{user.username}' created successfully.")
            return redirect('dashboard:users')
    else:
        form = StaffUserCreateForm()
    return render(request, 'dashboard/user_form.html', {'form': form, 'title': 'Create Staff Account'})


@staff_required
def dashboard_user_edit(request, pk):
    """Edit staff user permissions and details."""
    user_to_edit = get_object_or_404(User, pk=pk, is_staff=True)

    if not request.user.is_superuser and request.user != user_to_edit:
        messages.error(request, "Permission denied.")
        return redirect('dashboard:users')

    if request.method == 'POST':
        form = StaffUserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            # Prevent user from revoking their own superuser or staff status
            if request.user == user_to_edit and not form.cleaned_data['is_active']:
                messages.error(request, "You cannot deactivate your own account.")
                return redirect('dashboard:users')
            form.save()
            messages.success(request, f"User '{user_to_edit.username}' updated.")
            return redirect('dashboard:users')
    else:
        form = StaffUserEditForm(instance=user_to_edit)

    return render(request, 'dashboard/user_form.html', {'form': form, 'user_obj': user_to_edit, 'title': f'Edit Staff: {user_to_edit.username}'})


@staff_required
def dashboard_user_toggle_active(request, pk):
    """Activate or deactivate staff user."""
    if request.method == 'POST':
        if not request.user.is_superuser:
            messages.error(request, "Only superusers can toggle staff status.")
            return redirect('dashboard:users')

        user_obj = get_object_or_404(User, pk=pk, is_staff=True)
        if user_obj == request.user:
            messages.error(request, "You cannot deactivate your own administrative account.")
            return redirect('dashboard:users')

        user_obj.is_active = not user_obj.is_active
        user_obj.save(update_fields=['is_active'])
        state = "activated" if user_obj.is_active else "deactivated"
        messages.info(request, f"Account '{user_obj.username}' was {state}.")
    return redirect('dashboard:users')


# ==========================================
# WEBSITE CONTENT & SITE SETTINGS
# ==========================================

@staff_required
def dashboard_site_settings(request):
    """Manage global website contact and announcement settings."""
    site_setting = SiteSetting.load()

    if request.method == 'POST':
        form = SiteSettingForm(request.POST, instance=site_setting)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings updated successfully. Changes are now visible across the website.")
            return redirect('dashboard:site_settings')
    else:
        form = SiteSettingForm(instance=site_setting)

    return render(request, 'dashboard/site_settings.html', {'form': form, 'site_setting': site_setting})
