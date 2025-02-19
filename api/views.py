from django.shortcuts import get_list_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .models import Document, SelectedDocuments
from .serializers import (
    DocumentSelectionSerializer,
    DocumentSerializer,
    QuestionSerializer,
)
from .rag import RAG


# Create your views here.
class DocumentUploadView(APIView):
    """
    View for handling document uploads.
    """

    # Defining parsers to handle file uploads
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Validating incoming data with the serializer
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            # Saving the valid document to the database
            document = serializer.save()
            rag = RAG()
            # Processing the uploaded document with RAG
            rag.add_document(document.file.path)
            return Response(
                {
                    "upload_status": "success",
                    "message": "Document uploaded successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenericDocumentsView(GenericAPIView, ListModelMixin, RetrieveModelMixin):
    """
    View to list and retrieve document instances.
    """

    serializer_class = DocumentSerializer
    queryset = Document.objects.all()
    lookup_field = "id"

    def get(self, request, id=None):
        """
        Handling GET requests for retrieving all
        documents or a single document.
        """
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)


class DocumentSelectionView(APIView):
    """
    View for selecting documents.
    """

    def post(self, request, *args, **kwargs):
        """
        Store selected document IDs in the database.
        """
        serializer = DocumentSelectionSerializer(data=request.data)
        if serializer.is_valid():
            doc_ids = serializer.validated_data["document_ids"]

            # Validating document existence
            documents = get_list_or_404(Document, id__in=doc_ids)

            rag = RAG()
            rag.clear_vectors()

            # Clearing previous selection
            # SelectedDocuments.objects.all().delete()
            # Adding new selection
            selected_docs = SelectedDocuments.objects.create(selected_ids=doc_ids)

            for doc_id in doc_ids:
                document = Document.objects.get(id=doc_id)
                rag.add_document(document.file.path)

            return Response(
                {
                    "message": "Documents selected successfully",
                    "selected_documents": selected_docs.selected_ids,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the IDs of selected documents.
        """
        try:
            # Getting the most recent selection
            selected_docs = SelectedDocuments.objects.latest("created_at")
            return Response(
                {"selected_documents": selected_docs.selected_ids},
                status=status.HTTP_200_OK,
            )
        except SelectedDocuments.DoesNotExist:
            return Response({"selected_documents": []}, status=status.HTTP_200_OK)


class QnAView(APIView):
    """
    View to handle Q&A requests based on selected documents.
    """

    def post(self, request, *args, **kwargs):
        """
        Generate an answer for a given question based on the selected documents.
        """
        # Validating incoming question data
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data["question"]

            # Fetching selected documents from DB
            try:
                selected_docs = SelectedDocuments.objects.latest("created_at")
                doc_ids = selected_docs.selected_ids
            except SelectedDocuments.DoesNotExist:
                print("No selected documents found.")

            rag = RAG()
            # Generating Answer using RAG
            answer = rag.ask_question(question)

            return Response(
                {"question": question, "answer": answer}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
