from django.urls import path
from . import views
from django.urls import path, include

from .views import customer_claims_admin

urlpatterns = [
    path('', customer_claims_admin, name='customer_claims_admin'),

]
