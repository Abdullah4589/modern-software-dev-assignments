## Running The App

- Run the app: `make run`
- Run tests: `make test`
- Format code: `make format`
- Lint code: `make lint`

## Structure

- Routers live in `backend/app/routers/`
- Tests live in `backend/tests/`
- Models and schemas live in `backend/app`

## Workflow Rules

- When implementing a new endpoint, write a failing test first, then implement the code to pass it.
- Run `make format` and `make lint` before committing.
