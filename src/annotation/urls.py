from django.urls import path

from . import views

app_name = "annotation"
urlpatterns = [path("", views.validate, name="index")]
