"""Dataset validation, isolated snapshot runs, and human grading."""

import argparse
import asyncio
from pathlib import Path

from benchmark.dataset import SnapshotStore, export_schema, load_case

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="AgentResearch benchmark contracts")
    sub = parser.add_subparsers(dest="command", required=True)
    schema = sub.add_parser("schema")
    schema.add_argument("output", type=Path)
    validate = sub.add_parser("validate")
    validate.add_argument("cases", type=Path, nargs="+")
    validate.add_argument("--manifest", type=Path)
    run = sub.add_parser("run", help="Run the GitHub snapshot development set")
    run.add_argument("--model", default="deepseek-flash", choices=["deepseek-flash"])
    run.add_argument("--repeat", type=int, default=1)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--case-id", action="append", help="Select a case; may be repeated")
    run.add_argument(
        "--cases-dir", type=Path, default=ROOT / "benchmarks/datasets/github_lookup_v1/cases"
    )
    run.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "benchmarks/snapshots/github_lookup_v1/manifest.json",
    )
    grade = sub.add_parser("grade", help="Validate human reviews and rebuild reports")
    grade.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "schema":
        export_schema(args.output)
    elif args.command == "validate":
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
    else:
        # Provider configuration is never imported for validate/schema/grade.
        try:
            if args.command == "run":
                from benchmark.runner import run_dataset

                summary = asyncio.run(
                    run_dataset(
                        output=args.output,
                        cases_dir=args.cases_dir,
                        manifest=args.manifest,
                        repeat=args.repeat,
                        model_name=args.model,
                        case_ids=args.case_id,
                    )
                )
            else:
                from benchmark.review import summarize

                summary = summarize(args.run_dir)
        except (OSError, ValueError) as exc:
            parser.exit(2, f"Error: {exc}\n")
        print(
            f"Runs={summary['total_runs']} graded={summary['graded_runs']} "
            f"ungraded={summary['ungraded_runs']} invalid={summary['invalid_reviews']} "
            f"run_failures={summary['run_failures']}"
        )
        if summary["invalid_reviews"] or (args.command == "run" and summary["run_failures"]):
            parser.exit(1)


if __name__ == "__main__":
    main()
