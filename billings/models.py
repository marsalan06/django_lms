from django.db import models
from django.conf import settings
from accounts.models import Organization
from django.db.models import Sum
# Create your models here.


class Subscription(models.Model):
    # Choices for the subscription name
    SUBSCRIPTION_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
    ]

    # Corresponding durations for the subscription choices
    DURATION_MAPPING = {
        'monthly': 1,
        'yearly': 12,
        'quarterly': 4,
        'half_yearly': 6,
    }

    name = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()

    def save(self, *args, **kwargs):
        # Automatically set the duration based on the name
        if self.name in self.DURATION_MAPPING:
            self.duration = self.DURATION_MAPPING[self.name]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
class OrganizationSubscription(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    date_of_subscription = models.DateField()

    def _str_(self):
        return f"{self.organization.name} - {self.subscription.name} ({self.date_of_subscription})"


class StudentInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=200, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Check if the instance is being updated
        if self.pk:
            old_instance = StudentInvoice.objects.get(pk=self.pk)
            old_amount = old_instance.amount
        else:
            old_amount = 0

        super(StudentInvoice, self).save(*args, **kwargs)
        self.update_organization_invoice(old_amount)

    def update_organization_invoice(self, old_amount):
        invoice_month = self.date.month
        invoice_year = self.date.year
        org_invoice = OrganizationInvoice.objects.filter(
            organization_subscription=self.organization_subscription,
            date__month=invoice_month,
            date__year=invoice_year
        ).first()

        if org_invoice:
            # Update the amount in the existing organization invoice
            amount_difference = self.amount - old_amount
            org_invoice.amount += amount_difference
            org_invoice.save()
        else:
            # Create a new OrganizationInvoice if none exists for the same month and year
            OrganizationInvoice.objects.create(
                organization_subscription=self.organization_subscription,
                total=self.total,
                amount=self.amount,
                date=self.date,
                payment_complete=self.payment_complete,
                payment_date=self.payment_date,
                invoice_code=self.invoice_code,
            )


 
class OrganizationInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    total = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=200, blank=True, null=True)