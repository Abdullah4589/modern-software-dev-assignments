from types import SimpleNamespace

import pytest

from ..app.services import extract as extract_service
from ..app.services.extract import (
    extract_action_items,
    extract_action_items_llm,
)


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_bullet_list(monkeypatch):
    fake_response = SimpleNamespace(
        message=SimpleNamespace(content='["Set up the database", "Write the tests"]')
    )

    def fake_chat(**kwargs):
        return fake_response

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    result = extract_action_items_llm("- Set up the database\n- Write the tests")

    assert result == ["Set up the database", "Write the tests"]


def test_extract_action_items_llm_keyword_lines(monkeypatch):
    fake_response = SimpleNamespace(
        message=SimpleNamespace(content='["Fix the login page", "Email the report"]')
    )

    def fake_chat(**kwargs):
        return fake_response

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    result = extract_action_items_llm("TODO: Fix the login page\nAction: Email the report")

    assert result == ["Fix the login page", "Email the report"]


def test_extract_action_items_llm_empty_input(monkeypatch):
    def fail_if_called(**kwargs):
        pytest.fail("Ollama should not be called for empty input")

    monkeypatch.setattr(extract_service, "chat", fail_if_called)

    assert extract_action_items_llm("") == []
