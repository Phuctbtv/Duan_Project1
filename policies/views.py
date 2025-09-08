from django.shortcuts import render

def customer_policies_admin(request):
    return render(request, 'admin/policies_section.html')
