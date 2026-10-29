from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ServiceRequestForm
from .models import ServiceRequest

def service_request_view(request):
    """
    Customer Service & Support booking page:
    - Installation, Maintenance, Repair, Filter Replacement
    - Validated form saved to PostgreSQL
    - Assigns unique tracking reference number
    """
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_req = form.save(commit=False)
            if request.user.is_authenticated:
                service_req.user = request.user
            service_req.save()

            request.session['latest_service_ref'] = service_req.reference_number
            request.session['latest_service_name'] = service_req.customer_name

            messages.success(request, f"Service Request #{service_req.reference_number} booked successfully!")
            return redirect('services:service_request_success')
        else:
            messages.error(request, "Please check the highlighted errors in your service booking.")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'customer_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'mobile': getattr(request.user, 'phone_number', ''),
                'city': getattr(request.user, 'city', ''),
            }
        form = ServiceRequestForm(initial=initial)

    return render(request, 'services/service_request_form.html', {'form': form})


def service_request_success(request):
    """Service request confirmation page displaying unique reference number."""
    ref_number = request.session.get('latest_service_ref', '')
    customer_name = request.session.get('latest_service_name', 'Customer')
    
    service_req = None
    if ref_number:
        service_req = ServiceRequest.objects.filter(reference_number=ref_number).first()

    context = {
        'reference_number': ref_number,
        'customer_name': customer_name,
        'service_req': service_req,
    }
    return render(request, 'services/service_request_success.html', context)
