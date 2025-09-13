from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from users.decorators import admin_required
from users.models import User

@admin_required
def admin_home(request):
    return render(request, "admin/dashboard_section.html")



# def user_detail(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     return render(request, "admin/user_detail.html", {"user": user})

# def user_edit(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     if request.method == "POST":
#         form = UserEditForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()
#             return redirect("user_list")
#     else:
#         form = UserEditForm(instance=user)
#     return render(request, "admin/user_edit.html", {"form": form, "user": user})



