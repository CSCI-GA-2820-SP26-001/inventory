# Inventory Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python_3.12-blue.svg)](https://python.org/)

[![CI](https://github.com/CSCI-GA-2820-SP26-001/inventory/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP26-001/inventory/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP26-001/inventory/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SP26-001/inventory)

A REST API service for managing inventory items. Built with Flask, Flask-RESTX, and SQLAlchemy.

## Overview

This service provides CRUD operations for inventory records. Each inventory item has a name, product ID, quantity on hand, restock level, and condition (`new`, `open_box`, or `used`). The `/service` folder contains the `Inventory` model and REST routes; `/tests` contains test suites for the model and service.

## Prerequisites

- Python 3.12
- Pipenv (recommended) or pip

## Setup

### Using this repo as a template

Press the **Use this template** button on GitHub to create your own repository from this template.

### Local setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd inventory
   ```

2. Copy environment configuration:
   ```bash
   cp dot-env-example .env
   ```
   Edit `.env` if needed (e.g. database URL).

3. Install dependencies:
   ```bash
   pipenv install --dev
   ```
   Or with Make:
   ```bash
   make install
   ```

4. Optional — copy hidden files if you moved files manually:
   ```bash
   cp .gitignore   ../<your_repo_folder>/
   cp .flaskenv    ../<your_repo_folder>/
   cp .gitattributes ../<your_repo_folder>/
   ```

### Pipenv troubleshooting (macOS/Linux)

If you see `zsh: command not found: pipenv`, install Pipenv first:

```bash
python3 -m pip install --user pipenv
```

Or with Homebrew:

```bash
brew install pipenv
```

Then verify:

```bash
pipenv --version
```

## Running the Service

```bash
honcho start
# or
make run
```

The API will be available at the URL configured in `.flaskenv` (default typically `http://localhost:8000`).

Swagger/OpenAPI docs are available at:

- `http://localhost:8000/api/docs`

## Development

| Command     | Description                    |
|------------|--------------------------------|
| `make install` | Install Python dependencies   |
| `make lint`    | Run flake8 and pylint         |
| `make test`    | Run pytest with coverage      |
| `make run`     | Start the service (honcho)    |
| `make secret`  | Generate a secret hex key     |

## Project Layout

```text
.gitignore          - Ignores Vagrant and other metadata
.flaskenv           - Environment variables for Flask
.gitattributes      - Line ending handling (e.g. CRLF)
.devcontainer/      - VSCode Remote Containers support
dot-env-example     - Copy to .env for local config
Pipfile             - Python dependencies (Pipenv)
Makefile            - Development and build commands

service/                    - Main service package
├── __init__.py             - Package initializer
├── config.py               - Configuration
├── models.py               - Inventory model and ItemCondition enum
├── routes.py               - REST API routes
└── common/
    ├── cli_commands.py     - Flask CLI (e.g. recreate tables)
    ├── error_handlers.py   - HTTP error handling
    ├── log_handlers.py     - Logging setup
    └── status.py           - HTTP status constants

tests/
├── __init__.py
├── factories.py            - Test factories
├── test_cli_commands.py    - CLI tests
├── test_models.py          - Model tests
└── test_routes.py          - Route tests
```

## API Summary

The primary API is exposed under the `/api` prefix using Flask-RESTX:

- `GET /api/inventory`
- `POST /api/inventory`
- `GET /api/inventory/<id>`
- `PUT /api/inventory/<id>`
- `DELETE /api/inventory/<id>`
- `PUT /api/inventory/<id>/restock` with JSON `{"amount": <positive integer>}`

Health endpoints:

- `GET /health`
- `GET /api/health`

For backward compatibility, legacy non-prefixed `/inventory` routes are still available.

Each record includes:

- **name** — Item name
- **product_id** — Product identifier
- **quantity_on_hand** — Current stock
- **restock_level** — Threshold for restocking
- **condition** — One of: `new`, `open_box`, `used`
- **created_at** / **last_updated** — Timestamps (managed by the service)

Use the root URL (`/`) for a simple service description. Full endpoints are defined in `service/routes.py`.

## Kubernetes Manifests

Kubernetes manifests are included for both the application and PostgreSQL:

- `k8s/deployment.yaml` - Inventory app Deployment (includes readiness/liveness probe on `/health`)
- `k8s/service.yaml` - ClusterIP Service for the app
- `k8s/ingress.yaml` - Ingress routing to the app Service
- `k8s/postgres/statefulset.yaml` - PostgreSQL StatefulSet
- `k8s/postgres/service.yaml` - Headless Service for PostgreSQL
- `k8s/postgres/pvc.yaml` - PersistentVolumeClaim for PostgreSQL data

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE).

This repository is part of the New York University (NYU) course **CSCI-GA.2820-001 DevOps and Agile Methodologies**, created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
