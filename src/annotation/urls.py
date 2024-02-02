from django.urls import path

from . import views

app_name = "annotation"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("api/pages/<int:page_id>", views.get_page, name="get-page"),
    path("validate", views.mark_valid, name="mark-valid"),
    path("save", views.SaveAnnotationView.as_view(), name="save"),
    path("thank-you", views.thank_you, name="thank-you"),
]
