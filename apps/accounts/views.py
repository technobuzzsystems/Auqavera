from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomerRegisterForm, CustomerLoginForm, CustomerProfileForm
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest

def register_view(request):
    """Customer registration view."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to AQUAVERA, {user.first_name or user.username}! Your account is ready.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = CustomerRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Customer & Staff authentication view."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            # Check for next parameter or staff redirect
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            if user.is_staff:
                return redirect('dashboard:home')
            return redirect('accounts:profile')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomerLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Customer sign out handler."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('pages:home')


@login_required
def profile_view(request):
    """Customer profile page allowing updates to contact details."""
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please fix the form errors.")
    else:
        form = CustomerProfileForm(instance=request.user)

    # Summary counts
    enquiries_count = ProductEnquiry.objects.filter(user=request.user).count()
    services_count = ServiceRequest.objects.filter(user=request.user).count()

    context = {
        'form': form,
        'enquiries_count': enquiries_count,
        'services_count': services_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def my_enquiries_view(request):
    """Customer-specific view of submitted product inquiries."""
    enquiries = ProductEnquiry.objects.filter(user=request.user).select_related('product').order_by('-created_at')
    return render(request, 'accounts/my_enquiries.html', {'enquiries': enquiries})


@login_required
def my_service_requests_view(request):
    """Customer-specific view of requested service tickets."""
    service_requests = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_service_requests.html', {'service_requests': service_requests})
