from django.contrib import admin
from .models import Volume
from .models import Page
from .models import Annotation

# Register your models here.
admin.site.register(Volume)
admin.site.register(Page)
admin.site.register(Annotation)
