from unittest import TestCase
from unittest.mock import patch
from langchain_core.documents import Document
from RAG.rag import RAG


class TestRAG(TestCase):
    def setUp(self):
        """Initialize RAG instance before each test"""
        self.rag_module = RAG()

    @patch("RAG.rag.PyPDFLoader")
    def test_data_extracter(self, MockLoader):
        """Test extracting pages from a PDF file"""
        mock_loader = MockLoader.return_value
        mock_loader.lazy_load.return_value = [
            Document(page_content="Page 1 text"),
            Document(page_content="Page 2 text"),
        ]

        pages = self.rag_module._RAG__data_extracter("test.pdf")
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0].page_content, "Page 1 text")

    @patch("RAG.rag.RecursiveCharacterTextSplitter")
    def test_split_text(self, MockSplitter):
        """Test splitting text into chunks"""
        mock_splitter = MockSplitter.return_value
        mock_splitter.split_documents.return_value = [
            Document(page_content="Chunk 1"),
            Document(page_content="Chunk 2"),
        ]

        pages = [Document(page_content="Page text")]
        chunks = self.rag_module._RAG__split_text(pages)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].page_content, "Chunk 1")

    @patch("RAG.rag.Chroma")
    def test_add_documents_to_db(self, MockChroma):
        """Test adding documents to the vector database"""
        mock_chroma = MockChroma.return_value
        mock_chroma.add_documents.return_value = ["doc_1", "doc_2"]

        self.rag_module._RAG__vector_store = mock_chroma

        docs = [
            Document(page_content="Chunk 1"),
            Document(page_content="Chunk 2"),
        ]
        doc_ids = self.rag_module._RAG__add_documents_to_db(docs)
        self.assertEqual(len(doc_ids), 2)

    @patch("RAG.rag.Chroma")
    def test_retrieve_relevant_documents_from_db(self, MockChroma):
        """Test retrieving relevant documents from the vector store"""
        mock_chroma = MockChroma.return_value
        mock_chroma.similarity_search.return_value = [
            Document(page_content="Relevant Doc 1"),
            Document(page_content="Relevant Doc 2"),
        ]

        self.rag_module._RAG__vector_store = mock_chroma

        results = self.rag_module._RAG__retrieve_relevant_documents_from_db(
            "test question"
        )
        # self.assertEqual(len(results), 2)
        self.assertEqual(results[0].page_content, "Relevant Doc 1")

    @patch("RAG.rag.init_chat_model")
    @patch("RAG.rag.ChatPromptTemplate")
    def test_ask_question(self, MockChatPromptTemplate, MockChatModel):
        """Test asking a question and getting an AI-generated response"""
        mock_llm = MockChatModel.return_value
        mock_llm.invoke.return_value.content = "Generated answer"

        mock_prompt = MockChatPromptTemplate.return_value
        mock_prompt.invoke.return_value = "Formatted prompt"

        self.rag_module._RAG__llm = mock_llm
        self.rag_module._RAG__prompt_template = mock_prompt

        with patch.object(
            self.rag_module, "_RAG__retrieve_relevant_documents_from_db"
        ) as mock_retrieve:
            mock_retrieve.return_value = [Document(page_content="Context text")]

            response = self.rag_module.ask_question("What is RAG?")
            self.assertEqual(response, "Generated answer")

    @patch("RAG.rag.Chroma")
    def test_clear_vectors(self, MockChroma):
        """Test clearing all vectors in the database"""
        mock_chroma = MockChroma.return_value

        self.rag_module._RAG__vector_store = mock_chroma

        self.rag_module.clear_vectors()
        mock_chroma.reset_collection.assert_called_once()
