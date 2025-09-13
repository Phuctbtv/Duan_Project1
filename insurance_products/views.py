from django.shortcuts import render

def custom_products_admin(request):
    return render(request, 'admin/products_section.html')
