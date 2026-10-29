from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from apps.catalog.models import Product, Category
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest
from .forms import ProductAdminForm, EnquiryStatusForm, ServiceStatusForm

@staff_member_required(login_url='accounts:login')
def dashboard_home(request):
    """Staff dashboard summary overview."""
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_enquiries = ProductEnquiry.objects.count()
    new_enquiries = ProductEnquiry.objects.filter(status='new').count()
    pending_services = ServiceRequest.objects.filter(status='pending').count()
    completed_services = ServiceRequest.objects.filter(status='completed').count()

    recent_enquiries = ProductEnquiry.objects.select_related('product')[:5]
    recent_services = ServiceRequest.objects.all()[:5]

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        'pending_services': pending_services,
        'completed_services': completed_services,
        'recent_enquiries': recent_enquiries,
        'recent_services': recent_services,
    }
    return render(request, 'dashboard/index.html', context)


@staff_member_required(login_url='accounts:login')
def dashboard_products(request):
    """Staff management for products."""
    products = Product.objects.select_related('category').order_by('-created_at')
    return render(request, 'dashboard/products.html', {'products': products})


@staff_member_required(login_url='accounts:login')
def dashboard_product_create(request):
    """Add a new product through staff dashboard."""
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' created successfully!")
            return redirect('dashboard:products')
        else:
            messages.error(request, "Failed to create product. Please check the fields.")
    else:
        form = ProductAdminForm()

    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add New Water Purifier'})


@staff_member_required(login_url='accounts:login')
def dashboard_product_edit(request, pk):
    """Edit existing product."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('dashboard:products')
        else:
            messages.error(request, "Failed to update product.")
    else:
        form = ProductAdminForm(instance=product)

    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product, 'title': f'Edit: {product.name}'})


@staff_member_required(login_url='accounts:login')
def dashboard_product_delete(request, pk):
    """Delete a product."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' was deleted.")
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


@staff_member_required(login_url='accounts:login')
def dashboard_enquiries(request):
    """Staff management for customer enquiries."""
    status_filter = request.GET.get('status', '').strip()
    enquiries = ProductEnquiry.objects.select_related('product', 'user').order_by('-created_at')
    if status_filter:
        enquiries = enquiries.filter(status=status_filter)

    return render(request, 'dashboard/enquiries.html', {
        'enquiries': enquiries,
        'current_status': status_filter,
        'status_choices': ProductEnquiry.STATUS_CHOICES,
    })


@staff_member_required(login_url='accounts:login')
def dashboard_enquiry_update_status(request, pk):
    """Quick update enquiry status."""
    enquiry = get_object_or_404(ProductEnquiry, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ProductEnquiry.STATUS_CHOICES):
            enquiry.status = new_status
            enquiry.save()
            messages.success(request, f"Enquiry #{enquiry.reference_number} marked as {enquiry.get_status_display()}.")
    return redirect('dashboard:enquiries')


@staff_member_required(login_url='accounts:login')
def dashboard_service_requests(request):
    """Staff management for service tickets."""
    status_filter = request.GET.get('status', '').strip()
    services = ServiceRequest.objects.select_related('user').order_by('-created_at')
    if status_filter:
        services = services.filter(status=status_filter)

    return render(request, 'dashboard/service_requests.html', {
        'services': services,
        'current_status': status_filter,
        'status_choices': ServiceRequest.STATUS_CHOICES,
    })


@staff_member_required(login_url='accounts:login')
def dashboard_service_update_status(request, pk):
    """Quick update service ticket status."""
    service_req = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ServiceRequest.STATUS_CHOICES):
            service_req.status = new_status
            service_req.save()
            messages.success(request, f"Service Request #{service_req.reference_number} updated to {service_req.get_status_display()}.")
    return redirect('dashboard:service_requests')
