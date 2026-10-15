from app.services import ingestion


class FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.committed = False

    def execute(self, statement) -> None:
        self.statement = statement

    def add_all(self, values) -> None:
        self.added.extend(values)

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        raise AssertionError("Unexpected rollback")


def test_unverified_document_is_skipped_before_embedding(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("Unverified content must not be embedded")

    monkeypatch.setattr(ingestion, "embed_texts", fail_if_called)
    session = FakeSession()

    result = ingestion.ingest_document(
        session,
        "community.md",
        "---\ndoc_id: KB-099\nstatus: UnVerified\n---\nDo not ingest this.",
    )

    assert result.ingested is False
    assert result.status == "UnVerified"
    assert result.document_id == "KB-099"
    assert result.chunks_created == 0
    assert not session.added
    assert not session.committed


def test_ingested_chunks_keep_document_metadata(monkeypatch) -> None:
    monkeypatch.setattr(ingestion, "embed_texts", lambda texts, task_type: [[0.0] * 768])
    session = FakeSession()

    result = ingestion.ingest_document(
        session,
        "article.md",
        "---\ndoc_id: KB-001\nstatus: current\ntitle: Reset\n---\nReset steps.",
    )

    assert result.ingested is True
    assert result.chunks_created == 1
    assert session.committed
    chunk = session.added[0]
    assert chunk.document_id == "KB-001"
    assert chunk.status == "current"
    assert chunk.metadata_["title"] == "Reset"
    assert chunk.metadata_["source_file"] == "article.md"
    assert chunk.metadata_["chunk_index"] == 0
