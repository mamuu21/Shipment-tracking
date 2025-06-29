from django.db import models
from djmoney.models.fields import MoneyField
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Staff', 'Staff'),
        ('Admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return self.username

    def is_customer(self):
        return self.role == 'customer'

    def is_staff_user(self): 
        return self.role == 'staff'

    def is_admin(self):
        return self.role == 'admin'
  
  
class Customer(models.Model):
    STATUS = [
        ('Active', 'Active'),
        ('Dormant', 'Dormant')
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='Active')

    def __str__(self):
        return self.name
    
        
class Shipment(models.Model):
    STATUS_CHOICES = [
        ('In-transit', 'In-transit'),
        ('Delivered', 'Delivered')
    ]
    
    TRANSPORT = [
        ('Air', 'Air'),
        ('Sea', 'Sea'),
        ('Road', 'Road'),
        ('Rail', 'Rail')
    ]
    
    WEIGHT_UNITS = [
        ('kg', 'Kilograms'),
        ('lbs', 'Pounds'),
        ('tons', 'Tons')
    ]

    VOLUME_UNITS = [
        ('m³', 'Cubic Meters'),
        ('ft³', 'Cubic Feet')
    ]
    
    shipment_no = models.CharField(max_length=100, primary_key=True)
    # customer = models.ForeignKey(
    #     Customer,
    #     on_delete=models.CASCADE, 
    #     related_name='shipments',
    #     null=True, 
    #     blank=True)
    transport = models.CharField(max_length=100, choices=TRANSPORT)
    vessel = models.CharField(max_length=250)
    
    weight = models.FloatField()
    weight_unit = models.CharField(max_length=10, choices=WEIGHT_UNITS, default='kg')
    
    volume = models.FloatField()
    volume_unit = models.CharField(max_length=10, choices=VOLUME_UNITS, default='m³')
    
    origin = models.CharField(max_length=250)
    destination = models.CharField(max_length=250)
    steps = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    def customers(self):
        # Get all customers who have parcels in this shipment
        return Customer.objects.filter(parcels__shipment=self).distinct()

    def customer_count(self):
        return self.customers().count()
    
    def parcel_count(self):
        return self.parcels.count()
    
    def formatted_weight(self):
        return f"{self.weight} {self.weight_unit}"
    
    def formatted_volume(self):
        return f"{self.volume} {self.volume_unit}"
    
    def __str__(self):
        return self.shipment_no


class Parcel(models.Model):
    WEIGHT_UNITS = [
        ('kg', 'Kilograms'),
        ('lbs', 'Pounds'),
        ('tons', 'Tons')
    ]

    VOLUME_UNITS = [
        ('m³', 'Cubic Meters'),
        ('ft³', 'Cubic Feet')
    ]
    
    COMMODITY_TYPE = [
        ('Box', 'Box'),
        ('Parcel', 'Parcel'),
        ('Envelope', 'Envelope')
    ]
    
    parcel_no = models.CharField(max_length=100, primary_key=True)
    shipment = models.ForeignKey(
        Shipment, 
        on_delete=models.CASCADE, 
        related_name='parcels',
        to_field='shipment_no',
        db_column='shipment_no')
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='parcels',
        null=True,
        blank=True)
    
    weight = models.FloatField()
    weight_unit = models.CharField(max_length=10, choices=WEIGHT_UNITS, default='kg')
    
    volume = models.FloatField()
    volume_unit = models.CharField(max_length=10, choices=VOLUME_UNITS, default='m³')
    
    charge = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS')
    payment = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')
    commodity_type = models.CharField(max_length=255, choices=COMMODITY_TYPE, default='parcel')
    description = models.TextField(blank=True, null=True)

    def formatted_weight(self):
        return f"{self.weight} {self.weight_unit}"
    
    def formatted_volume(self):
        return f"{self.volume} {self.volume_unit}"
    
    def __str__(self):
        return self.parcel_no


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('Invoice', 'Invoice'),
        ('Bill_of_lading', 'Bill of Lading'),
        ('Customs_clearance', 'Customs Clearance'),
        ('Packing_list', 'Packing List'),
        ('Other', 'Other')
    ]

    document_no = models.CharField(max_length=100, primary_key=True, default='DOC0001')
    shipment = models.ForeignKey(
        'Shipment',
        on_delete=models.CASCADE,
        related_name='documents',
        to_field='shipment_no',
        db_column='shipment_no'
    )
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    parcel = models.ForeignKey(
        'Parcel',
        on_delete=models.SET_NULL,
        related_name='documents',
        db_column='parcel_no',
        null=True,
        blank=True
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    issued_date = models.DateTimeField(default=now, editable=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_no}"


class Invoice(models.Model):
    invoice_no = models.CharField(max_length=100, primary_key=True)
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    total_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS')
    tax = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS', default=0)
    final_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS')
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Overdue', 'Overdue')],
        default='Pending'
    )

    def calculate_final_amount(self):
        """Automatically calculate the final amount after tax and discount."""
        self.final_amount = self.total_amount + self.tax

    def save(self, *args, **kwargs):
        self.calculate_final_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_no} - {self.customer.name}"

