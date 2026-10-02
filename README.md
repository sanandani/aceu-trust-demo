# ACE-U Trust Demo

A small, Dockerized educational demo inspired by Shubham Anandani's
“Trust-Aware Professional Identity Representation in AI-Mediated Systems”
(IEEE SoutheastCon 2026).

ACE-U represents four distinct dimensions of professional identity:
Authenticity, Credibility, Empathy, and Uniqueness.

## Run locally

Prerequisite: Docker Desktop.

```bash
docker compose up --build -d
```

Open http://localhost:8000/docs for the interactive API documentation.

Example endpoints:

- `GET /health`
- `GET /profiles`
- `GET /profiles/builder/aceu`

Stop the demo with `docker compose down`.

## Docker design

The Dockerfile uses separate dependency-builder and runtime stages.
The runtime container runs as a non-root user and includes a health check.

## Important limitation

All profiles and evidence are fictional. The illustrative indices are calculated
using transparent, unvalidated rules over synthetic examples; they are not assessments
of real people. Do not use this demo for hiring or other consequential decisions.

## Tests

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements-dev.txt
./.venv/bin/python -m pytest -q
```

For a guided explanation, see [the Docker walkthrough](docs/DOCKER-WALKTHROUGH.md).
The illustrative values are calculated from synthetic example evidence in
`scoring.py`; they are not validated measures of human trustworthiness.
