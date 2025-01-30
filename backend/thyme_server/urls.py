from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('printrun/', include('printrun.urls')),  # Include the printrun app's URLs
]