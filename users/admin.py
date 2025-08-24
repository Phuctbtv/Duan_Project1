from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    # Trường hiển thị ngoài list
    list_display = ("username", "email", "first_name", "last_name", "user_type", "is_staff")
    list_filter = ("user_type", "is_staff", "is_superuser", "is_active")

    # Trường để tìm kiếm
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")

    # Sắp xếp
    ordering = ("username",)

    # Tùy chỉnh form hiển thị khi edit user
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin cá nhân",
         {"fields": ("first_name", "last_name", "email", "phone_number", "address", "date_of_birth")}),
        ("Loại người dùng", {"fields": ("user_type",)}),
        ("Phân quyền", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Thời gian", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )

    # Form khi tạo user mới trong admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "user_type", "phone_number", "password1",
                       "password2"),
        }),
    )
