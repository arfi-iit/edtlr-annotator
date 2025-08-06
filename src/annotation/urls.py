"""Defines the routing table of the application."""
from . import views
from django.urls import path

app_name = "annotation"
urlpatterns = [
    path("new", views.NewAnnotationView.as_view(), name="new-annotation"),
    path("<int:id>", views.AnnotateView.as_view(), name="annotate"),
    path("api/entries/<int:entry_id>",
         views.GetEntryContentsView.as_view(),
         name="get-entry"),
    path("complete",
         views.MarkAnnotationCompleteView.as_view(),
         name="mark-complete"),
    path("save", views.SaveAnnotationView.as_view(), name="save"),
    path("thank-you", views.ThankYouView.as_view(), name="thank-you"),
    path("", views.IndexView.as_view(), name="index"),
]
