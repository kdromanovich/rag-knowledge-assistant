import pytest
from app.chunking import chunk_text


def test_chunking_overlap():
    text = " ".join(str(i) for i in range(20))
    chunks = chunk_text(text, size_words=8, overlap_words=2)
    assert len(chunks) == 3
    assert chunks[0].split()[-2:] == chunks[1].split()[:2]


def test_empty_text():
    assert chunk_text("   ") == []


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("a b c", size_words=3, overlap_words=3)
