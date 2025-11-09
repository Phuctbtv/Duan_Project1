from django.shortcuts import render

def about_us(request):
    return render(request, 'base/about_us.html')  # Thêm 'base/'

def contact(request):
    return render(request, 'base/contact.html')   # Thêm 'base/'