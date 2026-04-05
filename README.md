# Task Manager — Docker Teaching Project

A full-stack task manager application used to teach Docker and Docker Compose in a classroom setting.

The project is intentionally simple so students can focus on Docker concepts rather than application code. It covers containers, images, Dockerfiles, networking, volumes, bind mounts, and multi-container orchestration with Docker Compose.

## Stack

- **Nginx** — reverse proxy, single entry point for all traffic
- **Frontend** — plain HTML, CSS, and JavaScript, no framework
- **Flask** — Python REST API backend
- **PostgreSQL** — persistent task storage
- **Redis** — caching layer, demonstrates cache hits and misses live

