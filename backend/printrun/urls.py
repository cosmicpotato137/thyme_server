from django.urls import path
from . import views

urlpatterns = [
    path('', views.printrun_view, name='printrun'),
]