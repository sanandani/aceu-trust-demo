"""Command line interface for read-only Entra workload identity scoring."""
import argparse
import json
import sys
from pathlib import Path

from . import HOMEPAGE
from .graph import export_graph
from .report import to_json, to_markdown, to_sarif
from .scoring import score_identities


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=f"Read-only ACE-U assessment for Microsoft Entra workload identities. Project: {HOMEPAGE}")
    result.add_argument("--input", help="Saved Graph JSON export for offline scoring")
    result.add_argument("--out", default="-", help="Output file (default: stdout)")
    result.add_argument("--format", choices=("json", "markdown", "sarif"), default="json")
    result.add_argument("--fail-under", type=float, help="Exit 1 if any identity score is below this threshold")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        export = json.loads(Path(args.input).read_text()) if args.input else export_graph()
        results = score_identities(export)
        rendered = {"json": to_json, "markdown": to_markdown, "sarif": to_sarif}[args.format](results)
        if args.out == "-":
            sys.stdout.write(rendered)
        else:
            Path(args.out).write_text(rendered)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"aceu-entra: {exc}", file=sys.stderr)
        return 2
    return int(args.fail_under is not None and any(r["total"] < args.fail_under for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
