"""Register the models for the admin site."""
from .models import Annotation
from .models import Entry
from .models import Page
from .models import EntryPage
from .models import Volume
from django.contrib import admin

# Register your models here.
admin.site.register(Volume)
admin.site.register(Page)
admin.site.register(Annotation)
admin.site.register(Entry)
admin.site.register(EntryPage)
