# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Apache 2.0 `LICENSE` file
- CI workflow: pytest matrix across Python 3.9, 3.11, 3.12 + ruff lint check
- GitHub issue templates (bug report, feature request) and PR template
- `CONTRIBUTING.md` contributor guide
- `SECURITY.md` vulnerability disclosure policy
- `.pre-commit-config.yaml` with ruff linting/formatting hooks
- `.github/dependabot.yml` for automated dependency updates
- `[project.optional-dependencies] dev` extras in `pyproject.toml`

### Changed
- `requires-python` bumped from `>=3.8` to `>=3.9`
- License updated from MIT to Apache 2.0 in `pyproject.toml` and classifier
- README rewritten to document the full CLI (`pods`, `serverless`, `tasks`, `gpus`, `credentials`) and all SDK classes

## [0.2.0] — 2026-03-12

### Added
- v2 API migration: all SDK modules now target `/v2/` endpoints
- `ElasticApi` — serverless endpoint management (create, list, get, scale, stop, start, delete, workers)
- `SkywalkerTaskApi` — task management for QUEUE-mode endpoints
- `CredentialApi` — container registry credential management
- `serverless` CLI group with full lifecycle commands
- `tasks` CLI group (list, get, count, create)
- `credentials` CLI group (list, get, create, update, delete)
- Enhanced `pods create` with `--env`, `--expose`, `--image-registry`, `--credential-id`, `--resource-type`, `--min-vram`, `--min-ram`, `--min-vcpu`, `--shm`
- `scripts/test_pods.sh` — 10-step pod lifecycle integration test
- `scripts/test_serverless.sh` — 14-step serverless lifecycle integration test

### Removed
- `deployments.py` CLI module (replaced by `serverless.py`)

## [0.1.0] — 2025-07-06

### Added
- Initial release
- `PodApi` — pod management (create, list, get, pause, resume, delete)
- `GpuApi` — GPU type listing
- `pods` and `gpus` CLI groups
- `yotta` CLI entry point
