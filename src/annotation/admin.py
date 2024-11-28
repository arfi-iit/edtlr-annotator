"""Register the models for the admin site."""
from .models import Annotation
from .models import Entry
from .models import Page
from .models import EntryPage
from .models import Volume
from django.contrib import admin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


# Register your models here.
class VolumeAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Volume."""

    list_display = ["id", "name"]


class PageAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Page."""

    list_display = ["volume", "page_no", "image_path"]
    list_filter = ["volume"]


class EntryPageAdmin(admin.ModelAdmin):
    """Overrides the default admin options for EntryPage."""

    list_display = ["entry", "page"]
    list_filter = ["page"]


class AnnotationAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Annotation."""

    list_display = ["entry", "user", "status"]
    list_filter = ["status", "user"]
    ordering = ["entry"]


admin.site.register(Volume, VolumeAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Entry)
admin.site.register(EntryPage, EntryPageAdmin)

admin.site.site_url = reverse_lazy('annotation:index')
admin.site.index_title = _('Admin eDTLR data')
admin.site.site_header = _('Admin eDTLR data')
admin.site.site_title = _('Admin eDTLR data')
