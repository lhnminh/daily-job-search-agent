from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from job_agent.models import JobScore, RunInsight


def save_run_history(path: Path, scored_jobs: list[JobScore], insight: RunInsight) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "jobs": [
            {
                "id": scored_job.job.id,
                "company": scored_job.job.company,
                "title": scored_job.job.title,
                "score": scored_job.score,
                "role_family": scored_job.role_match.role_family,
                "skill_signals": list(scored_job.skill_signals),
                "url": scored_job.job.url,
            }
            for scored_job in scored_jobs
        ],
        "top_signals": [
            {
                "signal_type": signal.signal_type,
                "signal": signal.signal,
                "evidence_count": signal.evidence_count,
            }
            for signal in insight.top_signals
        ],
        "recommended_focus": list(insight.recommended_focus),
    }
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, sort_keys=True))
        file.write("\n")
