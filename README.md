# Task Manager — Docker Teaching Project

A full-stack task manager application used to teach Docker and Docker Compose in a classroom setting.

The project is intentionally simple so students can focus on Docker concepts rather than application code. It covers containers, images, Dockerfiles, networking, volumes, bind mounts, and multi-container orchestration with Docker Compose.

## Stack

- **Nginx** — reverse proxy, single entry point for all traffic
- **Frontend** — plain HTML, CSS, and JavaScript, no framework
- **Flask** — Python REST API backend
- **PostgreSQL** — persistent task storage
- **Redis** — caching layer, demonstrates cache hits and misses live

## GitHub Actions CI Pipeline

The project includes a robust CI pipeline (`.github/workflows/ci.yml`) that demonstrates:
1. **Backend Quality Checks**: Using `flake8` for linting and `bandit` for security scanning.
2. **Backend Unit Tests**: Using `pytest` with mocked services and integration tests using real PostgreSQL/Redis services in the CI environment.
3. **Frontend Quality Checks**: Using `ESLint` to ensure JavaScript best practices.
4. **Docker Smoke Test**: Automatically building and starting the entire stack with `docker compose` to ensure the project is always deployable.

This pipeline triggers on every `push` and `pull_request` to the main branch.

