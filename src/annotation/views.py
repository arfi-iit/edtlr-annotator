from django.shortcuts import render


# Create your views here.
def validate(request):
    return render(request, "annotation/validate.html",
                  {'image_path': 'annotation/data/128.png'})
