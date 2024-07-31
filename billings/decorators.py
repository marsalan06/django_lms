from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, date
from django.utils import timezone

# from dateutil.relativedelta import relativedelta
from accounts.models import Organization
from .models import OrganizationSubscription, OrganizationInvoice, StudentInvoice
from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.models import User
from decimal import Decimal

# def organizationtransaction_check_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         user_profile = request.user
#         organization = get_object_or_404(Organization, user=user_profile)

#         organization_subscriptions = OrganizationSubscription.objects.filter(organization=organization)
#         # print("SHIT\n\n\n\n\n")
#         total_students = User.objects.filter(organization=organization,is_student=True).count()

#         for subscription in organization_subscriptions:
#             start_date = subscription.date_of_subscription
#             end_date = date.today()
#             current_date = start_date
            
#             amount = subscription.subscription.price
#             total_amount=amount*total_students
#             while current_date <= end_date:
#                 month_str = current_date.strftime("%Y-%m-%d")
#                 end_month=end_date.strftime("%Y-%m-%d")
#                 end_object= datetime.strptime(end_month, '%Y-%m-%d').date()
#                 date_obj = datetime.strptime(month_str, '%Y-%m-%d').date()
#                 transaction_count = OrganizationInvoice.objects.filter(
#                     organizationsubscription=subscription,
#                     month__month=date_obj.month,
#                 ).count()
#                 if(end_object.month!=date_obj.month or (end_object.month==date_obj.month and date_obj.day<end_object.day) ):
                
#                     if transaction_count == 0:
#                         redirect_url= reverse('organization_view_paymenthistory') + '?alert=clear_dues'
                        
#                         return redirect(redirect_url)
                    
#                     transaction = OrganizationInvoice.objects.filter(
#                         organizationsubscription=subscription,
#                         month__month=date_obj.month,
#                     ).first()
#                     if(transaction_count!=0):
#                         # print(transaction.amount,transaction.id)
#                         payment=transaction.amount
#                         total_amount_float = float(total_amount)
#                         if(payment<(.75*total_amount_float)):
#                             redirect_url= reverse('login') + '?alert=less_payment'
                            
#                             return redirect(redirect_url)

#                 current_date += relativedelta(months=1)
                
#         # If no condition is met, continue with the original view function
#         return view_func(request, *args, **kwargs)

#     return wrapper





# def studentorganizationtransaction_check_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         user = request.user
#         user_profile = get_object_or_404(UserProfile, user=user)
#         student = get_object_or_404(Student, user_profile=user_profile)
#         organization = student.organization
#         organization_subscriptions = OrganizationSubscription.objects.filter(organization=organization)
#         total_students = Student.objects.filter(organization=organization).count()

#         for subscription in organization_subscriptions:
#             start_date = subscription.date_of_subscription
#             end_date = date.today()
#             current_date = start_date
            
#             amount = subscription.subscription.price
#             total_amount=amount*total_students
#             while current_date <= end_date:
#                 month_str = current_date.strftime("%Y-%m-%d")
#                 date_obj = datetime.strptime(month_str, '%Y-%m-%d').date()
                
#                 end_month=end_date.strftime("%Y-%m-%d")
#                 end_object= datetime.strptime(end_month, '%Y-%m-%d').date()
#                 transaction_count = OrganizationInvoice.objects.filter(
#                     organizationsubscription=subscription,
#                     month__month=date_obj.month,
#                 ).count()
#                 if(end_object.month!=date_obj.month or (end_object.month==date_obj.month and date_obj.day<end_object.day) ):

#                     if transaction_count == 0:
#                         # Redirect to student_view_paymenthistory if more than 1 payment exists
#                         redirect_url= reverse('login') + '?alert=organization_clear_dues'
                        
#                         return redirect(redirect_url)
                    
#                     transaction = OrganizationInvoice.objects.filter(
#                         organizationsubscription=subscription,
#                         month__month=date_obj.month,
#                     ).first()
#                     if(transaction_count!=0):
#                         # print(transaction.amount,transaction.id)
#                         # print("\n\n\n\najeeb")
#                         payment=transaction.amount
#                         total_amount_float = float(total_amount)
#                         if(payment<(.75*total_amount_float)):
#                             redirect_url= reverse('login') + '?alert=less_payment'
                            
#                             return redirect(redirect_url)

#                 current_date += relativedelta(months=1)
                
#         # If no condition is met, continue with the original view function
#         return view_func(request, *args, **kwargs)

#     return wrapper



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
            
            organization = user.organization
            
            if organization:    
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
                            # Redirect if the next_due_date is less than the current date
                            print("user default 1")
                            return redirect("/billing/billing")  # Replace 'some_view_name' with the name of your view or URL pattern
                    else:
                        # No invoice found, calculate the next_due_date based on subscription and its duration
                        subscription = organization_subscription.subscription
                        subscription_duration_months = subscription.duration

                        # Assuming the subscription start date is when the OrganizationSubscription was created
                        subscription_start_date = organization_subscription.date_of_subscription

                        # Calculate next_due_date based on the subscription duration
                        next_due_date = subscription_start_date + timedelta(days=subscription_duration_months * 30)
                        
                        if next_due_date < current_date:
                            print("user default 2")
                            # Redirect if the calculated next_due_date is less than the current date
                            return redirect("/billing/billing") 
                        

                    
                    latest_invoice = OrganizationInvoice.objects.filter(
                    organization_subscription=organization_subscription
                    ).order_by('-billing_period_date').first()
                    
                    current_date = timezone.now().date()
                    if latest_invoice:
                        if latest_invoice.next_due_date and latest_invoice.next_due_date < current_date:
                            # Redirect if the next_due_date is less than the current date
                            print("organization default 1")
                            return redirect("/billing/billing")   # Replace 'some_view_name' with the name of your view or URL pattern
                        
                        # Check if amount_paid is less than 75% of amount_payable
                        if latest_invoice.amount_paid and latest_invoice.amount_payable:
                            if latest_invoice.amount_paid < 0.75 * latest_invoice.amount_payable:
                                # Handle case where amount_paid is less than 75% of amount_payable
                                print("Amount paid is less than 75% of the amount payable.")
                                return redirect("/billing/billing")   # Replace with appropriate view or URL pattern

                    else:
                        # No invoice found, calculate the next_due_date based on subscription and its duration
                        subscription = organization_subscription.subscription
                        subscription_duration_months = subscription.duration

                        # Assuming the subscription start date is when the OrganizationSubscription was created
                        subscription_start_date = organization_subscription.date_of_subscription

                        # Calculate next_due_date based on the subscription duration
                        next_due_date = subscription_start_date + timedelta(days=subscription_duration_months * 30)

                        if next_due_date < current_date:
                            print("organization default 2")
                            # Redirect if the calculated next_due_date is less than the current date
                            return redirect("/billing/billing")  # Replace 'some_view_name' with the name of your view or URL pattern

                    
                else:
                    # Handle case where the user has no associated organization
                    print("No subscription found for this organization.")

                
                
                
                
        # Continue with the original view function
        return view_func(request, *args, **kwargs)

    return wrapper
