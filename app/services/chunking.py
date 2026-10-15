def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be greater than zero.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_overlap must be non-negative and less than chunk_size.")

    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized) and normalized[end] != " ":
            boundary = normalized.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(normalized[start:end].strip())
        if end >= len(normalized):
            break
        next_start = max(end - overlap, start + 1)
        if next_start < len(normalized) and normalized[next_start] == " ":
            next_start += 1
        else:
            next_start = normalized.rfind(" ", 0, next_start) + 1
        start = max(next_start, start + 1)
    return chunks
