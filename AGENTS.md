# Repository Guidelines

## Project Structure & Module Organization

AgentResearch builds on a Python toolkit using LangGraph, FastAPI, and Streamlit. Agent implementations live in `src/agents/`; register new agents in `src/agents/agents.py`. HTTP endpoints are in `src/service/`, client code in `src/client/`, shared API models in `src/schema/`, and configuration in `src/core/`. Persistence integrations live in `src/memory/`.

Benchmark contracts and grading utilities live in `src/benchmark/`; examples, exported schemas, and snapshots are in `benchmarks/`. Tests mirror subsystems under `tests/`. Use `docs/` for documentation, `media/` for assets, and `docker/` for container definitions.

## Build, Test, and Development Commands

Use Python 3.12–3.14 and uv 0.12.5, matching CI.

- `uv sync --frozen`: install locked dependencies and development tools.
- `uv run python src/run_service.py`: start the API service.
- `uv run streamlit run src/streamlit_app.py`: start the UI in another terminal.
- `docker compose watch`: build and run the local container stack.
- `uv run pytest --cov=src/ --cov-report=xml`: run tests and generate coverage.
- `uv run ruff check` and `uv run ruff format --check`: validate lint and formatting.
- `uv run pyrefly check`: check Python types.
- `uv run pymarkdown scan README.md docs/`: lint project documentation.

## Coding Style & Naming Conventions

Use four-space indentation, type annotations, and a 100-character line-length target. Follow `snake_case` for functions/modules, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants. Ruff handles formatting, import sorting, and Python modernization. Run `uv run pre-commit install` to enable local hooks.

## Testing Guidelines

Use pytest and pytest-asyncio; name files `test_*.py` and tests `test_*`. Add focused regression tests for changed behavior and mock external services. Run targeted suites such as `uv run pytest tests/benchmark -q`. Docker integration tests require running infrastructure and `--run-docker`. Codecov allows a two-percentage-point project coverage decrease; patch coverage is informational.

## Commit & Pull Request Guidelines

All new commits must follow Conventional Commits: `<type>[optional scope][!]: <description>`.
Use `feat` for new features, `fix` for bug fixes, and `docs`, `style`, `refactor`, `perf`,
`test`, `build`, `ci`, `chore`, or `revert` as appropriate for other changes. Use an optional
scope to identify the affected subsystem, such as `agents`, `service`, or `benchmark`.
Write a concise, imperative description and keep each commit focused on one logical change.
Examples: `feat(benchmark): add grading utilities` and `docs: clarify setup instructions`.
Mark breaking changes with `!` before the colon or a `BREAKING CHANGE:` footer, and explain
the impact and required migration in the commit body or footer.

PRs should explain the problem, resulting behavior, and validation performed. Link relevant
issues and include screenshots for UI changes. If squash merging, ensure the final squash
commit message also follows Conventional Commits.

## Configuration & Benchmark Integrity

Copy `.env.example` to `.env` for local configuration; never commit credentials. Preserve snapshot hashes and version changed benchmark cases. Keep ground truth out of Agent inputs and label synthetic fixtures explicitly.
