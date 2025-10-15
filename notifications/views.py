from django.shortcuts import render

def support_users(request):
    return render(request, "support/support_user.html")
