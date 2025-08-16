from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request,'trangchu.html')
def login_view(request):
    return render(request, 'users/login.html')