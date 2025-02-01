from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("publicapp.urls")),
    path("printrun/", include("printrun.urls")),
]
