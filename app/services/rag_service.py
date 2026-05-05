from app.rag.graph import build_graph
from app.core.logger import get_logger

logger = get_logger(__name__)

graph = build_graph()


async def run_rag(query: str, user_id: str):
    result = await graph.ainvoke({
        "query": query,
        "user_id": user_id,
        "chunks": [],
        "answer": "",
        "citations": []
    })

    return result