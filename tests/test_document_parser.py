import pytest

from app.services.document_parser import parse_document


def test_parse_yaml_front_matter_and_body() -> None:
    metadata, body = parse_document(
        "---\ndoc_id: KB-1\nstatus: unverified\neffective_date: 2026-01-01\n---\nHello\n"
    )

    assert metadata == {
        "doc_id": "KB-1",
        "status": "unverified",
        "effective_date": "2026-01-01",
    }
    assert body == "Hello"


def test_document_without_front_matter() -> None:
    assert parse_document("# Just text") == ({}, "# Just text")


def test_reject_unclosed_front_matter() -> None:
    with pytest.raises(ValueError, match="closing"):
        parse_document("---\nstatus: current\nBody")
