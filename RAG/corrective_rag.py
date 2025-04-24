import os

os.environ["USER_AGENT"] = "CRAG/1.0"


from enum import Enum
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Literal, Annotated, List
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .tools import (
    get_web_search_tool,
    get_news_search_tool,
    wikipedia_tool,
    wikidata_tool,
    youtube_search_tool,
)


class RAGDocumentGrade(Enum):
    relevant = "relevant"
    irrelevant = "irrelevant"


class RAGDocumentGraderResponse(BaseModel):
    """Represents the structured response for grading a retrieved document in a RAG-based system."""

    grade: RAGDocumentGrade = Field(
        ...,
        description="""The assigned grade indicating whether the document is relevant ("relevant") or not ("irrelevant")""",
    )
    description: str | None = Field(
        None,
        description="""Additional context or reasoning for the grading, typically provided when the grade is "irrelevant". This field is optional.""",
    )


class CRAGState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    answer: str
    document_grader_response: RAGDocumentGraderResponse
    crawler_response: str
    rag_context: List[Document]
    user_id: str


class CorrectiveRAG:

    def __init__(self):
        self.__memory = MemorySaver()
        self._llm = init_chat_model(model="gpt-4o-mini", model_provider="openai")
        self.__embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.__tools = [
            get_web_search_tool(),
            wikipedia_tool,
            wikidata_tool,
            youtube_search_tool,
            get_news_search_tool(),
        ]
        self.__llm_with_tools = self._llm.bind_tools(self.__tools)
        chroma_db_collection_name = "rag_db"
        chroma_db_path = f"./{chroma_db_collection_name}"
        self.__vector_store = Chroma(
            collection_name=chroma_db_collection_name,
            embedding_function=self.__embeddings,
            persist_directory=chroma_db_path,
        )
        self.__graph = self.__get_graph()
        # print(self.graph.get_graph().draw_mermaid())

    def run(self, query: str, user_id: str, thread_id: str = "default"):
        """
        Public method to invoke the graph and get a final response for a given query.
        """
        config = {
            "configurable": {"thread_id": f"{user_id}#{thread_id}"},
            "recursion_limit": 25,
        }

        initial_state: CRAGState = {
            "messages": [
                {"role": "user", "content": query},
            ],
            "user_id": user_id,
        }

        events = self.__graph.stream(initial_state, config, stream_mode="values")

        final_message = None
        for event in events:
            event["messages"][-1].pretty_print()
            final_message = event["messages"][-1]  # Last message is the result

        return final_message.content if final_message else "No response"

    def __get_graph(self):
        """
        Builds and compiles the LangGraph for RAG-based querying and correction.
        """
        graph_builder = StateGraph(CRAGState)

        # Primary path: RAG retriever -> document grading
        # graph_builder.add_sequence([self.__rag_retriver, self.__document_grader])
        graph_builder.add_node("rag_retriver", self.__rag_retriver)
        graph_builder.add_node("document_grader", self.__document_grader)

        # Conditional branches
        graph_builder.add_node("rephrase_query", self.__rephrase_query)
        graph_builder.add_node("crawler_agent", self.__crawler_agent)
        graph_builder.add_node("responder", self.__responder)

        tool_node = ToolNode(tools=self.__tools)
        graph_builder.add_node("tools", tool_node)

        graph_builder.set_entry_point("rag_retriver")

        # Adding edges to the graph
        graph_builder.add_edge("rag_retriver", "document_grader")

        graph_builder.add_conditional_edges(
            "document_grader",
            self.__document_grader_route_condition,
            path_map={
                "rephrase_query": "rephrase_query",
                "responder": "responder",
            },
        )

        graph_builder.add_edge("rephrase_query", "crawler_agent")

        graph_builder.add_conditional_edges(
            "crawler_agent",
            self.__custom_tools_condition,
            {"tools": "tools", "responder": "responder"},
        )

        graph_builder.add_edge("tools", "crawler_agent")
        graph_builder.add_edge("responder", END)

        graph = graph_builder.compile(checkpointer=self.__memory)
        return graph

    def __rag_retriver(self, state: CRAGState):
        """
        Retrieves relevant documents from the vector store based on last user message.
        """
        user_id = state.get("user_id", "anon")
        messages = state.get("messages", [])
        last_user_message = None
        n = len(messages)
        for i in range(n - 1, -1, -1):
            msg = messages[i]
            if isinstance(msg, HumanMessage):
                last_user_message = msg.content
                break
        if last_user_message is None:
            raise Exception("No user message found in the conversation.")
        retrieved_docs = self.__vector_store.similarity_search(
            query=last_user_message, filter={"user_id": user_id}
        )
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)

        new_state = CRAGState(**state)
        new_state["rag_context"] = retrieved_docs
        new_state["question"] = last_user_message
        new_state["messages"] = [{"content": context, "role": "ai"}]
        return new_state

    def __document_grader(self, state: CRAGState):
        """
        Uses LLM to assess whether retrieved context is relevant to the question or not.
        """
        question = state.get("question")
        context = state.get("rag_context", [])
        docs_content = "\n\n".join(doc.page_content for doc in context)

        grader_llm = self._llm.with_structured_output(RAGDocumentGraderResponse)
        grader_prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are an expert evaluator responsible for grading retrieved documents in a Retrieval Augmented Generation (RAG) system. Your task is to assess whether the retrieved context is relevant and useful in answering the question or not, also give a proper reason if the context in not relevant.",
                ),
                ("human", "question: {question}\ncontext: {context}"),
            ]
        )
        chain = grader_prompt_template | grader_llm
        grader_response = chain.invoke({"question": question, "context": docs_content})

        new_state = CRAGState(**state)
        new_state["document_grader_response"] = grader_response
        new_state["messages"] = [
            {"content": grader_response.model_dump_json(), "role": "ai"}
        ]
        return new_state

    def __rephrase_query(self, state: CRAGState):
        """
        Rephrases the original query to improve search and retrieval accuracy.
        """
        question = state.get("question")
        prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are an expert in query optimization and search enhancement. Your task is to rephrase and improve user query to make them clearer, more specific, and better suited for retrieval in a search engine or a Retrieval Augmented Generation (RAG) system.",
                ),
                ("human", "Question: {question}\nRephrased Question:"),
            ]
        )
        chain = prompt_template | self._llm | StrOutputParser()
        rephrased_question = chain.invoke({"question": question})

        new_state = CRAGState(**state)
        new_state["question"] = rephrased_question
        new_state["messages"] = [{"content": rephrased_question, "role": "ai"}]
        return new_state

    def __crawler_agent(self, state: CRAGState):
        """
        Uses LLM + tools to perform external search and gather new information.
        """
        if state.get("crawler_response", None) is None:
            llm_input = state.get("question")
        else:
            llm_input = state.get("messages", [])

        response = self.__llm_with_tools.invoke(llm_input)

        new_state = CRAGState(**state)
        new_state["crawler_response"] = response.content
        new_state["messages"] = [response]
        return new_state

    def __responder(self, state: CRAGState):
        """
        Generates final answer based on best available context.
        """
        question = state.get("question")
        final_context = None
        should_consider_rag_context = False
        document_grader_response = state.get("document_grader_response", None)
        if (
            document_grader_response is None
            or document_grader_response.grade == "relevant"
        ):
            should_consider_rag_context = True
        if should_consider_rag_context:
            context = state.get("rag_context", [])
            docs_content = "\n\n".join(doc.page_content for doc in context)
            final_context = docs_content
        else:
            final_context = state.get("crawler_response", "No Context Found")

        prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.",
                ),
                ("user", "Question: {question}\nContext: {context}\nAnswer:"),
            ]
        )
        chain = prompt_template | self._llm | StrOutputParser()
        answer = chain.invoke({"question": question, "context": final_context})

        new_state = CRAGState(**state)
        new_state["answer"] = answer
        new_state["messages"] = [{"content": answer, "role": "assistant"}]
        return new_state

    def __document_grader_route_condition(
        self, state: CRAGState
    ) -> Literal["rephrase_query", "responder"]:
        """
        Branches to either responder (if context is relevant)
        or rephrase_query (if context is not relevant).
        """
        document_grader_response = state.get("document_grader_response", None)
        if (
            document_grader_response is None
            or document_grader_response.grade == "relevant"
        ):
            return "responder"
        return "rephrase_query"

    def __custom_tools_condition(
        self,
        state: CRAGState,
        messages_key: str = "messages",
    ) -> Literal["tools", "responder"]:
        """
        Checks if tool call is needed based on message content.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif isinstance(state, dict) and (messages := state.get(messages_key, [])):
            ai_message = messages[-1]
        elif messages := getattr(state, messages_key, []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "responder"
