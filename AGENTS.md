# nldate development instructions

## Project requirements

Build a Python library named `nldate` for DSC 190 Assignment 06, with source in
`src/nldate/` and this public API:

```python
from datetime import date


def parse(s: str, today: date | None = None) -> date: ...
```

Convert natural-language date expressions to `datetime.date`. Relative expressions
use `today`, defaulting to the actual current date when omitted. Eventually support
a broad variety of formats, including:

- `December 1st, 2025`
- `5 days before December 1st, 2025`
- `1 year and 2 months after yesterday`
- `next Tuesday`
- `in 3 days`
- `two weeks from tomorrow`

Use modern Python and type hints. Do not install date-parsing libraries without
the human's explicit approval.

## Middle Path workflow

The human writes the entire test suite and defines expected behavior. The AI
handles project setup, implementation, and debugging.

- Never write tests, example tests, placeholder tests, or generated test cases.
- Never modify the human's tests unless explicitly authorized.
- Setup only is currently authorized. Keep `parse()` unfinished and
  `tests/test_parse.py` empty. Wait for the human to write tests and explicitly
  request implementation before implementing date parsing.
- After that request, implement the parser and fix failures without changing
  tests. Ask the human to resolve ambiguous expectations when necessary.
- Do not push to GitHub unless explicitly requested.

## Development commands

```bash
uv sync
uv run pytest
uv run mypy src/nldate tests
uv run ruff check .
uv run ruff format --check .
```

Before tests are written, pytest exits with code 5 because no tests are collected;
this is expected. Do not add tests or suppress this result to make it pass.

Keep `uv.lock` committed for reproducible development dependencies. Keep virtual
environments, tool caches, build artifacts, and secrets out of Git.
