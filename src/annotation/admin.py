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


class EntryAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Entry."""

    list_display = ["entry_title_word", "entry_text_length"]

    def entry_title_word(self, entry):
        """Get the localized title word of the provided entry.

        Parameters
        ----------
        entry: models.Entry, required
            The entry object.

        Returns
        -------
        title_word: str
            The title word of the entry.
        """
        return entry.title_word

    def entry_text_length(self, entry):
        """Get the text length of the provided entry.

        Parameters
        ----------
        entry: models.Entry, required
            The entry object.

        Returns
        -------
        length: int
            The length of the text of the entry.
        """
        return entry.text_length

    entry_title_word.short_description = _("title word")
    entry_text_length.short_description = _("text length")


class EntryPageAdmin(admin.ModelAdmin):
    """Overrides the default admin options for EntryPage."""

    list_display = ["entry", "page"]
    list_filter = ["page"]


class AnnotationAdmin(admin.ModelAdmin):
    """Overrides the default admin options for Annotation."""

    list_display = ["entry", "annotation_text_length", "user", "status"]
    list_filter = ["status", "user"]
    ordering = ["entry"]

    def annotation_text_length(self, annotation):
        """Get the text length of the provided annotation.

        Parameters
        ----------
        annotation: models.Annotation, required
            The annotation object.

        Returns
        -------
        length: int
            The length of the annotation text.
        """
        return annotation.text_length

    annotation_text_length.short_description = _("text length")


admin.site.register(Volume, VolumeAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryPage, EntryPageAdmin)

admin.site.site_url = reverse_lazy('annotation:index')
admin.site.index_title = _('Admin eDTLR data')
admin.site.site_header = _('Admin eDTLR data')
admin.site.site_title = _('Admin eDTLR data')
