from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    ShipmentListCreateView, ShipmentDetailView,
    CustomerListCreateView, CustomerDetailView,
    ParcelListCreateView, ParcelDetailView,
    DocumentListCreateView, DocumentDetailView,
    InvoiceListCreateView, InvoiceDetailView,
    RegisterView, 
)


urlpatterns = [  
    path("register/", RegisterView.as_view(), name="register"),
    path('login/', TokenObtainPairView.as_view(), name='login' ),
    
    path('shipments/', ShipmentListCreateView.as_view(), name='shipment-list-create'),
    path('shipments/<str:pk>/', ShipmentDetailView.as_view(), name='shipment-detail'),
    
    path('customers/', CustomerListCreateView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    
    path('parcels/', ParcelListCreateView.as_view(), name='parcel-list-create'),
    path('parcels/<str:pk>/', ParcelDetailView.as_view(), name='parcel-detail'),
    
    path('documents/', DocumentListCreateView.as_view(), name='document-list-create'),
    path('documents/<str:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<str:pk>/', InvoiceDetailView.as_view(), name='invoice-detail')
]
