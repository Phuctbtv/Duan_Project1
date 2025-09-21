from django.urls import path
from django.contrib.auth import views as auth_views
from users.views import trangchu, login_view, register_view, custom_users_admin, custom_users_user, profile_view, \
    update_profile, change_password

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
]
