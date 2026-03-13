# Contributing to YottaML

Thank you for your interest in contributing!

## Getting started

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/YottaML.git
   cd YottaML
   ```

2. Create a virtual environment and install the package in editable mode with dev dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Running tests

```bash
pytest
```

For verbose output:
```bash
pytest -v
```

## Code style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. It runs automatically via pre-commit, but you can also run it manually:

```bash
ruff check .          # lint
ruff format .         # format
```

## Submitting a pull request

1. Create a branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes and commit using [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` — new feature
   - `fix:` — bug fix
   - `docs:` — documentation only
   - `refactor:` — code change that neither fixes a bug nor adds a feature
   - `test:` — adding or updating tests
   - `chore:` — build process, dependency updates, etc.

   Example:
   ```
   feat: add --timeout option to pods create
   ```

3. Push your branch and open a pull request against `main`.

4. Ensure all CI checks pass before requesting review.

## Reporting bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml) template. Please include the `yottaml` version (`pip show yottaml`), Python version, and a minimal reproduction.

## Requesting features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml) template. For significant changes, open an issue first to discuss the approach before writing code.

## License

By contributing, you agree that your contributions will be licensed under the [Apache 2.0 License](LICENSE).
