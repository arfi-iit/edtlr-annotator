"""Register the models for the admin site."""
from annotation.models.annotation import Annotation
from annotation.models.entry import Entry
from annotation.models.entrypage import EntryPage
from annotation.models.page import Page
from annotation.models.reference import Reference
from annotation.models.volume import Volume
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
    search_fields = ["page_no__iexact", "image_path__icontains"]


class EntryAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Entry."""

    exclude = ["title_word", "title_word_normalized", "text_length"]
    list_display = ["title_word", "text_length"]
    search_fields = [
        "title_word__icontains", "title_word_normalized__icontains"
    ]


class EntryPageAdmin(admin.ModelAdmin):
    """Overrides the default admin options for EntryPage."""

    list_display = ["entry", "page"]
    list_filter = ["page"]


class AnnotationAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Annotation."""

    exclude = ["title_word", "title_word_normalized", "text_length"]
    list_display = ["entry", "title_word", "text_length", "user", "status"]
    list_filter = ["status", "user"]
    search_fields = [
        "title_word__icontains", "title_word_normalized__icontains"
    ]
    ordering = ["entry"]


class ReferenceAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Reference."""

    exclude = ["row_creation_timestamp"]
    list_filter = ["is_approved"]
    search_fields = ["text__icontains"]


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryPage, EntryPageAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Volume, VolumeAdmin)

admin.site.site_url = reverse_lazy('annotation:index')
admin.site.index_title = _('Admin eDTLR data')
admin.site.site_header = _('Admin eDTLR data')
admin.site.site_title = _('Admin eDTLR data')
