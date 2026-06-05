from django.urls import path
from . import views

urlpatterns = [
    path("log", views.create_log),
    path("logs/<str:client_id>", views.get_logs)
]