from __future__ import annotations

from datetime import date

from job_agent.matching import find_best_role_match, has_avoid_term
from job_agent.models import Company, Job, JobScore, UserProfile


def score_jobs(
    jobs: list[Job],
    profile: UserProfile,
    companies: dict[str, Company],
    *,
    today: date | None = None,
) -> list[JobScore]:
    run_date = today or date.today()
    scored_jobs = [
        score_job(job, profile, companies, today=run_date)
        for job in jobs
        if not has_avoid_term(job, profile)
    ]
    return sorted(scored_jobs, key=lambda item: item.score, reverse=True)


def score_job(
    job: Job,
    profile: UserProfile,
    companies: dict[str, Company],
    *,
    today: date | None = None,
) -> JobScore:
    run_date = today or date.today()
    role_match = find_best_role_match(job, profile)
    company = companies.get(job.company.casefold())
    reasons: list[str] = []

    company_points = round((company.priority if company else 0.4) * 25)
    if company:
        reasons.append(f"{job.company} is in the target company list.")
    else:
        reasons.append(f"{job.company} is not configured, so company priority is lower.")

    title_points = min(25, len(role_match.title_terms) * 12)
    if role_match.title_terms:
        reasons.append(
            f"Title matches {role_match.role_family}: {', '.join(role_match.title_terms)}."
        )
    else:
        reasons.append("Title is not a direct target-role match.")

    ai_points = min(20, len(role_match.description_terms) * 4)
    if role_match.description_terms:
        reasons.append(
            "Description includes relevant signals: "
            f"{', '.join(role_match.description_terms[:4])}."
        )
    else:
        reasons.append("Description has weak AI-role signals.")

    location_points, location_reason = _score_location(job, profile)
    reasons.append(location_reason)

    seniority_points, seniority_reason = _score_seniority(job, profile)
    reasons.append(seniority_reason)

    freshness_points, freshness_reason = _score_freshness(job, run_date)
    reasons.append(freshness_reason)

    total = min(
        100,
        company_points
        + title_points
        + ai_points
        + location_points
        + seniority_points
        + freshness_points,
    )
    return JobScore(job=job, role_match=role_match, score=total, reasons=tuple(reasons))


def filter_top_jobs(
    scored_jobs: list[JobScore],
    *,
    limit: int,
    minimum_score: int,
) -> list[JobScore]:
    return [job for job in scored_jobs if job.score >= minimum_score][:limit]


def _score_location(job: Job, profile: UserProfile) -> tuple[int, str]:
    location = job.location.casefold()
    preferred = [item.casefold() for item in profile.preferred_locations]
    if "remote" in location and profile.remote_preference == "preferred":
        return 10, "Remote role matches the remote preference."
    if any(item in location for item in preferred):
        return 8, f"Location matches preferences: {job.location}."
    return 3, f"Location is not a strong preference match: {job.location}."


def _score_seniority(job: Job, profile: UserProfile) -> tuple[int, str]:
    seniority = job.seniority.casefold()
    if any(term.casefold() in seniority for term in profile.seniority_terms):
        return 10, f"Seniority appears aligned: {job.seniority}."
    if not seniority:
        return 5, "Seniority is not specified."
    return 3, f"Seniority may be less aligned: {job.seniority}."


def _score_freshness(job: Job, today: date) -> tuple[int, str]:
    if not job.posted_at:
        return 4, "Posting date is unknown."
    age_days = max(0, (today - job.posted_at).days)
    if age_days <= 7:
        return 10, f"Posted recently: {age_days} days ago."
    if age_days <= 21:
        return 7, f"Still fairly fresh: {age_days} days old."
    return 3, f"Older posting: {age_days} days old."
