from django.shortcuts import render

# Create your views here.
def billing(request):
    context={}
    return render(request, "billing/billing.html", context)
