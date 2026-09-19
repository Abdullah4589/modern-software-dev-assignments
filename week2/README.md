# Action Item Extractor

Action Item Extractor is a small FastAPI and SQLite application that turns free-form meeting notes into a checklist of action items. It supports two extraction methods:

- **Extract** uses simple rules, such as bullet points and `TODO:` lines.
- **Extract LLM** uses a local Ollama model to find action items in ordinary sentences.

The web page also lets you save notes, mark action items complete, and list all saved notes.

## Requirements

- Python 3.12
- [Conda](https://docs.conda.io/) with the `cs146s` environment, or another Python 3.12 environment
- [Poetry](https://python-poetry.org/)
- [Ollama](https://ollama.com/)
- The `llama3.1:8b` Ollama model

## Setup

Run these commands from the parent project folder, `modern-software-dev-assignments`.

```powershell
conda activate cs146s
poetry env use python
poetry install
```

Download the model once:

```powershell
ollama pull llama3.1:8b
```

Ollama must be running before you use **Extract LLM**. If the Ollama desktop application is not already running, start its local server in another terminal:

```powershell
ollama serve
```

## Run the application

From the parent project folder, start FastAPI:

```powershell
poetry run uvicorn week2.app.main:app --reload
```

Open the application in a browser:

```text
http://127.0.0.1:8000/
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The SQLite database is created automatically at `week2/data/app.db` when the server starts.

## Web page features

- **Extract**: applies the rule-based extractor to the notes.
- **Extract LLM**: sends the notes to the local `llama3.1:8b` Ollama model.
- **Save as note**: saves the submitted notes in SQLite when checked.
- **List Notes**: shows all saved notes, including their ID and creation time.
- Action-item checkboxes: mark saved action items as complete.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Serve the Action Item Extractor web page. |

### Notes

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/notes` | Save one note. Body: `{"content": "Meeting notes"}`. |
| `GET` | `/notes` | Return all saved notes, newest first. |
| `GET` | `/notes/{note_id}` | Return one saved note by ID. Returns `404` if it does not exist. |

### Action items

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/action-items/extract` | Extract action items using rules. Body: `{"text": "- Write tests", "save_note": true}`. |
| `POST` | `/action-items/extract-llm` | Extract action items with Ollama. Uses the same request body as `/action-items/extract`. |
| `GET` | `/action-items` | Return all action items. Optionally filter by note: `/action-items?note_id=1`. |
| `POST` | `/action-items/{action_item_id}/done` | Mark an item complete or incomplete. Body: `{"done": true}`. Returns `404` if the item does not exist. |

Both extraction endpoints return a note ID when the note was saved and a list of extracted action items:

```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "Write tests"}
  ]
}
```

## Run tests

From the parent project folder, run:

```powershell
poetry run pytest week2/tests -v
```

The tests mock Ollama responses, so Ollama does not need to be running to execute the test suite.
