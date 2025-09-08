from django.shortcuts import render

def customer_products_admin(request):
    return render(request, 'admin/products_section.html')
