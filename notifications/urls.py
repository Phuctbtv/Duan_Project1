from django.urls import path

from notifications.views import support_users

urlpatterns = [
    path("", support_users, name="support_users"),

]
