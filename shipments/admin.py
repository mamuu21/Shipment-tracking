from django.contrib import admin
from .models import Shipment, Customer, Parcel, Document, Invoice

from django.contrib.auth.admin import UserAdmin
from .models import User

class UserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
admin.site.register(User, UserAdmin)


class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'shipment_no',
        'transport',
        'vessel',
        'customer_count',
        'parcel_count',
        'formatted_weight',
        'formatted_volume',
        'origin',
        'destination',
        'steps',
        'document_count',
        'status',
    )
    
    search_fields = ('shipment_no', 'vessel', 'status')

    def customer_count(self, obj):
        return obj.customer_count()
    customer_count.short_description = 'Customers'

    def parcel_count(self, obj):
        return obj.parcel_count()
    parcel_count.short_description = 'Parcels'

    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Documents'

    def formatted_weight(self, obj):
        return obj.formatted_weight()
    formatted_weight.short_description = 'Weight'

    def formatted_volume(self, obj):
        return obj.formatted_volume()
    formatted_volume.short_description = 'Volume'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('documents', 'parcels__customer')  # optimize related lookups



class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone','email', 'address', 'status')
    search_fields = ('name', 'phone')

    # def shipment_number(self, obj):
    #     return obj.shipment.shipment_no if obj.shipment else "No Shipment"
    # shipment_number.short_description = 'Shipment No'

    # def parcel_numbers(self, obj):
    #     parcels = obj.parcels.all()  
    #     return ", ".join(parcel.parcel_no for parcel in parcels) if parcels else "Container"
    # parcel_numbers.short_description = 'Parcel No'


class ParcelAdmin(admin.ModelAdmin):
    list_display = ('parcel_no', 'shipment_number', 'customer_name')
    search_fields = ('parcel_no', 'customer__name', 'shipment__shipment_no')

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
    list_display = ('invoice_no', 'customer', 'total_amount', 'due_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('invoice_no', 'customer__name')
    ordering = ('-issue_date',)

    def save_model(self, request, obj, form, change):
        obj.calculate_final_amount()
        super().save_model(request, obj, form, change)
        
            
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Parcel, ParcelAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Invoice, InvoiceAdmin)

