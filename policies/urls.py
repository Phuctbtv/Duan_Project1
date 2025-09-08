from django.urls import path
from . import views
from django.urls import path, include
urlpatterns = [
    path('', views.customer_policies_admin, name='customer_policies_admin'),

]
