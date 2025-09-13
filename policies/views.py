from django.shortcuts import render

def custom_policies_admin(request):
    return render(request, 'admin/policies_section.html')
def custom_policies_users(request):
    return render(request, 'users/policies_users.html')
