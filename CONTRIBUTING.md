# Contributing

Contributions are welcome. Keep scoring deterministic and explain every rule in `docs/trust-model.md`. Avoid adding write operations or collecting tenant data beyond the stated Graph v1.0 scope.

## Development

```bash
python -m pip install '.[dev]'
pytest
aceu-entra --input examples/sample-export.json --format json
```

Add or update tests for scoring behavior and report output. Keep sample exports synthetic, remove tenant identifiers, and never commit tokens or credentials. Use focused commits and describe behavioral changes in the pull request.

Project homepage: [https://imshubh.com](https://imshubh.com).
