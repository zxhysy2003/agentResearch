"""Usage: PYTHONPATH=src python -m benchmark validate benchmarks/examples/*.json"""

import argparse
from pathlib import Path

from benchmark.dataset import SnapshotStore, export_schema, load_case


def main():
    parser = argparse.ArgumentParser(description="AgentResearch benchmark contracts")
    sub = parser.add_subparsers(dest="command", required=True)
    schema = sub.add_parser("schema")
    schema.add_argument("output", type=Path)
    validate = sub.add_parser("validate")
    validate.add_argument("cases", type=Path, nargs="+")
    validate.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "schema":
        export_schema(args.output)
    else:
        store = SnapshotStore(args.manifest) if args.manifest else None
        ids = set()
        for path in args.cases:
            case = load_case(path)
            if case.id in ids:
                raise ValueError(f"duplicate case ID: {case.id}")
            ids.add(case.id)
            if store:
                store.validate_case(case)
            print(f"Valid: {case.id}")


if __name__ == "__main__":
    main()
