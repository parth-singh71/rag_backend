from typing import List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DataInjector:
    """
    RAG class for managing document retrieval and
    question-answering based on the provided documents.
    """

    def __init__(self, chroma_db_collection_name="rag_db"):
        self.__embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        chroma_db_path = f"./{chroma_db_collection_name}"
        self.__vector_store = Chroma(
            collection_name=chroma_db_collection_name,
            embedding_function=self.__embeddings,
            persist_directory=chroma_db_path,
        )

    def __data_extracter(self, file_path):
        """
        Extract pages from a PDF file.

        :param file_path: Path to the PDF file to be loaded.
        :return: List of documents representing the pages in the PDF.
        """
        loader = PyPDFLoader(file_path)
        pages: List[Document] = []
        for page in loader.lazy_load():
            pages.append(page)
        return pages

    def __split_text(self, pages: List, chunk_size=1000, chunk_overlap=200):
        """
        Split the given document pages into smaller chunks for easier processing.

        :param pages: List of Document objects representing the pages.
        :param chunk_size: Maximum size of each chunk.
        :param chunk_overlap: Overlap between consecutive chunks.
        :return: List of Document chunks.
        """
        recursive_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        # Splitting the pages into chunks
        splits = recursive_text_splitter.split_documents(pages)
        return splits

    def __add_documents_to_db(self, docs: List[Document], user_id: str):
        """
        Add documents to the vector store.

        :param docs: List of Document objects to be added.
        :param user_id: ID of the user to associate with the documents.
        :return: List of document IDs assigned by the vector store.
        """

        # Injecting user_id into metadata
        for doc in docs:
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata["user_id"] = user_id

        document_ids = self.__vector_store.add_documents(documents=docs)
        return document_ids

    def add_document(self, file_path: str, user_id: str):
        """
        Add a new document to the vector store by extracting and processing it.

        :param file_path: Path to the PDF file to be added.
        """
        pages = self.__data_extracter(file_path)
        splits = self.__split_text(pages)
        self.__add_documents_to_db(splits, user_id)

    def clear_vectors(self):
        """
        Clears all vectors stored in the Chroma vector store.
        """
        self.__vector_store.reset_collection()
