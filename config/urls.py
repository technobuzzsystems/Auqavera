"""
URL configuration for AQUAVERA Premium Water Purifiers project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('', include('apps.catalog.urls', namespace='catalog')),
    path('', include('apps.enquiries.urls', namespace='enquiries')),
    path('', include('apps.services.urls', namespace='services')),
    path('', include('apps.content.urls', namespace='pages')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'apps.content.views.custom_404_view'
handler500 = 'apps.content.views.custom_500_view'

