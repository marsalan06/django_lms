from django.contrib import admin
from .models import Subscription, OrganizationSubscription, StudentInvoice, OrganizationInvoice
# Register your models here.

class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('duration',)
    list_display = ('name', 'description', 'price', 'duration')
    search_fields = ('name', 'description')
    
class OrganizationInvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('amount_payable', 'next_due_date')
    list_display = (
        'organization_subscription', 
        'amount_payable', 
        'amount_paid', 
        'formatted_billing_period_date',  # Custom method for formatted date
        'payment_complete', 
        'payment_date', 
        'next_due_date', 
        'invoice_code'
    )
    search_fields = ('organization_subscription__organization__name', 'invoice_code')
    list_filter = ('payment_complete',)

    def formatted_billing_period_date(self, obj):
        return obj.billing_period_date.strftime('%B %Y')  # Month Year
    formatted_billing_period_date.admin_order_field = 'billing_period_date'
    formatted_billing_period_date.short_description = 'Billing Period Date'


class StudentInvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('amount_payable', 'next_due_date', 'amount_paid')
    list_display = (
        'user', 
        'amount_payable', 
        'formatted_billing_period_date',  # Custom method for formatted date
        'payment_complete', 
        'payment_date', 
        'next_due_date', 
    )
    search_fields = ('user__username', 'invoice_code')
    list_filter = ('payment_complete',)

    def formatted_billing_period_date(self, obj):
        return obj.billing_period_date.strftime('%B %Y')  # Month Year
    formatted_billing_period_date.admin_order_field = 'billing_period_date'
    formatted_billing_period_date.short_description = 'Billing Period Date'

    
class OrganizationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'subscription', 'date_of_subscription')
    search_fields = ('organization__name', 'subscription__name')
    list_filter = ('subscription',)

    
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(OrganizationSubscription, OrganizationSubscriptionAdmin)
admin.site.register(StudentInvoice, StudentInvoiceAdmin)
admin.site.register(OrganizationInvoice, OrganizationInvoiceAdmin)
