from django.shortcuts import render
from .models import Shipment, Customer, Parcel, Document, Invoice
from .serializers import ShipmentSerializer, CustomerSerializer, ParcelSerializer, DocumentSerializer, InvoiceSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
