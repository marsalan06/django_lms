from django.db import models
from django.conf import settings
import uuid
from accounts.models import Organization
from datetime import timedelta
from django.core.exceptions import ValidationError
import secrets
import string

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

def generate_uuid(length=6):
    """Generate a secure random numeric string."""
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))

class OrganizationInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    amount_payable = models.FloatField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)
    billing_period_date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    next_due_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=200, blank=True, null=True, default=generate_uuid)

    def save(self, *args, **kwargs):
        if self.organization_subscription:
            # Calculate amount_payable based on the number of students and subscription price
            
            organization = self.organization_subscription.organization
            student_count = organization.users.filter(is_student=True).count()
            print("\n\nwow",student_count)
            self.amount_payable = student_count * float(self.organization_subscription.subscription.price)

            # Ensure amount_paid does not exceed amount_payable
            if self.amount_paid and self.amount_paid > self.amount_payable:
                raise ValidationError("Amount paid cannot exceed amount payable")

            subscription_duration = self.organization_subscription.subscription.duration
            previous_invoices = OrganizationInvoice.objects.filter(organization_subscription=self.organization_subscription).count()
            if previous_invoices == 0:
                self.next_due_date = self.organization_subscription.date_of_subscription + timedelta(days=subscription_duration * 30)
            else:
                self.next_due_date = self.billing_period_date + timedelta(days=subscription_duration * 30)
        
        super(OrganizationInvoice, self).save(*args, **kwargs)

class StudentInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_payable = models.FloatField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)
    billing_period_date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    next_due_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=200, blank=True, null=True, default=generate_uuid)

    def save(self, *args, **kwargs):
        if self.organization_subscription:
            # Calculate amount_payable based on the subscription price
            self.amount_payable = float(self.organization_subscription.subscription.price)
            self.amount_paid = float(self.organization_subscription.subscription.price)

            # Ensure amount_paid does not exceed amount_payable
            # if self.amount_paid and self.amount_paid > self.amount_payable:
            #     raise ValidationError("Amount paid cannot exceed amount payable")

            subscription_duration = self.organization_subscription.subscription.duration
            previous_invoices = StudentInvoice.objects.filter(user=self.user).count()
            if previous_invoices == 0:
                self.next_due_date = self.organization_subscription.date_of_subscription + timedelta(days=subscription_duration * 30)
            else:
                self.next_due_date = self.billing_period_date + timedelta(days=subscription_duration * 30)

            if self.pk:
                old_instance = StudentInvoice.objects.get(pk=self.pk)
                old_amount = old_instance.amount_paid
            else:
                old_amount = 0
        super(StudentInvoice, self).save(*args, **kwargs)

        # Update or create OrganizationInvoice based on the student invoice
        self.update_organization_invoice(old_amount)
        
        
        

        
        

    def update_organization_invoice(self,old_amount):
        invoice_month = self.billing_period_date.month
        invoice_year = self.billing_period_date.year
        org_invoice = OrganizationInvoice.objects.filter(
            organization_subscription=self.organization_subscription,
            billing_period_date__month=invoice_month,
            billing_period_date__year=invoice_year
        ).first()

        
        if org_invoice:
            # Update the amount in the existing organization invoice
            amount_difference = self.amount_paid - old_amount
            org_invoice.amount_paid += amount_difference
            org_invoice.save()
        
        else:
            OrganizationInvoice.objects.create(
                organization_subscription=self.organization_subscription,
                amount_payable=self.amount_payable,
                amount_paid=self.amount_paid,
                billing_period_date=self.billing_period_date,
                payment_complete=self.payment_complete,
                payment_date=self.payment_date,
                next_due_date=self.next_due_date,
                invoice_code=self.invoice_code
            )

