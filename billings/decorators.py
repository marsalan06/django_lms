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
        if user.is_student:
            # Access the related organization of the user
            organization = user.organization
            
            if organization: 
                try:
                    # Access OrganizationSubscription related to the user's organization
                    organization_subscription = organization.organizationsubscription
                    
                    # Example: Print or use the subscription in some way
                    print(f"Subscription: {organization_subscription.subscription.name}, Start Date: {organization_subscription.date_of_subscription}")
                     # Extract date_of_subscription and subscorganization_subscriptionription duration
                    date_of_subscription = organization_subscription.date_of_subscription
                    subscription_duration = organization_subscription.subscription.duration
                    
                    # Print or use the variables as needed
                    print(f"Date of Subscription: {date_of_subscription}")
                    print(f"Subscription Duration: {subscription_duration}")
                    current_date = timezone.now().date()
                                    
                    payment_dates = []
                    next_payment_date = date_of_subscription
                    
                    while next_payment_date <= current_date:
                        payment_dates.append(next_payment_date)
                        next_payment_date = add_months(next_payment_date, subscription_duration)

                    existing_invoices = StudentInvoice.objects.filter(
                        user=user,
                        organization_subscription=organization_subscription
                    ).values_list('date', flat=True)
                    existing_invoice_dates = [invoice_date for invoice_date in existing_invoices]
                    
                    print(payment_dates)
                    print(existing_invoice_dates)
                    payment_dates=payment_dates[:-1]
                    missing_dates=[]
                    # Find missing payment dates
                    payment_dates_month_year = [(date.year, date.month) for date in payment_dates]
                    existing_invoice_dates_month_year = [(date.year, date.month) for date in existing_invoice_dates]

                    # Find missing payment months
                    missing_dates = [
                        (year, month) for year, month in payment_dates_month_year
                        if (year, month) not in existing_invoice_dates_month_year
                    ]

                    # missing_dates = [date for date in existing_invoice_dates if date not in payment_dates]
                   
                    
                    # Print missing dates
                    for date in missing_dates:
                        print(f"Missing invoice for {date}")
                    if(len(missing_dates)>0):
                        return redirect("/programs/my_courses/")
                except OrganizationSubscription.DoesNotExist:
                    # Handle case where no OrganizationSubscription exists
                    print("No subscription found for this organization.")
            else:
                # Handle case where the user has no associated organization
                print("User has no associated organization.")

            
            if organization: 
                try:
                    # Access OrganizationSubscription related to the user's organization
                    organization_subscription = organization.organizationsubscription

                    student_count = User.objects.filter(
                    organization=organization,
                    is_student=True
                    ).count()
                    print(student_count)
                    print(f"Subscription: {organization_subscription.subscription.name}, Start Date: {organization_subscription.date_of_subscription}")
                     # Extract date_of_subscription and subscorganization_subscriptionription duration
                    date_of_subscription = organization_subscription.date_of_subscription
                    subscription_duration = organization_subscription.subscription.duration
                    price = organization_subscription.subscription.price*student_count
                    
                    
                    # Print or use the variables as needed
                    print(f"Date of Subscription: {date_of_subscription}")
                    print(f"Subscription Duration: {subscription_duration}")
                    current_date = timezone.now().date()
                
                    payment_dates = []
                    next_payment_date = date_of_subscription
                    
                    while next_payment_date <= current_date:
                        payment_dates.append(next_payment_date)
                        next_payment_date = add_months(next_payment_date, subscription_duration)

                    existing_invoices = OrganizationInvoice.objects.filter(
                        organization_subscription=organization_subscription
                    ).values_list('date', 'amount')
                    existing_invoice_dates = [invoice_date for invoice_date, _ in existing_invoices]
                    amount = [amount for _, amount in existing_invoices]
                    
                    

                    print(amount)
                    print("noob\n\n")
                    # amount=amount[:-1]
                    
                    payment_dates=payment_dates[:-1]
                    missing_dates=[]
                    # Find missing payment dates
                    payment_dates_month_year = [(date.year, date.month) for date in payment_dates]
                    existing_invoice_dates_month_year = [(date.year, date.month) for date in existing_invoice_dates]

                    # Find missing payment months
                    missing_dates = [
                        (year, month) for year, month in payment_dates_month_year
                        if (year, month) not in existing_invoice_dates_month_year
                    ]

                    # missing_dates = [date for date in existing_invoice_dates if date not in payment_dates]
                
                    
                    # Print missing dates
                    for date in missing_dates:
                        print(f"Missing invoice for {date}")
                    if(len(missing_dates)>0):
                        return redirect("/billing")
                    this_month = datetime.now().month
                    this_year = datetime.now().year
                    for i in range(len(existing_invoice_dates_month_year)):
                        year, month = existing_invoice_dates_month_year[i]
                        
                        if year == this_year and month == this_month:
                            print("wowr")
                        else:
                            if amount[i] < Decimal(0.75) * price:
                                
                                return redirect("/billing/billing")
                                print(f"Price less then 75% for the month: {existing_invoice_dates[i]}")
                        
                except OrganizationSubscription.DoesNotExist:
                    # Handle case where no OrganizationSubscription exists
                    print("No subscription found for this organization.")
        # Continue with the original view function
        return view_func(request, *args, **kwargs)

    return wrapper
