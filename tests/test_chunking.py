import pytest

from app.services.chunking import chunk_text


def test_chunk_text_observes_size_and_overlap() -> None:
    chunks = chunk_text("one two three four five six", chunk_size=13, overlap=3)

    assert chunks == ["one two three", "three four", "four five six"]
    assert all(len(chunk) <= 13 for chunk in chunks)


def test_reject_invalid_overlap() -> None:
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text("text", chunk_size=10, overlap=10)


def test_zero_overlap_does_not_repeat_words() -> None:
    assert chunk_text("one two three four", chunk_size=7, overlap=0) == [
        "one two",
        "three",
        "four",
    ]
