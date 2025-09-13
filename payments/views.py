from django.shortcuts import render

# Create your views here.
def payments_users(request):
    return render(request, 'payments/payments_users.html')