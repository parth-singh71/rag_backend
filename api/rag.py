import asyncio
import shutil
from typing import List
from langchain_chroma import Chroma
from chromadb import PersistentClient
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RAG:
    """
    RAG class for managing document retrieval and
    question-answering based on the provided documents.
    """

    def __init__(self):
        self.__llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        self.__embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.chroma_db_collection_name = "rag_db"
        self.chroma_db_path = f"./{self.chroma_db_collection_name}"
        self.__vector_store = Chroma(
            collection_name=self.chroma_db_collection_name,
            embedding_function=self.__embeddings,
            persist_directory=self.chroma_db_path,
        )
        # Defining the prompt template for querying the LLM
        self.__prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.",
                ),
                ("user", "Question: {question}\nContext: {context}\nAnswer:"),
            ]
        )

    def __data_extracter(self, file_path):
        """
        Extract pages from a PDF file.

        :param file_path: Path to the PDF file to be loaded.
        :return: List of documents representing the pages in the PDF.
        """
        loader = PyPDFLoader(file_path)
        pages = []
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

    def __add_documents_to_db(self, docs: List[Document]):
        """
        Add documents to the vector store.

        :param docs: List of Document objects to be added.
        :return: List of document IDs assigned by the vector store.
        """
        document_ids = self.__vector_store.add_documents(documents=docs)
        return document_ids

    def __retrieve_relevant_documents_from_db(self, question: str):
        """
        Retrieve documents from the vector store relevant to the given question.

        :param question: The user's question for which to find relevant documents.
        :return: List of Document objects that are relevant.
        """
        retrieved_docs = self.__vector_store.similarity_search(question)
        return retrieved_docs

    def add_document(self, file_path: str):
        """
        Add a new document to the vector store by extracting and processing it.

        :param file_path: Path to the PDF file to be added.
        """
        pages = self.__data_extracter(file_path)
        splits = self.__split_text(pages)
        self.__add_documents_to_db(splits)

    def clear_vectors(self):
        """
        Clears all vectors stored in the Chroma vector store.
        """
        self.__vector_store.reset_collection()

    def ask_question(self, question: str):
        """
        Ask a question and get relevant answers based on stored documents.

        :param question: The question to be asked.
        :return: The response from the language model based on retrieved context.
        """
        context = self.__retrieve_relevant_documents_from_db(question)
        docs_content = "\n\n".join(doc.page_content for doc in context)
        messages = self.__prompt_template.invoke(
            {"question": question, "context": docs_content}
        )
        response = self.__llm.invoke(messages)
        return response.content
