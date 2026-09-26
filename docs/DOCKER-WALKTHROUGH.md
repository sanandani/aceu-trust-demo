# From ACE-U concept to running container

This repository turns the ACE-U conceptual framework into a small,
inspectable API. It uses fictional profiles and transparent formulas
to demonstrate how separate identity dimensions can be represented
without collapsing them into one overall "trust score."

## Follow the evidence

Open `main.py` to see the synthetic examples. Open `scoring.py` to see
exactly how each illustrative index is calculated. Request
`/profiles/builder/aceu` to see the four dimensions, explanations,
evidence counts, and coverage notes. Empty categories return `null`:
missing evidence is not proof of a missing human quality.

These formulas are teaching examples, not findings from a validation
study. Do not use them to evaluate real people.

## Follow the container build

Run `docker compose up --build -d`. Compose builds the Dockerfile and
publishes the API on port 8000. The builder stage installs Python
dependencies into a virtual environment. The runtime stage copies
that environment and only the application code, then runs as a
non-root user. The health check calls `/health`.

Inspect the result:

```bash
docker compose ps
curl -sS http://localhost:8000/profiles/builder/aceu
docker image ls
```

Open http://localhost:8000/docs to try the API interactively.
Stop it with `docker compose down`.

The multi-stage design separates build work from runtime files.
No image-size reduction is claimed here without a measured baseline.
