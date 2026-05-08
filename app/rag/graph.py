from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Any

from app.rag.retriever import retrieve_chunks
from app.rag.reranker import rerank_chunks
from app.rag.prompt_builder import build_prompt
from app.services.llm_service import generate_answer
from app.rag.validator import validate_response


class GraphState(TypedDict):
    query: str
    user_id: str
    audio_id: str | None
    chunks: List[Any]
    answer: str
    citations: List[str]


async def retrieve_node(state: GraphState):
    chunks = await retrieve_chunks(
        state["query"],
        state["user_id"],
        state["audio_id"],
    )
    return {"chunks": chunks}


async def rerank_node(state: GraphState):
    ranked = rerank_chunks(state["chunks"])
    return {"chunks": ranked[:3]}


async def generate_node(state: GraphState):
    if not state["chunks"]:
        return {
            "answer": "I could not find this in your audio.",
            "citations": []
        }

    prompt, citations = build_prompt(state["query"], state["chunks"])
    answer = await generate_answer(prompt)

    return {"answer": answer, "citations": citations}


async def validate_node(state: GraphState):
    valid = validate_response(state["answer"], state["chunks"])

    if not valid:
        return {
            "answer": "I could not find this in your audio.",
            "citations": []
        }

    return {
        "answer": state["answer"],
        "citations": state["citations"]
    }


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("generate", generate_node)
    graph.add_node("validate", validate_node)

    graph.set_entry_point("retrieve")

    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", "validate")
    graph.add_edge("validate", END)

    return graph.compile()