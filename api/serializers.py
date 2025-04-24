from rest_framework import serializers
from .models import Document, SelectedDocuments


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "uploaded_at",
            "file",
        ]


class DocumentSelectionSerializer(serializers.Serializer):
    document_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )


class SelectedDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedDocuments
        fields = ["id", "selected_ids", "created_at"]


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    thread_id = serializers.CharField()
