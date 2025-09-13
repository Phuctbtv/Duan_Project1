from django.urls import path
from . import views
from django.urls import path, include

from .views import custom_products_admin

urlpatterns = [
    path('', custom_products_admin, name='custom_products_admin'),

]
