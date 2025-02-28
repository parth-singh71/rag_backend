import datetime
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from ..models import Document, SelectedDocuments


class DocumentModelTest(TestCase):
    def setUp(self):
        """Set up a sample PDF file for testing"""
        self.valid_pdf = SimpleUploadedFile(
            "test.pdf", b"PDF content", content_type="application/pdf"
        )
        self.invalid_txt_file = SimpleUploadedFile(
            "test.txt", b"Text content", content_type="text/plain"
        )

    def test_document_creation(self):
        """Test if a Document object can be created successfully"""
        title = "Test Document"
        description = "This is a test document"
        doc = Document.objects.create(
            title=title,
            description=description,
            file=self.valid_pdf,
        )
        self.assertEqual(doc.title, title)
        self.assertEqual(doc.description, description)
        # asserting True because this should be auto-generated
        self.assertTrue(doc.uploaded_at)

    def test_uploaded_at_auto_now_add(self):
        """Test if 'uploaded_at' is automatically set on creation"""
        doc = Document.objects.create(title="Test Doc", file=self.valid_pdf)
        self.assertIsInstance(doc.uploaded_at, datetime.datetime)

    def test_invalid_file_extension(self):
        """Test that only PDFs are allowed (raise ValidationError for other file types)"""
        doc = Document(title="Invalid File", file=self.invalid_txt_file)
        with self.assertRaises(ValidationError):
            doc.full_clean()  # This triggers model validations, including FileExtensionValidator

    def test_str_method(self):
        """Test the __str__ method (if implemented)"""
        title = "Test Document"
        doc = Document.objects.create(title=title, file=self.valid_pdf)
        # Adjust if `__str__` method is defined differently
        self.assertEqual(str(doc), title)


class SelectedDocumentsModelTest(TestCase):
    def test_selected_documents_creation(self):
        """Test if a SelectedDocuments object can be created successfully"""
        ids = [1, 2, 3]
        doc = SelectedDocuments.objects.create(selected_ids=ids)
        self.assertEqual(doc.selected_ids, ids)
        self.assertTrue(doc.created_at)  # Should be auto-generated

    def test_created_at_auto_now_add(self):
        """Test if 'created_at' is automatically set on creation"""
        doc = SelectedDocuments.objects.create(selected_ids=[10, 20])
        self.assertIsInstance(doc.created_at, datetime.datetime)

    def test_str_method(self):
        """Test the __str__ method"""
        ids = [1, 2, 3]
        doc = SelectedDocuments.objects.create(selected_ids=ids)
        expected_str = f"Selected Documents {doc.id} - {ids}"
        self.assertEqual(str(doc), expected_str)
