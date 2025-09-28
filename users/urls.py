from django.urls import path
from django.contrib.auth import views as auth_views
from users.views import trangchu, login_view, register_view, custom_users_admin, custom_users_user, profile_view, \
    update_profile, change_password, CustomPasswordResetConfirmView

urlpatterns = [
    path("", trangchu, name="trangchu"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(next_page="trangchu"), name="logout"),
    path("quanlytaikhoan/",custom_users_user , name="custom_users_user"),
    path("custom_user/", custom_users_admin, name="custom_users_admin"),
    path("profile/",profile_view, name="custom_profile_user"),
    path("profile/update_profile",update_profile, name="update_profile"),
    path("profile/change_password",change_password, name="change_password"),

# Form nhập email để reset
    path("reset_password/",
         auth_views.PasswordResetView.as_view(template_name="users/components/registration/password_reset.html",
          email_template_name="users/components/registration/password_reset_email.txt",
          subject_template_name="users/components/registration/password_reset_subject.txt"
          ),
         name="reset_password"),

    # Thông báo đã gửi email
    path("reset_password_sent/",
         auth_views.PasswordResetDoneView.as_view(template_name="users/components/registration/password_reset_done.html"),
         name="password_reset_done"),

    # Link trong email → xác nhận
    path("reset/<uidb64>/<token>/",
            CustomPasswordResetConfirmView.as_view(),name="password_reset_confirm"),

    # Hoàn tất reset
    path("reset_password_complete/",
         auth_views.PasswordResetCompleteView.as_view(template_name="users/components/registration/password_reset_complete.html"),
         name="password_reset_complete"),
]
