from __future__ import annotations

from job_agent.models import Company, Job
from job_agent.sources.greenhouse import fetch_greenhouse_jobs
from job_agent.sources.lever import fetch_lever_jobs


def fetch_live_jobs(companies: dict[str, Company]) -> list[Job]:
    jobs: list[Job] = []
    for company in companies.values():
        if company.source_type == "greenhouse":
            jobs.extend(fetch_greenhouse_jobs(company))
        elif company.source_type == "lever":
            jobs.extend(fetch_lever_jobs(company))
    return jobs
