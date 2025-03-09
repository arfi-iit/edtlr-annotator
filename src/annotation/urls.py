from django.urls import path

from . import views

app_name = "annotation"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("new", views.NewAnnotatioView.as_view(), name="new-annotation"),
    path("<int:id>", views.AnnotateView.as_view(), name="annotate"),
    path("api/entries/<int:entry_id>",
         views.GetEntryContentsView.as_view(),
         name="get-entry"),
    path("complete",
         views.MarkAnnotationCompleteView.as_view(),
         name="mark-complete"),
    path("save", views.SaveAnnotationView.as_view(), name="save"),
    path("thank-you", views.thank_you, name="thank-you"),
]
