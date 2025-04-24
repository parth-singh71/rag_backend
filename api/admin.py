from django.contrib import admin

from api.models import Document, SelectedDocuments


# Register your models here.
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin View for Document"""

    list_display = (
        "title",
        "uploaded_by",
        "uploaded_at",
        "file",
    )
    list_filter = (
        "uploaded_at",
        "uploaded_by",
    )


@admin.register(SelectedDocuments)
class SelectedDocumentsAdmin(admin.ModelAdmin):
    """Admin View for SelectedDocuments"""

    list_display = (
        "selected_ids",
        "created_at",
        "user",
    )
    list_filter = ("created_at", "user")
