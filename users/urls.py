from django.urls import path
from django.contrib.auth import views as auth_views
from users.views import trangchu, login_view, register_view

urlpatterns = [
    path("", trangchu, name="trangchu"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(next_page="trangchu"), name="logout"),
]
