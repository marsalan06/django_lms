from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, date
from django.utils import timezone
from accounts.models import Organization
from .models import OrganizationSubscription, OrganizationInvoice, StudentInvoice
from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.models import User
from decimal import Decimal




def add_months(date, months):
    """Add a number of months to a given date."""
    new_month = date.month + months
    new_year = date.year + (new_month - 1) // 12
    new_month = (new_month - 1) % 12 + 1
    return date.replace(year=new_year, month=new_month, day=min(date.day, 28))




def payment_check_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user and user.student:
            # Access the related organization of the user
            
            if(user.organization):
                organization = user.organization
            
               
                current_date = timezone.now().date()

                organization_subscription = OrganizationSubscription.objects.filter(
                organization=user.organization
                ).first() 
                if organization_subscription: 
                    latest_invoice = StudentInvoice.objects.filter(
                        user=user,
                        organization_subscription=organization_subscription
                    ).order_by('-billing_period_date').first()
                    
                    if latest_invoice:
                        if latest_invoice.next_due_date and latest_invoice.next_due_date < current_date:
                            return redirect("billing") 
                    else:
                        # No invoice found, calculate the next_due_date based on subscription and its duration
                        subscription = organization_subscription.subscription
                        subscription_duration_months = subscription.duration

                        subscription_start_date = organization_subscription.date_of_subscription

                        next_due_date = subscription_start_date + timedelta(days=subscription_duration_months * 30)
                        
                        if next_due_date < current_date:
                            return redirect("billing") 
                        

                    
                    latest_invoice = OrganizationInvoice.objects.filter(
                    organization_subscription=organization_subscription
                    ).order_by('-billing_period_date').first()
                    
                    current_date = timezone.now().date()
                    if latest_invoice:
                        if latest_invoice.next_due_date and latest_invoice.next_due_date < current_date:
                            return redirect("billing")   
                        
                        # Check if amount_paid is less than 75% of amount_payable
                        if latest_invoice.amount_paid and latest_invoice.amount_payable:
                            if latest_invoice.amount_paid < 0.75 * latest_invoice.amount_payable:
                                print("Amount paid is less than 75% of the amount payable.")
                                return redirect("billing")  

                    else:
                        # No invoice found, calculate the next_due_date based on subscription and its duration
                        subscription = organization_subscription.subscription
                        subscription_duration_months = subscription.duration

                        subscription_start_date = organization_subscription.date_of_subscription

                        next_due_date = subscription_start_date + timedelta(days=subscription_duration_months * 30)

                        if next_due_date < current_date:
                            return redirect("billing") 

                    
                else:
                    print("No subscription found for this organization.")

                
                
                
                
        return view_func(request, *args, **kwargs)

    return wrapper
