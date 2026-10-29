from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category
from apps.content.models import FAQ
from apps.enquiries.forms import ProductEnquiryForm

def product_list(request):
    """
    Dedicated /products/ catalogue page with:
    - Search by product name or description
    - Category filter
    - Technology filter
    - Price range filter
    - Capacity filter
    - Sorting (price low-high, high-low, alphabetical, featured)
    - Pagination
    - Active product count
    """
    queryset = Product.objects.filter(is_active=True).select_related('category')
    
    # Search query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(short_description__icontains=q) |
            Q(technology__icontains=q) |
            Q(description__icontains=q)
        )

    # Category filter
    category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
        selected_category = Category.objects.filter(slug=category_slug, is_active=True).first()

    # Technology filter
    tech_filter = request.GET.get('tech', '').strip()
    if tech_filter:
        queryset = queryset.filter(technology__icontains=tech_filter)

    # Capacity filter
    capacity = request.GET.get('capacity', '').strip()
    if capacity == 'under_7':
        queryset = queryset.filter(storage_capacity_liters__lt=7)
    elif capacity == '7_to_10':
        queryset = queryset.filter(storage_capacity_liters__gte=7, storage_capacity_liters__lte=10)
    elif capacity == 'over_10':
        queryset = queryset.filter(storage_capacity_liters__gt=10)

    # Price range filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price.isdigit():
        queryset = queryset.filter(price__gte=int(min_price))
    if max_price.isdigit():
        queryset = queryset.filter(price__lte=int(max_price))

    # Sorting
    sort = request.GET.get('sort', 'featured').strip()
    if sort == 'price_low':
        queryset = queryset.order_by('price')
    elif sort == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort == 'alpha':
        queryset = queryset.order_by('name')
    else:  # featured / default
        queryset = queryset.order_by('-is_featured', 'price')

    total_count = queryset.count()

    # Pagination: 6 products per page
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # All active categories for filter sidebar
    categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')

    # Available distinct technologies for filtering
    available_technologies = [
        'RO + UV + UF + TDS Control',
        'RO + UV',
        'UV + UF',
        'Gravity UF',
        'Commercial RO',
    ]

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_count': total_count,
        'categories': categories,
        'selected_category': selected_category,
        'current_q': q,
        'current_category': category_slug,
        'current_tech': tech_filter,
        'current_capacity': capacity,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_sort': sort,
        'available_technologies': available_technologies,
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail(request, slug):
    """
    Detailed product showcase:
    - Large CSS placeholder
    - Pricing, specifications, purification stages
    - Maintenance details
    - FAQ accordions
    - Pre-filled enquiry form modal
    - Related products
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:3]

    if not related_products.exists():
        related_products = Product.objects.filter(is_active=True).exclude(id=product.id)[:3]

    faqs = FAQ.objects.filter(is_active=True, category__in=['technology', 'maintenance'])[:4]

    # Pre-filled enquiry form
    initial_data = {'product': product.id}
    if request.user.is_authenticated:
        initial_data.update({
            'customer_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'mobile': getattr(request.user, 'phone_number', ''),
            'city': getattr(request.user, 'city', ''),
        })
    enquiry_form = ProductEnquiryForm(initial=initial_data)

    context = {
        'product': product,
        'related_products': related_products,
        'faqs': faqs,
        'enquiry_form': enquiry_form,
    }
    return render(request, 'catalog/product_detail.html', context)


def product_compare(request):
    """
    Side-by-side comparison for up to 3 purifiers.
    Supports comma-separated IDs or slugs in query params (e.g. ?ids=1,2,3).
    """
    ids_param = request.GET.get('ids', '').strip()
    products = []
    
    if ids_param:
        # Split by comma and filter digits
        id_list = [int(i.strip()) for i in ids_param.split(',') if i.strip().isdigit()][:3]
        if id_list:
            products = list(Product.objects.filter(id__in=id_list, is_active=True).select_related('category'))
            # Sort in the order requested
            id_order = {val: idx for idx, val in enumerate(id_list)}
            products.sort(key=lambda p: id_order.get(p.id, 99))

    all_active_products = Product.objects.filter(is_active=True).order_by('name')

    context = {
        'products': products,
        'all_active_products': all_active_products,
        'selected_ids': [p.id for p in products],
    }
    return render(request, 'catalog/compare.html', context)


def product_finder(request):
    """
    Interactive product finder wizard:
    - Water source (Borewell/Groundwater, Municipal/Tap, Mixed/Tanker)
    - Budget range (<10k, 10k-20k, 20k-30k, 30k+)
    - Use type (Home, Large Family, Commercial/Office)
    - Capacity preference
    Returns matching recommendations from the database.
    """
    recommendations = []
    submitted = request.GET.get('find', False)
    
    source = request.GET.get('source', '')
    budget = request.GET.get('budget', '')
    use_type = request.GET.get('use_type', '')
    capacity = request.GET.get('capacity', '')

    if submitted:
        qs = Product.objects.filter(is_active=True).select_related('category')
        
        # Filter based on water source
        if source == 'borewell':
            # High TDS needs RO
            qs = qs.filter(technology__icontains='RO')
        elif source == 'municipal':
            # Low TDS can use UV/UF or mild RO
            pass
        elif source == 'commercial':
            qs = qs.filter(intended_use__icontains='Commercial')

        # Filter by budget
        if budget == 'under_10k':
            qs = qs.filter(price__lt=10000)
        elif budget == '10k_20k':
            qs = qs.filter(price__gte=10000, price__lte=20000)
        elif budget == '20k_30k':
            qs = qs.filter(price__gte=20000, price__lte=30000)
        elif budget == 'above_30k':
            qs = qs.filter(price__gt=30000)

        # Capacity filter
        if capacity == 'under_7':
            qs = qs.filter(storage_capacity_liters__lt=7)
        elif capacity == '7_to_10':
            qs = qs.filter(storage_capacity_liters__gte=7, storage_capacity_liters__lte=10)
        elif capacity == 'over_10':
            qs = qs.filter(storage_capacity_liters__gt=10)

        recommendations = list(qs[:4])
        # If no exact match found, provide top 3 recommended alternatives
        if not recommendations:
            recommendations = list(Product.objects.filter(is_active=True).order_by('-is_featured', 'price')[:3])

    context = {
        'recommendations': recommendations,
        'submitted': bool(submitted),
        'source': source,
        'budget': budget,
        'use_type': use_type,
        'capacity': capacity,
    }
    return render(request, 'catalog/product_finder.html', context)
