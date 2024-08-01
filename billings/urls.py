from .views import  billing
from django.urls import path, include


urlpatterns = [
    
    path("billing/", billing, name="billing"),
]