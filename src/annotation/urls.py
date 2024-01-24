from django.urls import path

from . import views

app_name = "annotation"
urlpatterns = [
    path("", views.validate, name="index"),
    path("api/ocrresults", views.get_ocr_result, name="get_ocr_result")
]
