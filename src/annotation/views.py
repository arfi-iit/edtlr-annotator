"""Defines the views of the application."""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import Http404
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from .models import Page, Annotation
from django.db.models import Count
import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from typing import Tuple
# Create your views here.


@login_required
def thank_you(request):
    return render(request, "annotation/thank-you.html")


MAX_CONCURRENT_ANNOTATORS = 2


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
                              current_annotation.page_id.id))

        page = self.__get_next_page(request.user)
        if page is not None:
            record = self.__insert_annotation(request.user, page)
            return render(request,
                          self.template_name,
                          context=self.__build_template_context(page.id))

        return redirect(self.thank_you_page)

    def __get_next_page(self, user) -> Page | None:
        in_progress_annotations = Annotation.objects.values('page_id')\
                                                    .annotate(count=Count('page_id'))\
                                                    .order_by('page_id')\
                                                    .filter(count__lt=MAX_CONCURRENT_ANNOTATORS)
        user_annotations = Annotation.objects.filter(user_id=user)\
                                             .values('page_id')
        user_annotations = set([a['page_id'] for a in user_annotations])

        for annotation in in_progress_annotations:
            page_id = annotation['page_id']
            if page_id not in user_annotations:
                return Page.objects.get(pk=in_progress_annotations['page_id'])

        in_progress_pages = [
            p['page_id'] for p in Annotation.objects.values('page_id')
        ]

        return Page.objects.exclude(id__in=in_progress_pages).first()

    def __insert_annotation(self, user, page: Page) -> Annotation:
        status = Annotation.AnnotationStatus.IN_PROGRESS
        record = Annotation(page_id=page, user_id=user, status=status)
        record.contents = json.dumps({'ops': [{'insert': page.text}]})
        record.version = 1
        record.save()
        return record

    def __build_template_context(self, page_id: int) -> dict:
        return {'page_id': page_id}

    def __get_in_progress_annotation(self, user_id: int) -> Annotation | None:
        status = Annotation.AnnotationStatus.IN_PROGRESS
        return Annotation.objects.filter(user_id=user_id,status=status)\
                                 .first()


@login_required
def get_page(request, page_id: int):
    try:
        user_id = request.user.id
        page = Page.objects.get(pk=page_id)
        annotation = Annotation.objects.filter(page_id=page_id,
                                               user_id=user_id).first()
        data = {
            'contents': annotation.contents,
            'image_path': f'/static/annotation/{page.image_path}'
        }
        return JsonResponse(data)
    except (Page.DoesNotExist, Annotation.DoesNotExist):
        raise Http404()


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
        page_id, contents = self.__parse_request_body(request)
        annotation = Annotation.objects.get(
            page_id=page_id,
            user_id=request.user,
            status=Annotation.AnnotationStatus.IN_PROGRESS)
        if annotation is not None:
            annotation.contents = json.dumps(contents)
            annotation.version = annotation.version + 1
            annotation.save()
        return redirect(self.index_page)

    def __parse_request_body(self, request) -> Tuple[int, object]:
        contents = json.loads(request.POST['contents'])
        page_id = int(request.POST['page-id'])
        return page_id, contents


@login_required
def mark_valid(request):
    return redirect("annotation:index")
