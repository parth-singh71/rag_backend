from django.db import models
from django.core.validators import FileExtensionValidator


# Create your models here.
class Document(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to="documents/", validators=[FileExtensionValidator(["pdf"])]
    )


class SelectedDocuments(models.Model):
    selected_ids = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Selected Documents {self.id} - {self.selected_ids}"
