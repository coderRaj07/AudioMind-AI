def build_prompt(query: str, chunks: list):
    context_parts = []
    citations = []

    for i, c in enumerate(chunks):
        meta = c["metadata"]
        context_parts.append(meta["text"])
        citations.append(
            f"[Chunk {i+1} | {meta.get('start_time',0)}–{meta.get('end_time',0)}]"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
                You are a strict assistant.

                RULES:
                - Answer ONLY from the provided context
                - If answer is not found, say: "I could not find this in your audio."
                - Do NOT hallucinate
                - Provide citations

                Context:
                {context}

                Question:
                {query}

                Answer:
                """

    return prompt, citations