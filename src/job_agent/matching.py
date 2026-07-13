from __future__ import annotations

import re

from job_agent.models import Job, RoleMatch, UserProfile


def find_best_role_match(job: Job, profile: UserProfile) -> RoleMatch:
    title_text = _normalize(job.title)
    description_text = _normalize(job.description)
    best_match = RoleMatch("", 0.0, (), ())
    best_weight = -1.0

    for role_family in profile.role_families:
        title_terms = tuple(
            term for term in role_family.title_terms if _normalize(term) in title_text
        )
        description_terms = tuple(
            term
            for term in role_family.description_terms
            if _normalize(term) in description_text
        )
        weight = (len(title_terms) * 3 + len(description_terms)) * role_family.priority
        if weight > best_weight:
            best_weight = weight
            best_match = RoleMatch(
                role_family=role_family.name,
                role_priority=role_family.priority,
                title_terms=title_terms,
                description_terms=description_terms,
            )

    return best_match


def has_avoid_term(job: Job, profile: UserProfile) -> bool:
    combined = _normalize(f"{job.title} {job.description}")
    return any(_contains_term(combined, term) for term in profile.avoid_terms)


def _normalize(value: str) -> str:
    return " ".join(value.casefold().replace("/", " ").replace("-", " ").split())


def _contains_term(text: str, term: str) -> bool:
    normalized_term = _normalize(term)
    if " " in normalized_term:
        return normalized_term in text
    return re.search(rf"\b{re.escape(normalized_term)}\b", text) is not None
