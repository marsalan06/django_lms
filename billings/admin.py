from django.contrib import admin
from .models import Subscription, OrganizationSubscription, StudentInvoice, OrganizationInvoice
# Register your models here.

class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('duration',)
    

class OrganizationInvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('amount_payable','next_due_date')


class StudentInvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('amount_payable','next_due_date','amount_paid')

    
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(OrganizationSubscription)
admin.site.register(StudentInvoice, StudentInvoiceAdmin)
admin.site.register(OrganizationInvoice, OrganizationInvoiceAdmin)
