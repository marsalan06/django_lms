from django.contrib import admin
from .models import Subscription, OrganizationSubscription, StudentInvoice, OrganizationInvoice
from django.http import HttpResponseRedirect

from django.urls import reverse
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
    
    def save_model(self, request, obj, form, change):
        print(obj.validation_messages)
        # Clear validation messages before saving
        obj.validation_messages = []
        
        # Validate and save
        obj.save()


        # Display validation messages
        if obj.validation_messages:
            # Display validation messages
            for message in obj.validation_messages:
                self.message_user(request, message, level='error')
            # Do not save the object if there are validation errors
            return
        else:
            # Save the model if no validation errors
            super().save_model(request, obj, form, change)
            # Optionally show a custom success message if needed
        
    def response_change(self, request, obj):
        if obj.validation_messages:
            # Return to the admin change page with error messages
            return self.response_change_with_errors(request, obj)
        else:
            # Return the default response if no validation errors
            return super().response_change(request, obj)

    def response_change_with_errors(self, request, obj):
        """
        Redirect back to the change form with error messages.
        """
        # Example of redirecting back to the admin change form with error messages
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name),  # Build URL for redirect
                      args=[obj.pk], current_app=self.admin_site.name)
        return HttpResponseRedirect(url)
            

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
        'next_due_date'
    )
    search_fields = ('user__username', 'invoice_code')
    list_filter = ('payment_complete',)

    def formatted_billing_period_date(self, obj):
        return obj.billing_period_date.strftime('%B %Y')  # Month Year
    formatted_billing_period_date.admin_order_field = 'billing_period_date'
    formatted_billing_period_date.short_description = 'Billing Period Date'

    def save_model(self, request, obj, form, change):
        # Clear validation messages before saving
        obj.validation_messages = []
        
        # Validate and save
        obj.save()

        # Display validation messages
        
        # Display validation messages
        if obj.validation_messages:
            # Display validation messages
            for message in obj.validation_messages:
                self.message_user(request, message, level='error')
            # Do not save the object if there are validation errors
            return
        else:
            # Save the model if no validation errors
            super().save_model(request, obj, form, change)
    def response_change(self, request, obj):
        if obj.validation_messages:
            # Return to the admin change page with error messages
            return self.response_change_with_errors(request, obj)
        else:
            # Return the default response if no validation errors
            return super().response_change(request, obj)

    def response_change_with_errors(self, request, obj):
        """
        Redirect back to the change form with error messages.
        """
        # Example of redirecting back to the admin change form with error messages
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name),  # Build URL for redirect
                      args=[obj.pk], current_app=self.admin_site.name)
        return HttpResponseRedirect(url)
            

class OrganizationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'subscription', 'date_of_subscription')
    search_fields = ('organization__name', 'subscription__name')
    list_filter = ('subscription',)
    
    

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(OrganizationSubscription, OrganizationSubscriptionAdmin)
admin.site.register(StudentInvoice, StudentInvoiceAdmin)
admin.site.register(OrganizationInvoice, OrganizationInvoiceAdmin)
