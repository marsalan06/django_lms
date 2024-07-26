from django.contrib import admin
from .models import Subscription, OrganizationSubscription, StudentInvoice, OrganizationInvoice
# Register your models here.

admin.site.register(Subscription)
admin.site.register(OrganizationSubscription)
admin.site.register(StudentInvoice)
admin.site.register(OrganizationInvoice)
