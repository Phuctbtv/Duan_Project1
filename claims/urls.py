from django.urls import path
from . import views
from django.urls import path, include

from .views import custom_claims_admin

urlpatterns = [
    path('', custom_claims_admin, name='custom_claims_admin'),

]
