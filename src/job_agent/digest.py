from __future__ import annotations

from job_agent.models import JobScore, RunInsight


def render_digest(scored_jobs: list[JobScore], insight: RunInsight) -> str:
    lines: list[str] = ["# AI Job Shortlist", ""]
    if not scored_jobs:
        lines.extend(
            [
                "No jobs met the configured score threshold.",
                "",
                "Try lowering `--min-score` or adding more target companies.",
            ]
        )
        return "\n".join(lines)

    for index, scored_job in enumerate(scored_jobs, start=1):
        job = scored_job.job
        lines.extend(
            [
                f"## {index}. {job.title} - {job.company}",
                "",
                "### Responsibilities",
                *_format_bullets(scored_job.responsibilities),
                "",
                "### Key Requirements",
                *_format_bullets(scored_job.key_requirements),
                "",
            ]
        )

    return "\n".join(lines)


def _format_bullets(items: tuple[str, ...]) -> list[str]:
    if not items:
        return ["- Not enough detail found in the current job description."]
    return [f"- {item}" for item in items]
