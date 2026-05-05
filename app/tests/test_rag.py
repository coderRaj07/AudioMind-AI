import pytest
from app.rag.validator import validate_response


def test_validator_pass():
    chunks = [{
        "metadata": {"text": "AI is artificial intelligence"}
    }]
    answer = "AI is artificial intelligence"

    assert validate_response(answer, chunks) is True


def test_validator_fail():
    chunks = [{
        "metadata": {"text": "AI is artificial intelligence"}
    }]
    answer = "Banana rocket spaceship"

    assert validate_response(answer, chunks) is False