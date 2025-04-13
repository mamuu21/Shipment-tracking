from django.contrib import admin
from .models import Shipment, Customer, Parcel, Document, Invoice


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_no', 
                    'transport', 
                    'vessel', 
                    'customers', 
                    'parcels', 
                    'formatted_weight', 
                    'formatted_volume', 
                    'origin', 
                    'destination', 
                    'steps',
                    'documents',
                    'status')
    search_fields = ('shipment_no','vessel')

    def customers(self, obj):
        return obj.customers.count()  
    customers.short_description = 'Customers'

    def parcels(self, obj):
        return obj.parcels.count()  
    parcels.short_description = 'Parcels'

    def documents(self, obj):
        return obj.documents.count() if hasattr(obj, 'documents') else 0
    documents.short_description = 'Documents'
    
    def formatted_weight(self, obj):
        return obj.formatted_weight()
    formatted_weight.short_description = 'Weight'

    def formatted_volume(self, obj):
        return obj.formatted_volume()
    formatted_volume.short_description = 'Volume'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('documents')  


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'shipment_number', 'parcel_numbers')
    search_fields = ('name', 'shipment_number', 'phone', 'parcel_numbers')

    def shipment_number(self, obj):
        return obj.shipment.shipment_no if obj.shipment else "No Shipment"
    shipment_number.short_description = 'Shipment No'

    def parcel_numbers(self, obj):
        parcels = obj.parcels.all()  # Get all related parcels
        return ", ".join(parcel.parcel_no for parcel in parcels) if parcels else "Container"
    parcel_numbers.short_description = 'Parcel No'


class ParcelAdmin(admin.ModelAdmin):
    list_display = ('parcel_no', 'shipment_number', 'customer_name')
    search_fields = ('parcel_no', 'customer_name', 'shipment_number')

    def shipment_number(self, obj):
        return obj.shipment.shipment_no if obj.shipment else "No Shipment"
    shipment_number.short_description = 'Shipment No'

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "No Customer"
    customer_name.short_description = 'Customer Name'
    

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_no', 'get_document_type', 'shipment', 'customer', 'parcel', 'issued_date', 'description')
    list_filter = ('document_type', 'issued_date', 'shipment')
    search_fields = ('document_no', 'shipment__shipment_no', 'customer__name', 'parcel__parcel_no', 'document_type')
    ordering = ('-issued_date',)

    def get_document_type(self, obj):
        return obj.get_document_type_display() 
    get_document_type.short_description = 'Document Type'
    
    
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'parcel', 'customer', 'shipment', 'total_amount', 'due_date', 'status')
    list_filter = ('status', 'issue_date', 'shipment')
    search_fields = ('invoice_no', 'customer__name', 'shipment__shipment_no')
    ordering = ('-issue_date',)

    def save_model(self, request, obj, form, change):
        obj.calculate_final_amount()
        super().save_model(request, obj, form, change)
        
            
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Parcel, ParcelAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Invoice, InvoiceAdmin)

