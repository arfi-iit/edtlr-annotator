from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf.urls.static import static
from .models import OcrResult


# Create your views here.
def validate(request):
    return render(request, "annotation/validate.html")


def get_ocr_result(request, page_no: int):
    model = OcrResult.objects.get(pk=page_no)
    data = {
        'text': model.text,
        'image_path': f'/static/annotation/{model.image_path}'
    }
    return JsonResponse(data)


def save_annotation(request):
    return redirect("annotation:index")


def mark_valid(request):
    return redirect("annotation:index")
