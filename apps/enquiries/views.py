from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProductEnquiryForm
from .models import ProductEnquiry

def submit_enquiry(request):
    """Handles product enquiry form submissions."""
    if request.method == 'POST':
        form = ProductEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            if request.user.is_authenticated:
                enquiry.user = request.user
            enquiry.save()

            # Store in session for success display
            request.session['latest_enquiry_ref'] = enquiry.reference_number
            request.session['latest_enquiry_name'] = enquiry.customer_name

            messages.success(request, f"Enquiry #{enquiry.reference_number} submitted successfully!")
            return redirect('enquiries:enquiry_success')
        else:
            messages.error(request, "Please correct the errors in the enquiry form.")
            # If submitted from product detail or contact, render or redirect back
            return render(request, 'enquiries/enquiry_form.html', {'form': form})
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'customer_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'mobile': getattr(request.user, 'phone_number', ''),
                'city': getattr(request.user, 'city', ''),
            }
        form = ProductEnquiryForm(initial=initial)
        return render(request, 'enquiries/enquiry_form.html', {'form': form})


def enquiry_success(request):
    """Confirmation page with unique enquiry reference number."""
    ref_number = request.session.get('latest_enquiry_ref', '')
    customer_name = request.session.get('latest_enquiry_name', 'Customer')
    
    enquiry = None
    if ref_number:
        enquiry = ProductEnquiry.objects.filter(reference_number=ref_number).first()

    context = {
        'reference_number': ref_number,
        'customer_name': customer_name,
        'enquiry': enquiry,
    }
    return render(request, 'enquiries/enquiry_success.html', context)
