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
from RAG.data_injector import DataInjector
from RAG.corrective_rag import CorrectiveRAG


# Create your views here.
class DocumentUploadView(APIView):
    """
    View for handling document uploads.
    """

    # Defining parsers to handle file uploads
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Validating incoming data with the serializer
        curr_user = request.user
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            # Saving the valid document to the database
            document = serializer.save(uploaded_by=curr_user)
            injector = DataInjector()
            # Injecting document into vector DB with user_id
            injector.add_document(document.file.path, user_id=str(curr_user.id))
            return Response(
                {
                    "upload_status": "success",
                    "message": "Document uploaded successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenericUserDocumentsView(GenericAPIView, ListModelMixin, RetrieveModelMixin):
    """
    View to list and retrieve user's document instances.
    """

    serializer_class = DocumentSerializer
    queryset = Document.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        """
        Return documents that belong only to the currently authenticated user.
        """
        return Document.objects.filter(uploaded_by=self.request.user)

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
        curr_user = request.user
        serializer = DocumentSelectionSerializer(data=request.data)
        if serializer.is_valid():
            doc_ids = serializer.validated_data["document_ids"]

            # Validating document existence
            # documents = get_list_or_404(Document, id__in=doc_ids)
            documents = Document.objects.filter(id__in=doc_ids, uploaded_by=curr_user)

            # Check if all provided IDs are valid and owned by user
            if documents.count() != len(doc_ids):
                return Response(
                    {
                        "error": "One or more documents are not owned by the current user."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            injector = DataInjector()
            injector.clear_vectors()

            # Creating or Updating selection
            try:
                selected_docs_obj = SelectedDocuments.objects.get(user=curr_user)
                selected_docs_obj.selected_ids = doc_ids
                selected_docs_obj.save()
            except SelectedDocuments.DoesNotExist:
                selected_docs_obj = SelectedDocuments.objects.create(
                    user=curr_user,
                    selected_ids=doc_ids,
                )

            for doc_id in doc_ids:
                document = Document.objects.get(id=doc_id)
                injector.add_document(document.file.path, user_id=curr_user.id)

            return Response(
                {
                    "message": "Documents selected successfully",
                    "selected_documents": selected_docs_obj.selected_ids,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the IDs of selected documents.
        """
        try:
            # Getting the most recent user's selection
            selected_docs = SelectedDocuments.objects.get(user=request.user)

            if selected_docs:
                return Response(
                    {"selected_documents": selected_docs.selected_ids},
                    status=status.HTTP_200_OK,
                )
            raise SelectedDocuments.DoesNotExist
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
        curr_user = request.user
        # Validating incoming question data
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data["question"]
            thread_id = serializer.validated_data["thread_id"]

            # Fetching selected documents from DB
            try:
                selected_docs = SelectedDocuments.objects.get(user=curr_user)
                doc_ids = selected_docs.selected_ids
            except SelectedDocuments.DoesNotExist:
                print("No selected documents found.")

            crag = CorrectiveRAG()
            # Generating Answer using RAG
            answer = crag.run(
                question,
                user_id=str(curr_user.id),
                thread_id=(thread_id if len(thread_id) > 0 else "default"),
            )

            return Response(
                {"question": question, "answer": answer}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
