from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('products/', views.dashboard_products, name='products'),
    path('products/add/', views.dashboard_product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.dashboard_product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.dashboard_product_delete, name='product_delete'),
    path('enquiries/', views.dashboard_enquiries, name='enquiries'),
    path('enquiries/<int:pk>/status/', views.dashboard_enquiry_update_status, name='enquiry_status'),
    path('service-requests/', views.dashboard_service_requests, name='service_requests'),
    path('service-requests/<int:pk>/status/', views.dashboard_service_update_status, name='service_status'),
]
