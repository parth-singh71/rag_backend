from users.models import User
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Document, SelectedDocuments
from unittest.mock import patch


class BaseAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


class DocumentUploadViewTest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.upload_url = reverse("document-upload")
        self.test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf",
        )

    @patch("RAG.data_injector.DataInjector.add_document")  # Mocking RAG processing
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
        data = {"title": "Test Document", "file": test_file}
        response = self.client.post(self.upload_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenericDocumentsViewTest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.doc = Document.objects.create(
            title="Sample Document",
            file=SimpleUploadedFile("sample.pdf", b"x"),
            uploaded_by=self.user,
        )
        self.list_url = reverse("documents-list")
        self.detail_url = reverse("document-detail", args=[self.doc.id])

    def test_get_all_user_documents(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_user_document(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.doc.id)


class DocumentSelectionViewTest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.test_file = SimpleUploadedFile(
            "test.pdf",
            b"dummy content",
            content_type="application/pdf",
        )
        self.doc1 = Document.objects.create(
            title="Doc 1", file=self.test_file, uploaded_by=self.user
        )
        self.doc2 = Document.objects.create(
            title="Doc 2", file=self.test_file, uploaded_by=self.user
        )
        self.select_url = reverse("document-selection")

    @patch("RAG.data_injector.DataInjector.clear_vectors")
    @patch("RAG.data_injector.DataInjector.add_document")
    def test_select_documents_success(
        self, mock_rag_add_document, mock_rag_clear_vectors
    ):
        data = {"document_ids": [self.doc1.id, self.doc2.id]}
        response = self.client.post(self.select_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SelectedDocuments.objects.filter(user=self.user).count(), 1)

    def test_get_selected_documents(self):
        SelectedDocuments.objects.create(user=self.user, selected_ids=[self.doc1.id])
        response = self.client.get(self.select_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("selected_documents", response.data)


class QnAViewTest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.qna_url = reverse("qna")
        self.selected_doc = SelectedDocuments.objects.create(
            selected_ids=[1, 2], user=self.user
        )

    @patch("RAG.corrective_rag.CorrectiveRAG.run")
    def test_qna_success(self, mock_rag_ask_question):
        mock_rag_ask_question.return_value = "This is a test answer."
        data = {"question": "What is AI?", "thread_id": "test-thread"}
        response = self.client.post(self.qna_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("answer", response.data)
