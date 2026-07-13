from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from job_agent.config import load_companies, load_jobs, load_profile
from job_agent.digest import render_digest
from job_agent.history import save_run_history
from job_agent.insights import attach_skill_signals, build_run_insight
from job_agent.scoring import filter_top_jobs, score_jobs
from job_agent.sources.live import fetch_live_jobs


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE_PATH = PROJECT_ROOT / "config" / "profile.json"
DEFAULT_COMPANIES_PATH = PROJECT_ROOT / "config" / "companies.json"
DEFAULT_JOBS_PATH = PROJECT_ROOT / "data" / "mock_jobs.json"
DEFAULT_HISTORY_PATH = PROJECT_ROOT / "data" / "run_history.jsonl"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "latest.md"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        output = run_command(args)
        print(output)
        return 0

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-agent",
        description="Find high-signal AI jobs and infer what to work on next.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Generate an on-demand job shortlist.")
    run_parser.add_argument("--source", choices=("live", "mock"), default="live")
    run_parser.add_argument("--limit", type=int, default=10)
    run_parser.add_argument("--min-score", type=int, default=None)
    run_parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE_PATH)
    run_parser.add_argument("--companies", type=Path, default=DEFAULT_COMPANIES_PATH)
    run_parser.add_argument("--jobs", type=Path, default=DEFAULT_JOBS_PATH)
    run_parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY_PATH)
    run_parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    run_parser.add_argument("--no-save-report", action="store_true")
    run_parser.add_argument("--no-save-history", action="store_true")
    return parser


def run_command(args: argparse.Namespace) -> str:
    profile = load_profile(args.profile)
    companies = load_companies(args.companies)
    if args.source == "live":
        jobs = fetch_live_jobs(companies)
    else:
        jobs = load_jobs(args.jobs)

    minimum_score = args.min_score
    if minimum_score is None:
        minimum_score = profile.minimum_score
    else:
        profile = replace(profile, minimum_score=minimum_score)

    scored = score_jobs(jobs, profile, companies)
    shortlist = filter_top_jobs(
        scored,
        limit=max(1, args.limit),
        minimum_score=minimum_score,
    )
    enriched = attach_skill_signals(shortlist)
    insight = build_run_insight(enriched, profile)

    if not args.no_save_history:
        save_run_history(args.history, enriched, insight)

    output = render_digest(enriched, insight)
    if not args.no_save_report:
        save_markdown_report(args.report, output)
    return output


def save_markdown_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")
