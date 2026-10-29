from django.urls import path
from . import views

app_name = 'enquiries'

urlpatterns = [
    path('enquiry/', views.submit_enquiry, name='enquiry_form'),
    path('enquiry/submit/', views.submit_enquiry, name='submit_enquiry'),
    path('enquiry/success/', views.enquiry_success, name='enquiry_success'),
]
