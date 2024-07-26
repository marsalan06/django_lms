from django.db import models
from django.conf import settings
from accounts.models import Organization

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
 
class OrganizationInvoice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    total = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    date = models.DateField()
    payment_complete = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    invoice_code = models.CharField(max_length=200, blank=True, null=True)