import re
import calendar
from datetime import timedelta
from django.db import models
from django.conf import settings
import uuid
from accounts.models import Organization
from django.utils.deconstruct import deconstructible

# Define Validators
@deconstructible
class StudentInvoiceValidator:
    def __call__(self, instance):
        instance.validation_messages = []
        billing_month = instance.billing_period_date.month
        billing_year = instance.billing_period_date.year
        if not instance.pk:
            if StudentInvoice.objects.filter(user=instance.user, billing_period_date__month=billing_month, billing_period_date__year=billing_year).exists():
                instance.validation_messages.append("An invoice for this user and billing period already exists.")

        if instance.organization_subscription:
            if instance.billing_period_date < instance.organization_subscription.date_of_subscription:
                instance.validation_messages.append("Billing period date cannot be earlier than the subscription date.")

            previous_due_date = instance.get_previous_due_date()
            if instance.billing_period_date > previous_due_date:
                instance.validation_messages.append("Billing period date must be smaller or equal to the next due date of the last invoice.")
        if instance.amount_paid and instance.amount_paid > instance.amount_payable:
            instance.validation_messages.append("Amount paid cannot exceed amount payable.")

        
@deconstructible
class AmountValidator:
    def __call__(self, instance):
        if instance.amount_paid and instance.amount_paid > instance.amount_payable:
            instance.validation_messages.append("Amount paid cannot exceed amount payable.")

# Define Model Classes
def generate_uuid(length=6):
    return str(uuid.uuid4().int)[:length]

class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
    ]

    DURATION_MAPPING = {
        'monthly': 1,
        'yearly': 12,
        'quarterly': 3,
        'half_yearly': 6,
    }

    name = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.name in self.DURATION_MAPPING:
            self.duration = self.DURATION_MAPPING[self.name]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class OrganizationSubscription(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    date_of_subscription = models.DateField()

    def __str__(self):
        return f"{self.organization.name} - {self.subscription.name} ({self.date_of_subscription})"

class OrganizationInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    amount_payable = models.FloatField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)
    billing_period_date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True,blank=True)
    next_due_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=6, unique=True, blank=True, null=True, default=generate_uuid)
    validation_messages = []

    def save(self, *args, **kwargs):
        if self.organization_subscription:
            organization = self.organization_subscription.organization
            student_count = organization.users.filter(is_student=True).count()
            self.amount_payable = student_count * float(self.organization_subscription.subscription.price)

        # Validate before saving
        self.validation_messages = []
        AmountValidator()(self)
        if self.validation_messages:
            print(self.validation_messages)
            print("wow")
            return  # Skip saving if there are validation errors
        
        super().save(*args, **kwargs)

class StudentInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_payable = models.FloatField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)
    billing_period_date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=6, unique=True, blank=True, null=True, default=generate_uuid)
    validation_messages = []

    def save(self, *args, **kwargs):
        self.validation_messages = []
        StudentInvoiceValidator()(self)
        # AmountValidator()(self)

        if self.validation_messages:
            print(self.validation_messages)
            return  # Skip saving if there are validation errors

        if self.organization_subscription:
            if not self.pk:
                self.amount_payable = float(self.organization_subscription.subscription.price)
                self.amount_paid = float(self.organization_subscription.subscription.price)
                self.next_due_date = self.calculate_next_due_date(self.get_previous_due_date(), self.organization_subscription.subscription.duration)

            if self.pk:
                old_instance = StudentInvoice.objects.get(pk=self.pk)
                old_amount = old_instance.amount_paid
            else:
                old_amount = 0
        super(StudentInvoice, self).save(*args, **kwargs)

        # Update or create OrganizationInvoice based on the student invoice
        self.update_organization_invoice(old_amount)
    def get_previous_due_date(self):
        previous_invoices = StudentInvoice.objects.filter(user=self.user).count()
        if previous_invoices == 0:
            return self.organization_subscription.date_of_subscription
        else:
            last_invoice = StudentInvoice.objects.filter(user=self.user).order_by('-billing_period_date').first()
            return last_invoice.next_due_date

    def calculate_next_due_date(self, start_date, months_to_add):
        next_date = start_date
        for _ in range(months_to_add):
            days_in_month = calendar.monthrange(next_date.year, next_date.month)[1]
            next_date += timedelta(days=days_in_month)
        return next_date

    def update_organization_invoice(self,old_amount):
        invoice_month = self.billing_period_date.month
        invoice_year = self.billing_period_date.year
        org_invoice = OrganizationInvoice.objects.filter(
            organization_subscription=self.organization_subscription,
            billing_period_date__month=invoice_month,
            billing_period_date__year=invoice_year
        ).first()
        
        print("ttttt\n\n\n")
        if org_invoice:
            if self.payment_complete and self.payment_date:
                print("rrrrr\n\n\n")
                amount_difference = self.amount_paid - old_amount
                print(amount_difference)
                org_invoice.amount_paid +=  amount_difference
                org_invoice.save()
        else:
            if self.payment_complete and self.payment_date:
                OrganizationInvoice.objects.create(
                    organization_subscription=self.organization_subscription,
                    amount_payable=self.amount_payable,
                    amount_paid=self.amount_paid,
                    billing_period_date=self.billing_period_date,
                    next_due_date=self.next_due_date
                )
