from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('compare/', views.product_compare, name='product_compare'),
    path('product-finder/', views.product_finder, name='product_finder'),
]
