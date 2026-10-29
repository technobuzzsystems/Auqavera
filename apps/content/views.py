from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from apps.catalog.models import Product, Category
from apps.content.models import Testimonial, FAQ, SiteSetting, NewsletterSubscriber
from apps.content.forms import NewsletterForm, ContactForm

def home_view(request):
    """
    Polished Homepage with:
    - Hero with abstract ripple/wave CSS art
    - Trust statistics strip
    - Product category cards
    - Featured products from DB
    - Why Choose Us cards
    - Step-by-step How Purification Works
    - Interactive Product Finder entry point
    - Customer Testimonials (clearly marked demo)
    - Service CTA
    - Newsletter signup
    """
    featured_products = Product.objects.filter(
        status='published',
        is_active=True,
        is_featured=True
    ).select_related('category').prefetch_related('images').order_by('-updated_at')[:6]
    
    categories = Category.objects.filter(is_active=True).order_by('sort_order')
    testimonials = Testimonial.objects.filter(is_active=True)[:3]
    faqs = FAQ.objects.filter(is_active=True)[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'testimonials': testimonials,
        'faqs': faqs,
        'newsletter_form': NewsletterForm(),
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    """Original brand story, mission, engineering philosophy, and values."""
    return render(request, 'pages/about.html')


def contact_view(request):
    """Contact page with validated contact form and demo business information."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # In a demo app, we log/show success feedback
            messages.success(
                request,
                "Thank you for contacting AQUAVERA. Your message has been received successfully. "
                "Our team will get in touch shortly."
            )
            return redirect('pages:contact')
    else:
        form = ContactForm()

    faqs = FAQ.objects.filter(is_active=True, category='general')[:5]
    return render(request, 'pages/contact.html', {'form': form, 'faqs': faqs})


def newsletter_subscribe(request):
    """Newsletter subscription handler with honeypot spam protection."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            sub, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            if created:
                messages.success(request, f"Welcome! {email} has been subscribed to AQUAVERA water care insights.")
            else:
                messages.info(request, f"{email} is already subscribed to our updates.")
        else:
            messages.error(request, "Please provide a valid email address.")
    
    # Redirect back to referring page or home
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


def robots_txt(request):
    """Standard robots.txt for search engines."""
    lines = [
        "User-agent: *",
        "Disallow: /dashboard/",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    """Dynamic XML sitemap listing public pages and active products."""
    products = Product.objects.filter(is_active=True).values('slug', 'updated_at')
    categories = Category.objects.filter(is_active=True).values('slug')
    
    base = request.build_absolute_uri('/').rstrip('/')
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{base}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{base}/products/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{base}/about/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>',
        f'  <url><loc>{base}/contact/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>',
        f'  <url><loc>{base}/service-request/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base}/product-finder/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base}/compare/</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>',
    ]
    
    for prod in products:
        loc = f"{base}/products/{prod['slug']}/"
        date_str = prod['updated_at'].strftime('%Y-%m-%d')
        xml_lines.append(f'  <url><loc>{loc}</loc><lastmod>{date_str}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')
        
    xml_lines.append('</urlset>')
    return HttpResponse("\n".join(xml_lines), content_type="application/xml")


def custom_404_view(request, exception=None):
    """Custom 404 Not Found error page."""
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    """Custom 500 Internal Server Error page."""
    return render(request, 'errors/500.html', status=500)

