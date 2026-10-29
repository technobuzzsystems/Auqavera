from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),

    # Command Center / Dashboard
    path('', views.dashboard_home, name='home'),

    # Products CRUD
    path('products/', views.dashboard_products, name='products'),
    path('products/add/', views.dashboard_product_create, name='product_create'),
    path('products/<int:pk>/', views.dashboard_product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.dashboard_product_edit, name='product_edit'),
    path('products/<int:pk>/toggle-status/', views.dashboard_product_toggle_status, name='product_toggle_status'),
    path('products/<int:pk>/toggle-featured/', views.dashboard_product_toggle_featured, name='product_toggle_featured'),
    path('products/<int:pk>/delete/', views.dashboard_product_delete, name='product_delete'),

    # Multiple Product Images
    path('products/<int:pk>/images/', views.dashboard_product_images, name='product_images'),
    path('images/<int:image_id>/primary/', views.dashboard_image_set_primary, name='image_set_primary'),
    path('images/<int:image_id>/delete/', views.dashboard_image_delete, name='image_delete'),

    # Inventory
    path('inventory/', views.dashboard_inventory, name='inventory'),
    path('inventory/adjust/<int:product_id>/', views.dashboard_inventory_adjust, name='inventory_adjust'),
    path('inventory/history/', views.dashboard_inventory_history, name='inventory_history'),

    # Customer Enquiries
    path('enquiries/', views.dashboard_enquiries, name='enquiries'),
    path('enquiries/<int:pk>/', views.dashboard_enquiry_detail, name='enquiry_detail'),
    path('enquiries/<int:pk>/status/', views.dashboard_enquiry_update_status, name='enquiry_status'),

    # Service Requests
    path('service-requests/', views.dashboard_service_requests, name='service_requests'),
    path('service-requests/<int:pk>/', views.dashboard_service_detail, name='service_detail'),
    path('service-requests/<int:pk>/status/', views.dashboard_service_update_status, name='service_status'),

    # Categories
    path('categories/', views.dashboard_categories, name='categories'),
    path('categories/add/', views.dashboard_category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.dashboard_category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.dashboard_category_delete, name='category_delete'),

    # Users & Permissions
    path('users/', views.dashboard_users, name='users'),
    path('users/create/', views.dashboard_user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.dashboard_user_edit, name='user_edit'),
    path('users/<int:pk>/toggle-active/', views.dashboard_user_toggle_active, name='user_toggle_active'),

    # Site Settings
    path('settings/', views.dashboard_site_settings, name='site_settings'),
]
