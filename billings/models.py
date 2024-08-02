from django.db import models
from django.conf import settings
import uuid
from accounts.models import Organization
from datetime import timedelta
from django.core.exceptions import ValidationError
import secrets
import string
import calendar

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
    """Generate a 6-character string from a UUID."""
    return str(uuid.uuid4().int)[:length]

class OrganizationInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    amount_payable = models.FloatField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)
    billing_period_date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    next_due_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=6, unique=True, blank=True, null=True, default=generate_uuid)

    def save(self, *args, **kwargs):
        if self.organization_subscription:
            # Calculate amount_payable based on the number of students and subscription price
            
            organization = self.organization_subscription.organization
            student_count = organization.users.filter(is_student=True).count()
            
            self.amount_payable = student_count * float(self.organization_subscription.subscription.price)

            # Ensure amount_paid does not exceed amount_payable
            if self.amount_paid and self.amount_paid > self.amount_payable:
                raise ValidationError("Amount paid cannot exceed amount payable")

            subscription_duration = self.organization_subscription.subscription.duration
            
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
    invoice_code = models.CharField(max_length=6, unique=True, blank=True, null=True, default=generate_uuid)

    def save(self, *args, **kwargs):
        
        billing_month = self.billing_period_date.month
        billing_year = self.billing_period_date.year

        # Check for existing invoices with the same user and billing month/year
        if StudentInvoice.objects.filter(user=self.user, billing_period_date__month=billing_month, billing_period_date__year=billing_year).exists():
            raise ValidationError("An invoice for this user and billing period already exists.")

        if self.organization_subscription:
            # Calculate amount_payable based on the subscription price
            self.amount_payable = float(self.organization_subscription.subscription.price)
            self.amount_paid = float(self.organization_subscription.subscription.price)

            if self.amount_paid and self.amount_paid > self.amount_payable:
                raise ValidationError("Amount paid cannot exceed amount payable")

            subscription_duration = self.organization_subscription.subscription.duration
            previous_invoices = StudentInvoice.objects.filter(user=self.user).count()
            previous_due_date=''
            if previous_invoices == 0:
                previous_due_date = self.organization_subscription.date_of_subscription
            else:
                last_invoice = StudentInvoice.objects.filter(user=self.user).order_by('-billing_period_date').first()
                previous_due_date = last_invoice.next_due_date

            if self.billing_period_date < self.organization_subscription.date_of_subscription:
                raise ValidationError("Billing period date cannot be earlier than the subscription date.")
            
            
            if self.billing_period_date > previous_due_date:
                print("rrrr\n\n\n")
                raise ValidationError("Billing period date must be smaller or equal than the next due date of the last invoice.")
            
            self.next_due_date = self.calculate_next_due_date(previous_due_date, subscription_duration)

            
            
            if self.pk:
                old_instance = StudentInvoice.objects.get(pk=self.pk)
                old_amount = old_instance.amount_paid
            else:
                old_amount = 0
        super(StudentInvoice, self).save(*args, **kwargs)

        # Update or create OrganizationInvoice based on the student invoice
        self.update_organization_invoice(old_amount)
        
        
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

        
        if org_invoice:
            # Update the amount in the existing organization invoice
            amount_difference = self.amount_paid - old_amount
            org_invoice.amount_paid += amount_difference
            org_invoice.save()
        
        else:
            print(self.next_due_date,"\n\n\n")
            OrganizationInvoice.objects.create(
                organization_subscription=self.organization_subscription,
                amount_payable=self.amount_payable,
                amount_paid=self.amount_paid,
                billing_period_date=self.billing_period_date,
                next_due_date=self.next_due_date
            )

