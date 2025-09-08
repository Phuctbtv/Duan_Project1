from django.shortcuts import render

def customer_claims_admin(request):
    return render(request, 'admin/claims_section.html')
