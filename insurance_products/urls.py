from django.urls import path
from . import views
from django.urls import path, include

from .views import customer_products_admin

urlpatterns = [
    path('', customer_products_admin, name='customer_products_admin'),

]
