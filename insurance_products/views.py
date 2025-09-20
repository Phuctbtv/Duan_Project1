from django.shortcuts import render

from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import InsuranceProduct
def custom_products_admin(request):
    return render(request, 'admin/products_section.html')



