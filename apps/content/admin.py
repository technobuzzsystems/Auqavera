from django.contrib import admin
from .models import Testimonial, FAQ, NewsletterSubscriber, SiteSetting

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'city', 'rating', 'is_demo_content', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_demo_content', 'rating')
    list_editable = ('is_active',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'sort_order', 'is_active')
    list_filter = ('category', 'is_active')
    list_editable = ('sort_order', 'is_active')
    search_fields = ('question', 'answer')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('website_name', 'support_email', 'support_phone')
