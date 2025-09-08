from django.urls import path
from django.contrib.auth import views as auth_views
from users.views import trangchu, login_view, register_view, customer_users_admin, customer_users_user

urlpatterns = [
    path("", trangchu, name="trangchu"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(next_page="trangchu"), name="logout"),
    path("quanlytaikhoan/",customer_users_user , name="customer_users_user"),
    path("customer_user/", customer_users_admin, name="customer_users_admin"),
]
