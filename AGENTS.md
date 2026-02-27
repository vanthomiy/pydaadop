# AGENTS Guidelines

This document provides guidance for automated coding agents operating in this repository. It covers build/test tooling, code style expectations, error handling, and how to coordinate multi-step tasks with a to-do workflow.

Note: Cursor rules are not present in this repository. Copilot rules are documented in the repository's Copilot directive file when available.

---

## 1) Build, Lint, and Test commands

- Environment and dependencies
  - Python 3.10+ is expected (as per pyproject.toml and tests).
  - Install development dependencies with:
    - `python -m pip install -e ".[dev]"`  (preferred)
      - Reason: installs pytest, pytest-asyncio, httpx as needed by tests.
    - Alternatively: `pip install -r requirements.txt` for runtime deps; add dev extras as needed.

- Build
  - Build distributions locally: `python -m build`
  - Prereqs: ensure `build` is installed (`pip install build`).
  - Outputs go to `dist/` by default.

- Lint (recommendations)
  - If you install lint tools, prefer:
    - `ruff check src tests`  (fast, modern linter)
    - `ruff format src tests` (auto-format fan-out)
  - Optional formatting and import sorting:
    - `black src tests` (code formatter, 88-char line length by default)
    - `isort src tests` (import sorter)
  - If a linter is not available, at minimum ensure style manually:
    - Use descriptive type hints, docstrings, and avoid overly long lines.

- Tests
  - Run the full test suite: `pytest -q` or `pytest tests -q`.
  - Run tests with concise output: `pytest -q --tb=short`.
  - Run a single test function or method:
    - `pytest tests/path/to/file.py::test_function`  (no class)
    - `pytest tests/path/to/file.py::TestClass::test_method`  (class method)
  - Run a subset by keyword:
    - `pytest -k "pattern" tests/`  (e.g., pattern = `test_base_query`)
  - Async tests are supported via pytest-asyncio (as configured in pyproject).

- Quick example workflows
  - One-off test for a single function: `pytest tests/test_base_query.py::test_get_type_literal -q`.
  - Full local verification: `python -m build && python -m venv venv && source venv/bin/activate && pip install -e ".[dev]" && pytest -q`.

- Continuous integration hints
  - CI should run `pytest tests/ -q --tb=short` and fail fast on first failure.
  - If you need to install Mongo/MongoDB dependencies, consider environment fixtures in tests.

---

## 2) Code style guidelines

- General
  - Follow PEP 8 for Python code; target readable, maintainable code.
  - Use the project’s existing conventions; when in doubt, align with nearby modules.
  - Docstrings for public API surfaces should describe intent, inputs, and outputs.

- Imports
  - Standard library imports first, then third-party, then local imports.
  - Separate groups with a blank line; no unused imports.
  - Use absolute imports where possible; avoid circular imports.
  - Prefer explicit imports over wildcard imports.
  - Run isort to enforce alphabetical grouping and order.

- Formatting
  - Use Black by default to normalize formatting; if not available, maintain consistent style.
  - Keep line lengths around 88 characters; break long expressions clearly.
  - Prefer meaningful variable names over abbreviations.

- Typing
  - Type hints are encouraged; add `->` return types and parameter annotations.
  - Use `from __future__ import annotations` if needed to defer evaluation.
  - Prefer concrete types over `Any` where possible; use `Optional` for nullable values.

- Naming conventions
  - Functions and methods: snake_case.
  - Classes: CamelCase.
  - Modules: snake_case; avoid overly long module names.
  - Constants: ALL_CAPS_WITH_UNDERSCORES where appropriate.

- Error handling
  - Catch specific exceptions; avoid broad `except:` blocks.
  - Propagate errors with meaningful messages; do not swallow stack traces in logs.
  - Define domain-specific exceptions when appropriate and document their use.

- Logging
  - Use the `logging` module; avoid `print` for runtime messages.
  - Include context-rich messages; include identifiers for tracing in logs.
  - Do not leak sensitive data in logs.

- Testing style
  - Tests should be deterministic and fast; isolate external dependencies.
  - Use pytest fixtures for setup/teardown; keep fixtures small and composable.
  - Name tests clearly; include the scenario and expected outcome in the name.
  - Cover both happy-path and edge cases; add property-based tests where useful.

- Documentation and examples
  - Update docs for public API changes; add examples if relevant.
  - Include docstrings and unit tests for new behavior.

- Public API stability
  - Do not introduce breaking changes without clear rationale and tests.
  - Maintain backward compatibility where possible; document deprecations.


## 3) Cursor and Copilot rules (repository alignment)

- Cursor rules
  - No Cursor rules found in this repository (.cursor/rules or .cursorrules).
  - If you add Cursor rules later, place them under:
    - `.cursor/rules/` or `.cursorrules` and reference them from AGENTS.md.

- Copilot rules (current, from repo directive)
  - Always start planning multi-step tasks with the plan tool: `manage_todo_list`.
  - Preface tool calls with a short 1-2 sentence rationale.
  - Provide progress updates after 3–5 tool calls or after editing more than 3 files.
  - Keep changes focused and minimize public API changes unless requested.
  - Run unit tests with `pytest` and fix only failures related to your changes.

- This AGENTS.md mirrors those conventions to ensure consistent agent behavior.


## 4) Deliverables and handoffs

- When you complete a task, summarize changes, testing performed, and next steps.
- If relevant, propose a follow-up task (e.g., add tests, update docs, improve CI).
- Provide commands to verify the work and any environment setup requirements.
