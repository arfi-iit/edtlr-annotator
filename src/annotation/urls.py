from django.urls import path

from . import views

app_name = "annotation"
urlpatterns = [
    path("", views.validate, name="index"),
    path("api/ocrresults/<int:page_no>",
         views.get_ocr_result,
         name="get_ocr_result"),
    path("validate", views.mark_valid, name="mark-valid"),
    path("save", views.save_annotation, name="save"),
]
