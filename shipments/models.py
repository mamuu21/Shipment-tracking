from django.db import models
from djmoney.models.fields import MoneyField
from django.utils.timezone import now


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('in_transit', 'In-transit'),
        ('delivered', 'Delivered')
    ]
    
    TRANSPORT = [
        ('air', 'Air'),
        ('sea', 'Sea'),
        ('road', 'Road'),
        ('rail', 'Rail')
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

    def customer_count(self):
        """Dynamically count the number of customers in this shipment"""
        return self.customers.count()
    
    def parcel_count(self):
        """Dynamically count the number of parcels in this shipment"""
        return self.parcels.count()
    
    def formatted_weight(self):
        return f"{self.weight} {self.weight_unit}"
    
    def formatted_volume(self):
        return f"{self.volume} {self.volume_unit}"
    
    def __str__(self):
        return self.shipment_no


class Customer(models.Model):
    shipment = models.ForeignKey(
        Shipment, 
        on_delete=models.CASCADE, 
        related_name='customers',
        to_field='shipment_no', 
        db_column='shipment_no',
        null=True, 
        blank=True)
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name


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
        ('box', 'Box'),
        ('parcel', 'Parcel'),
        ('envelope', 'Envelope')
    ]
    
    parcel_no = models.CharField(max_length=100, primary_key=True)
    shipment = models.ForeignKey(
        Shipment, 
        on_delete=models.CASCADE, 
        related_name='parcels',
        to_field='shipment_no',
        db_column='shipment_no')
    
    weight = models.FloatField()
    weight_unit = models.CharField(max_length=10, choices=WEIGHT_UNITS, default='kg')
    
    volume = models.FloatField()
    volume_unit = models.CharField(max_length=10, choices=VOLUME_UNITS, default='m³')
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='parcels',
        null=True,
        blank=True)
    
    charge = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS')
    commodity_type = models.CharField(max_length=255, choices=COMMODITY_TYPE, default='parcel')
    discription = models.TextField(blank=True, null=True)
    payment = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS')

    def formatted_weight(self):
        return f"{self.weight} {self.weight_unit}"
    
    def formatted_volume(self):
        return f"{self.volume} {self.volume_unit}"
    
    def __str__(self):
        return self.parcel_no


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('invoice', 'Invoice'),
        ('bill_of_lading', 'Bill of Lading'),
        ('customs_clearance', 'Customs Clearance'),
        ('packing_list', 'Packing List'),
        ('other', 'Other')
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
    shipment = models.OneToOneField(
        'Shipment',
        on_delete=models.CASCADE,
        related_name='invoices',
        to_field='shipment_no',
        db_column='shipment_no'
    )
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    parcel = models.ForeignKey(
        'Parcel',
        on_delete=models.SET_NULL,
        db_column='parcel_no',
        null=True,
        blank=True,
        related_name='invoices'
    )
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    total_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS')
    tax = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS', default=0)
    final_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='TZS')
    status = models.CharField(
        max_length=20,
        choices=[('unpaid', 'Unpaid'), ('paid', 'Paid'), ('overdue', 'Overdue')],
        default='unpaid'
    )

    def calculate_final_amount(self):
        """Automatically calculate the final amount after tax and discount."""
        self.final_amount = self.total_amount + self.tax

    def save(self, *args, **kwargs):
        self.calculate_final_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_no} - {self.customer.name}"

