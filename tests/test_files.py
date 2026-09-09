import pytest
from app.files import extract_text


def test_extract_text_file():
    assert extract_text("note.md", "text/markdown", b"hello") == "hello"


def test_reject_unknown_format():
    with pytest.raises(ValueError):
        extract_text("x.bin", "application/octet-stream", b"123")
