
from django.shortcuts import redirect

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_staff:
            return redirect("trangchu")
        return view_func(request, *args, **kwargs)
    return wrapper
def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.is_staff:
            return redirect("admin_home")
        return view_func(request, *args, **kwargs)
    return wrapper
