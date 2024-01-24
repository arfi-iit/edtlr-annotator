from django.shortcuts import render
from django.http import JsonResponse
from django.conf.urls.static import static
from .models import OcrResult


# Create your views here.
def validate(request):
    return render(request, "annotation/validate.html")


def get_ocr_result(request):
    model = OcrResult.objects.get(pk=128)
    data = {
        'text': model.text,
        'image_path': f'/static/annotation/{model.image_path}'
    }
    return JsonResponse(data)
