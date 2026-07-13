from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from job_agent.models import Company, Job, RoleFamily, UserProfile


def load_profile(path: Path) -> UserProfile:
    data = _load_json(path)
    role_families = tuple(
        RoleFamily(
            name=item["name"],
            priority=float(item["priority"]),
            title_terms=tuple(item["title_terms"]),
            description_terms=tuple(item["description_terms"]),
        )
        for item in data["target_role_families"]
    )
    return UserProfile(
        role_families=role_families,
        preferred_locations=tuple(data["preferred_locations"]),
        remote_preference=data["remote_preference"],
        seniority_terms=tuple(data["seniority_terms"]),
        minimum_score=int(data["minimum_score"]),
        current_skills=tuple(data["current_skills"]),
        current_projects=tuple(data["current_projects"]),
        avoid_terms=tuple(data["avoid_terms"]),
    )


def load_companies(path: Path) -> dict[str, Company]:
    companies = {}
    for item in _load_json(path):
        company = Company(
            name=item["name"],
            category=item["category"],
            priority=float(item["priority"]),
            careers_url=item["careers_url"],
        )
        companies[company.name.casefold()] = company
    return companies


def load_jobs(path: Path) -> list[Job]:
    jobs = []
    for item in _load_json(path):
        jobs.append(
            Job(
                id=item["id"],
                company=item["company"],
                title=item["title"],
                location=item["location"],
                department=item["department"],
                url=item["url"],
                description=item["description"],
                posted_at=_parse_date(item.get("posted_at")),
                seniority=item.get("seniority", ""),
            )
        )
    return jobs


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)
