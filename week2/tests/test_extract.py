import os
from typing import List
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


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
    
def extract_action_items_llm(input_text: str) -> List[str]:
      """Use Ollama to extract action items as a JSON list."""
      if not input_text.strip():
          return []

      prompt = (
          "Extract only the action items from these notes. "
          "Return an array of short action-item strings. "
          "If there are no action items, return an empty array.\n\n"
          f"Notes:\n{input_text}"
      )

      try:
          response = chat(
              model="llama3.1:8b",
              messages=[{"role": "user", "content": prompt}],
              format={
                  "type": "array",
                  "items": {"type": "string"},
              },
              options={
                  "temperature": 0.2,
                  "num_predict": 500,
              },
          )

          content = response.message.content
          action_items = json.loads(content)

          if isinstance(action_items, list) and all(
              isinstance(item, str) for item in action_items
          ):
              return action_items

          return []

      except (json.JSONDecodeError, AttributeError, Exception):
          return []

