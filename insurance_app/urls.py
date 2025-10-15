from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', include('dashboard.urls')),
    path('insurance_products/', include('insurance_products.urls')),
    path("",include("users.urls")),
    path("custom_products/", include("insurance_products.urls")),
    path("custom_policies/", include("policies.urls")),
    path("payments/", include("payments.urls")),
    path("custom_claims/", include("claims.urls")),
    path("notification/", include("notifications.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)