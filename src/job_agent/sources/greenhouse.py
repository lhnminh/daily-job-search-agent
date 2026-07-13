from __future__ import annotations

import json
from datetime import date
from urllib.request import urlopen

from job_agent.models import Company, Job
from job_agent.sources.html_sections import html_to_markdownish


GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def fetch_greenhouse_jobs(company: Company, *, timeout: int = 20) -> list[Job]:
    if not company.source_key:
        return []

    url = GREENHOUSE_URL.format(board=company.source_key)
    with urlopen(url, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    jobs = []
    for item in payload.get("jobs", []):
        jobs.append(
            Job(
                id=f"greenhouse-{company.source_key}-{item['id']}",
                company=company.name,
                title=item.get("title", ""),
                location=(item.get("location") or {}).get("name", ""),
                department=_department_name(item),
                url=item.get("absolute_url", ""),
                description=html_to_markdownish(item.get("content", "")),
                posted_at=_parse_greenhouse_date(item.get("first_published")),
                seniority="",
            )
        )
    return jobs


def _department_name(item: dict) -> str:
    departments = item.get("departments") or []
    if not departments:
        return ""
    return departments[0].get("name", "")


def _parse_greenhouse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])

