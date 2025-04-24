from unittest import TestCase
from unittest.mock import patch, MagicMock
from RAG.corrective_rag import (
    CorrectiveRAG,
    CRAGState,
    RAGDocumentGraderResponse,
    RAGDocumentGrade,
)
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage


class TestCorrectiveRAG(TestCase):

    def setUp(self):
        self.rag = CorrectiveRAG()
        self.user_id = "test_user"
        self.query = "What is the capital of France?"

    @patch("RAG.corrective_rag.Chroma.similarity_search")
    def test_rag_retriever(self, mock_search):
        mock_search.return_value = [
            Document(page_content="Paris is the capital of France.")
        ]
        state = {
            "messages": [HumanMessage(content=self.query)],
            "user_id": self.user_id,
        }

        result = self.rag._CorrectiveRAG__rag_retriver(state)
        self.assertTrue("rag_context" in result)
        self.assertEqual(len(result["rag_context"]), 1)
        self.assertIn("Paris", result["rag_context"][0].page_content)

    def test_document_grader_relevant(self):
        # Manually override the private __llm attribute using name mangling
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = RAGDocumentGraderResponse(
            grade=RAGDocumentGrade.relevant, description=None
        )

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_chain

        # Accessing the mangled attribute
        self.rag._CorrectiveRAG__llm = mock_llm

        state = {
            "question": self.query,
            "rag_context": [Document(page_content="Paris is the capital of France.")],
        }

        result = self.rag._CorrectiveRAG__document_grader(state)
        self.assertEqual(
            result["document_grader_response"].grade, RAGDocumentGrade.relevant
        )

    def test_document_grader_route_condition(self):
        state = {
            "document_grader_response": RAGDocumentGraderResponse(
                grade=RAGDocumentGrade.irrelevant
            )
        }
        route = self.rag._CorrectiveRAG__document_grader_route_condition(state)
        self.assertEqual(route, "rephrase_query")

    def test_custom_tools_condition_tool_call(self):
        mock_tool_message = MagicMock()
        mock_tool_message.tool_calls = [MagicMock()]
        state = {"messages": [mock_tool_message]}

        result = self.rag._CorrectiveRAG__custom_tools_condition(state)
        self.assertEqual(result, "tools")

    def test_custom_tools_condition_no_tool_call(self):
        mock_tool_message = MagicMock()
        mock_tool_message.tool_calls = []
        state = {"messages": [mock_tool_message]}

        result = self.rag._CorrectiveRAG__custom_tools_condition(state)
        self.assertEqual(result, "responder")
