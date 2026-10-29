from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('service-request/', views.service_request_view, name='service_request_form'),
    path('service-request/success/', views.service_request_success, name='service_request_success'),
]
