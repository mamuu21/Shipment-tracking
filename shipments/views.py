from django.shortcuts import render

from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from .models import Shipment, Customer, Parcel, Document, Invoice
from .serializers import ShipmentSerializer, CustomerSerializer, ParcelSerializer, DocumentSerializer, InvoiceSerializer, RegisterSerializer
from .permissions import IsAdmin, IsCustomer, IsStaff, IsAdminOrStaff


User = get_user_model()

# Register view
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# Role-based mixin for queryset logic
class RoleBasedQuerysetMixin:
    model = None
    customer_field = 'customer__email'

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return self.model.objects.all()
        elif user.role == 'customer':
            filter_kwargs = {self.customer_field: user.email}
            return self.model.objects.filter(**filter_kwargs)
        return self.model.objects.none()


class BaseUserView:
    authentication_classes = [JWTAuthentication]


# Shipment
class ShipmentListCreateView(BaseUserView, RoleBasedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = ShipmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['shipment_no', 'transport', 'origin', 'destination', 'status']
    model = Shipment
    customer_field = 'customers__email'

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrStaff()]
        return [IsAuthenticated()]


class ShipmentDetailView(BaseUserView, RoleBasedQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShipmentSerializer
    model = Shipment
    customer_field = 'customers__email'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]


# Customer
class CustomerListCreateView(BaseUserView, RoleBasedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    model = Customer
    customer_field = 'email'

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrStaff()]
        return [IsAuthenticated()]


class CustomerDetailView(BaseUserView, RoleBasedQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    model = Customer
    customer_field = 'email'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]


# Parcel
class ParcelListCreateView(BaseUserView, RoleBasedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = ParcelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['parcel_no', 'customer__name', 'shipment__shipment_no']
    model = Parcel
    customer_field = 'customer__email'

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrStaff()]
        return [IsAuthenticated()]


class ParcelDetailView(BaseUserView, RoleBasedQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ParcelSerializer
    model = Parcel
    customer_field = 'customer__email'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]


# Document
class DocumentListCreateView(BaseUserView, RoleBasedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document_no', 'shipment__shipment_no', 'customer__name', 'parcel__parcel_no', 'document_type']
    model = Document
    customer_field = 'customer__email'

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrStaff()]
        return [IsAuthenticated()]


class DocumentDetailView(BaseUserView, RoleBasedQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    model = Document
    customer_field = 'customer__email'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]


# Invoice
class InvoiceListCreateView(BaseUserView, RoleBasedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['invoice_no', 'customer__name', 'shipment__shipment_no']
    model = Invoice
    customer_field = 'customer__email'

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrStaff()]
        return [IsAuthenticated()]


class InvoiceDetailView(BaseUserView, RoleBasedQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer
    model = Invoice
    customer_field = 'customer__email'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

