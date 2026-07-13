from __future__ import annotations

import json
from datetime import date
from urllib.request import urlopen

from job_agent.models import Company, Job
from job_agent.sources.html_sections import html_to_markdownish


LEVER_URL = "https://api.lever.co/v0/postings/{site}?mode=json"


def fetch_lever_jobs(company: Company, *, timeout: int = 20) -> list[Job]:
    if not company.source_key:
        return []

    url = LEVER_URL.format(site=company.source_key)
    with urlopen(url, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    jobs = []
    for item in payload:
        jobs.append(
            Job(
                id=f"lever-{company.source_key}-{item['id']}",
                company=company.name,
                title=item.get("text", ""),
                location=(item.get("categories") or {}).get("location", ""),
                department=(item.get("categories") or {}).get("team", ""),
                url=item.get("hostedUrl", ""),
                description=_lever_description(item),
                posted_at=_parse_lever_date(item.get("createdAt")),
                seniority=(item.get("categories") or {}).get("commitment", ""),
            )
        )
    return jobs


def _lever_description(item: dict) -> str:
    sections = []
    if item.get("description"):
        sections.append(html_to_markdownish(item["description"]))
    for list_item in item.get("lists", []):
        text = list_item.get("text", "")
        content = list_item.get("content", "")
        if text:
            sections.append(f"**{text}**")
        if content:
            sections.append(html_to_markdownish(content))
    return "\n\n".join(section for section in sections if section)


def _parse_lever_date(value: int | None) -> date | None:
    if not value:
        return None
    return date.fromtimestamp(value / 1000)

