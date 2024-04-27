"""Defines the views of the application."""
from .models import Page, Annotation, EntryPage, Entry
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404, HttpRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from typing import Tuple
# Create your views here.


@login_required
def thank_you(request):
    """Render a thank you message when there are no pages to annotate."""
    return render(request, "annotation/thank-you.html")


MAX_CONCURRENT_ANNOTATORS = int(
    getattr(settings, "MAX_CONCURRENT_ANNOTATORS", 2))


def get_image_path(page: Page | None) -> str:
    """Get the image path of the specified page.

    Parameters
    ----------
    page: Page, required
        The page for which to get the image path.

    Returns
    -------
    image_path: str or None
        The image path of the image, or None if the page is None.
    """
    if page is None:
        return None
    return f'/static/annotation/{page.image_path}'


class IndexView(LoginRequiredMixin, View):
    """Implements the index view."""

    template_name = "annotation/index.html"
    thank_you_page = 'annotation:thank-you'

    def get(self, request):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        user_id = request.user.id
        current_annotation = self.__get_in_progress_annotation(user_id)
        if current_annotation is not None:
            return render(request,
                          self.template_name,
                          context=self.__build_template_context(
                              current_annotation.entry))

        entry = self.__get_next_entry(request.user)
        if entry is not None:
            record = self.__insert_annotation(request.user, entry)
            return render(request,
                          self.template_name,
                          context=self.__build_template_context(entry))

        return redirect(self.thank_you_page)

    def __get_next_entry(self, user: User) -> Page | None:
        in_progress_annotations = Annotation.objects.values('entry')\
                                                    .annotate(count=Count('entry'))\
                                                    .order_by('entry')\
                                                    .filter(count__lt=MAX_CONCURRENT_ANNOTATORS)

        user_annotations = Annotation.objects.filter(user=user)\
                                             .values('entry')
        user_annotations = set([a['entry'] for a in user_annotations])

        for annotation in in_progress_annotations:
            entry_id = annotation['entry']
            if entry_id not in user_annotations:
                return Entry.objects.get(pk=entry_id)

        in_progress_entries = [
            p['entry'] for p in Annotation.objects.values('entry')
        ]

        return Entry.objects.exclude(id__in=in_progress_entries).first()

    def __insert_annotation(self, user: User, entry: Entry) -> Annotation:
        status = Annotation.AnnotationStatus.IN_PROGRESS
        record = Annotation(entry=entry, user=user, status=status)
        record.text = entry.text
        record.version = 1
        record.save()
        return record

    def __build_template_context(self, entry: Entry) -> dict:
        entry_pages = EntryPage.objects.filter(entry=entry)
        page_images = [get_image_path(e.page) for e in entry_pages]
        return {'entry_id': entry.id, 'page_images': page_images}

    def __get_in_progress_annotation(self, user_id: int) -> Annotation | None:
        status = Annotation.AnnotationStatus.IN_PROGRESS
        return Annotation.objects.filter(user_id=user_id,status=status)\
                                 .first()


class GetEntryContentsView(LoginRequiredMixin, View):
    """Implements the view for retrieving the contents of the specified entry."""

    def get(self, request, entry_id: int) -> JsonResponse | Http404:
        """Retrieve the contents for the specified entry.

        Parameters
        ----------
        request: HttpRequest, required
            The HttpRequest object.
        entry_id: int, required
            The id of the entry for which to load the data.

        Returns
        -------
        response: JsonResponse or Http404
            The response data.
            If the response is a JsonResponse, then it contains the following fields:
            - 'contents': the text of the entry
        """
        try:
            user_id = request.user.id
            entry = Entry.objects.get(pk=entry_id)
            annotation = Annotation.objects.filter(entry=entry,
                                                   user=request.user).first()

            entry_page = EntryPage.objects.filter(entry=entry)\
                                            .first()

            data = {
                'contents': annotation.text,
                'current_page': self.__get_image_path(entry_page.page),
                'previous_page': None,
                'next_page': None
            }
            return JsonResponse(data)
        except (Page.DoesNotExist, Annotation.DoesNotExist):
            raise Http404()

    def __get_image_path(self, page: Page | None) -> str | None:
        """Get the image path of the specified page.

        Parameters
        ----------
        page: Page, required
            The page for which to get the image path.

        Returns
        -------
        image_path: str or None
            The image path of the image, or None if the page is None.
        """
        return get_image_path(page)


class SaveAnnotationView(LoginRequiredMixin, View):
    """Implements the view for saving an annotation."""

    index_page = "annotation:index"

    def post(self, request):
        """Save the annotation from the request body.

        Parameters
        ----------
        request: HttpRequest, required
            The HTTP request object.
        """
        entry_id, text = self.__parse_request_body(request)
        annotation = Annotation.objects.get(
            entry=entry_id,
            user=request.user,
            status=Annotation.AnnotationStatus.IN_PROGRESS)
        if annotation is not None:
            annotation.text = text
            annotation.version = annotation.version + 1
            annotation.save()
        return redirect(self.index_page)

    def __parse_request_body(self, request) -> Tuple[int, HttpRequest]:
        text = request.POST['text']
        entry_id = int(request.POST['entry-id'])
        return entry_id, text


class MarkAnnotationCompleteView(LoginRequiredMixin, View):
    """Implements the view for marking an annotation as being complete."""

    index_page = "annotation:index"

    def post(self, request):
        """Save the annotation from the request body and mark it as complete."""
        entry_id, contents = self.__parse_request_body(request)
        self.__mark_annotation_complete(entry_id, contents, request.user)
        self.__check_conflicts(entry_id)
        return redirect(self.index_page)

    def __check_conflicts(self, entry_id: int):
        entry_annotations = Annotation.objects.filter(
            entry=entry_id, status=Annotation.AnnotationStatus.COMPLETE)
        if len(entry_annotations) < MAX_CONCURRENT_ANNOTATORS:
            return

        if self.__have_conflicts(entry_annotations):
            for annotation in entry_annotations:
                annotation.version = annotation.version + 1
                annotation.status = Annotation.AnnotationStatus.CONFLICT
                annotation.save()

    def __have_conflicts(self, entry_annotations) -> bool:
        iterator = iter(entry_annotations)

        first = next(iterator).text
        for item in iterator:
            if first != item.text:
                return True

        return False

    def __mark_annotation_complete(self, entry_id: int, text: str, user: User):
        annotation = Annotation.objects.get(
            entry=entry_id,
            user=user,
            status=Annotation.AnnotationStatus.IN_PROGRESS)

        if annotation is not None:
            annotation.text = text
            annotation.version = annotation.version + 1
            annotation.status = Annotation.AnnotationStatus.COMPLETE
            annotation.save()

    def __parse_request_body(self, request) -> Tuple[int, object]:
        text = request.POST['text']
        entry_id = int(request.POST['entry-id'])
        return entry_id, text
