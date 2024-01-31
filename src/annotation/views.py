from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import Http404
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from .models import Page, Annotation
# Create your views here.


@login_required
def thank_you(request):
    return render(request, "annotation/thank-you.html")


@login_required
def validate(request):
    return render(request, "annotation/validate.html", context={'page_id': 1})


@login_required
def get_page(request, page_id: int):
    try:
        user_id = request.user.id
        page = Page.objects.get(pk=page_id)
        annotation = Annotation.objects.filter(page_id=page_id,
                                               user_id=user_id).first()
        data = {
            'text': page.text,
            'content': annotation.content,
            'image_path': f'/static/annotation/{page.image_path}'
        }
        return JsonResponse(data)
    except (Page.DoesNotExist, Annotation.DoesNotExist):
        raise Http404()


@login_required
def save_annotation(request):
    return redirect("annotation:index")


@login_required
def mark_valid(request):
    return redirect("annotation:index")
