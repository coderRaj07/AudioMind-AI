def clean_transcript(text: str) -> str:
    text = text.strip()
    text = text.replace("\n", " ")
    return text