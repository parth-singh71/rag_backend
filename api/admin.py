from django.contrib import admin

from api.models import Document, SelectedDocuments


# Register your models here.
@admin.register(Document)
class UserSkillAdmin(admin.ModelAdmin):
    """Admin View for UserSkill"""

    list_display = ("title", "uploaded_at", "file")
    list_filter = ("uploaded_at",)


@admin.register(SelectedDocuments)
class UserEducationAdmin(admin.ModelAdmin):
    """Admin View for UserEducation"""

    list_display = (
        "selected_ids",
        "created_at",
    )
    list_filter = ("created_at",)
