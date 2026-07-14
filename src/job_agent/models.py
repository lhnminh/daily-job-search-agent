from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class RoleFamily:
    name: str
    priority: float
    title_terms: tuple[str, ...]
    description_terms: tuple[str, ...]


@dataclass(frozen=True)
class UserProfile:
    role_families: tuple[RoleFamily, ...]
    preferred_locations: tuple[str, ...]
    remote_preference: str
    seniority_terms: tuple[str, ...]
    minimum_score: int
    current_skills: tuple[str, ...]
    current_projects: tuple[str, ...]
    avoid_terms: tuple[str, ...]
    excluded_title_prefixes: tuple[str, ...] = ()
    excluded_locations: tuple[str, ...] = ()


@dataclass(frozen=True)
class Company:
    name: str
    category: str
    priority: float
    careers_url: str
    source_type: str = "manual"
    source_key: str = ""


@dataclass(frozen=True)
class Job:
    id: str
    company: str
    title: str
    location: str
    department: str
    url: str
    description: str
    posted_at: date | None
    seniority: str


@dataclass(frozen=True)
class RoleMatch:
    role_family: str
    role_priority: float
    title_terms: tuple[str, ...]
    description_terms: tuple[str, ...]


@dataclass(frozen=True)
class JobScore:
    job: Job
    role_match: RoleMatch
    score: int
    reasons: tuple[str, ...]
    skill_signals: tuple[str, ...] = field(default_factory=tuple)
    responsibilities: tuple[str, ...] = field(default_factory=tuple)
    key_requirements: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LearningSignal:
    signal_type: str
    signal: str
    evidence_count: int


@dataclass(frozen=True)
class RunInsight:
    top_signals: tuple[LearningSignal, ...]
    recommended_focus: tuple[str, ...]
    project_ideas: tuple[str, ...]
    interview_story_prompts: tuple[str, ...]
