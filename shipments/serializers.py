from rest_framework import serializers
from django.db.models import Sum
from .models import Shipment, Customer, Parcel, Document, Invoice, User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn’t match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id']
        

class CustomerSerializer(serializers.ModelSerializer):
    total_invoices_paid = serializers.SerializerMethodField()
    total_parcels = serializers.SerializerMethodField()
    total_parcel_weight = serializers.SerializerMethodField()
    total_shipments = serializers.SerializerMethodField()
    shipment_nos = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'address', 'phone', 'status',
                  'total_invoices_paid', 'total_parcels', 'total_parcel_weight',
                  'total_shipments', 'shipment_nos']
        
    def get_total_invoices_paid(self, obj):
        return obj.invoices.filter(status='Pais').count()
    
    def get_total_parcels(self, obj):
        return obj.parcels.count()
    
    def get_total_parcel_weight(self, obj):
        total_weight = obj.parcels.aggregate(total=Sum('weight'))['total']
        return total_weight or 0
    
    def get_total_shipments(self, obj):
        return Shipment.objects.filter(parcels__customer=obj).distinct().count()
    
    def get_shipment_nos(self, obj):
        shipments = Shipment.objects.filter(parcels__customer=obj).distinct()
        return [s.shipment_no for s in shipments]
    
               

class ShipmentSerializer(serializers.ModelSerializer):
    customer_count = serializers.SerializerMethodField()
    parcel_count = serializers.SerializerMethodField
    
    class Meta:
        model = Shipment
        fields = ['shipment_no', 'transport', 'vessel', 'origin', 'destination',
            'weight', 'volume', 'steps', 'status',
            'customer_count', 'parcel_count']
        
    def get_customer_count(self, obj):
            return Customer.objects.filter(parcels__shipment=obj).distinct().count()

    def get_parcel_count(self, obj):
        return obj.parcels.count()

        
        
class ParcelSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source='customer', write_only=True
    )
    
    class Meta:
        model = Parcel
        fields = [
            'parcel_no', 'shipment', 'customer', 'customer_id', 'weight', 'weight_unit',
            'volume', 'volume_unit', 'charge', 'payment','commodity_type', 'description'
        ]
        
        
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        
        
class InvoiceSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()
    shipment = serializers.StringRelatedField()
    
    class Meta:
        model = Invoice
        fields = '__all__'