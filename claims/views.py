from django.shortcuts import render

def custom_claims_admin(request):
    return render(request, 'admin/claims_section.html')
