from django.db import models
from django.core.validators import FileExtensionValidator
from users.models import User


# Create your models here.
class Document(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to="documents/", validators=[FileExtensionValidator(["pdf"])]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class SelectedDocuments(models.Model):
    selected_ids = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Selected Documents for {self.user} - {self.selected_ids}"

    class Meta:
        verbose_name = "Selected Documents"
        verbose_name_plural = "Selected Documents"
