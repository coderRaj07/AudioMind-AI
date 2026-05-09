def validate_response(answer: str, chunks: list):
    if not answer or len(answer.strip()) == 0:
        return False

    if answer.strip() == "I could not find this in your audio.":
        return len(chunks) == 0

    if "I could not find this in your audio" in answer:
        return False

    # basic grounding check
    context_text = " ".join([c["metadata"]["text"] for c in chunks])

    overlap = sum(
        1 for word in answer.split()
        if word.lower() in context_text.lower()
    )

    ratio = overlap / max(len(answer.split()), 1)

    if ratio < 0.3:
        return False

    return True