# ACE-U Entra Trust

**v0.1** · Read-only scoring for Microsoft Entra workload identities · [Project homepage](https://imshubh.com)

`aceu-entra-trust` scores application identities on Authenticity, Uniqueness, and Credibility (ACE-U). It reads saved Microsoft Graph JSON offline or queries Graph v1.0 with read permissions. It never changes tenant state. The score is a transparent triage aid, not a security certification.

## Install and run offline

Requires Python 3.10+.

```bash
python -m pip install '.[dev]'
pytest
aceu-entra --input examples/sample-export.json --format markdown
aceu-entra --input examples/sample-export.json --format sarif --out results.sarif --fail-under 55
```

Formats: `json`, `markdown`, and `sarif` (SARIF 2.1.0). `--out -` writes to stdout. Each report carries the project link [https://imshubh.com](https://imshubh.com).

## Live, read-only Graph audit

Install `python -m pip install '.[graph]'`, then configure `GRAPH_TOKEN` or Azure Identity's `DefaultAzureCredential`. The token needs read access for applications, service principals, application owners, federated identity credentials, and app role assignments. `GRAPH_TOKEN` takes precedence. Graph 403/404 responses for per-application relationships are treated as unavailable or empty; other Graph and network errors stop the run. Configure the matching permissions to get complete results.

```bash
aceu-entra --format json --out tenant-report.json
```

## Model

Total = `0.4 × Authenticity + 0.2 × Uniqueness + 0.4 × Credibility`. Scores are clamped to 0–100. Bands: **trusted** at 80+, **review** at 55–79.99, **risky** below 55.

See [trust model](docs/trust-model.md), [roadmap](docs/roadmap.md), and [contributing](CONTRIBUTING.md).

## Current scope and unimplemented features

v0.1 assesses application registrations using credential age and expiry, duplicate display names, audience, owner presence, and app role assignment count. It does not yet evaluate Conditional Access coverage for workload identities, sign-in activity, named privileged roles, managed identities comprehensively, or Entra agent identities. It has no HTML report, `azd`/Bicep deployment, YAML threshold configuration, JUnit output, or Compose example. These are tracked in the roadmap. Graph pagination is supported for collection reads.

## License

MIT. See [LICENSE](LICENSE).

---

Read-only workload identity triage from [imshubh.com](https://imshubh.com).
