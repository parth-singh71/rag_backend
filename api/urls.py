from django.urls import path, include
from rest_framework import routers
from .views import (
    QnAView,
    DocumentUploadView,
    DocumentSelectionView,
    GenericDocumentsView,
)


urlpatterns = [
    path(
        "documents/upload/",
        DocumentUploadView.as_view(),
        name="document-upload",
    ),
    path(
        "documents/selection/",
        DocumentSelectionView.as_view(),
        name="document-selection",
    ),
    path("ask/", QnAView.as_view(), name="qna"),
    path("documents/", GenericDocumentsView.as_view(), name="documents-list"),
    path("documents/<int:id>/", GenericDocumentsView.as_view(), name="document-detail"),
]
