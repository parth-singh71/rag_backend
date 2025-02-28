from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Document, SelectedDocuments
from unittest.mock import patch


class DocumentUploadViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.upload_url = reverse("document-upload")
        self.test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf",
        )

    @patch("api.views.RAG.add_document")  # Mocking RAG processing
    def test_upload_document_success(self, mock_rag_add_document):
        mock_rag_add_document.return_value = None
        data = {
            "title": "Test Document",
            "file": self.test_file,
        }
        response = self.client.post(self.upload_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Document.objects.exists())

    def test_upload_invalid_file_format(self):
        test_file = SimpleUploadedFile(
            "test.txt",
            b"invalid format",
            content_type="text/plain",
        )
        data = {
            "title": "Test Document",
            "file": test_file,
        }
        response = self.client.post(self.upload_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenericDocumentsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.doc = Document.objects.create(title="Sample Document")
        self.list_url = reverse("documents-list")
        self.detail_url = reverse("document-detail", args=[self.doc.id])

    def test_get_all_documents(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_document(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DocumentSelectionViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_file = SimpleUploadedFile(
            "test.pdf",
            b"dummy content",
            content_type="application/pdf",
        )
        self.doc1 = Document.objects.create(title="Doc 1", file=self.test_file)
        self.doc2 = Document.objects.create(title="Doc 2", file=self.test_file)
        self.select_url = reverse("document-selection")

    @patch("api.views.RAG.clear_vectors")
    @patch("api.views.RAG.add_document")
    def test_select_documents_success(
        self, mock_rag_add_document, mock_rag_clear_vectors
    ):
        data = {"document_ids": [self.doc1.id, self.doc2.id]}
        response = self.client.post(self.select_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SelectedDocuments.objects.count(), 1)

    def test_get_selected_documents(self):
        SelectedDocuments.objects.create(selected_ids=[self.doc1.id])
        response = self.client.get(self.select_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("selected_documents", response.data)


class QnAViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.qna_url = reverse("qna")
        self.selected_doc = SelectedDocuments.objects.create(selected_ids=[1, 2])

    @patch("api.views.RAG.ask_question")
    def test_qna_success(self, mock_rag_ask_question):
        mock_rag_ask_question.return_value = "This is a test answer."
        data = {"question": "What is AI?"}
        response = self.client.post(self.qna_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("answer", response.data)
