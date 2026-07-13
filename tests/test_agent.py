from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from job_agent.config import load_companies, load_jobs, load_profile
from job_agent.digest import render_digest
from job_agent.insights import (
    attach_skill_signals,
    build_run_insight,
    extract_responsibilities_and_requirements,
)
from job_agent.matching import find_best_role_match
from job_agent.models import Job, JobScore, RoleMatch
from job_agent.scoring import filter_top_jobs, score_jobs


class AgentWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = load_profile(PROJECT_ROOT / "config" / "profile.json")
        self.companies = load_companies(PROJECT_ROOT / "config" / "companies.json")
        self.jobs = load_jobs(PROJECT_ROOT / "data" / "mock_jobs.json")

    def test_loads_config_and_jobs(self) -> None:
        self.assertGreaterEqual(len(self.profile.role_families), 3)
        self.assertIn("openai", self.companies)
        self.assertGreaterEqual(len(self.jobs), 8)

    def test_matches_forward_deployed_engineer_family(self) -> None:
        job = next(item for item in self.jobs if item.id == "openai-fde-001")
        role_match = find_best_role_match(job, self.profile)
        self.assertEqual(role_match.role_family, "Forward Deployed Engineer")
        self.assertIn("forward deployed engineer", role_match.title_terms)

    def test_matches_tpm_family(self) -> None:
        job = next(item for item in self.jobs if item.id == "anthropic-tpm-001")
        role_match = find_best_role_match(job, self.profile)
        self.assertEqual(role_match.role_family, "Technical Program Management")

    def test_scoring_ranks_relevant_roles_above_low_fit_role(self) -> None:
        scored = score_jobs(
            self.jobs,
            self.profile,
            self.companies,
            today=date(2026, 7, 13),
        )
        by_id = {item.job.id: item for item in scored}
        self.assertGreater(by_id["openai-fde-001"].score, by_id["generic-lowfit-001"].score)
        self.assertGreaterEqual(by_id["openai-fde-001"].score, self.profile.minimum_score)

    def test_filter_top_jobs_uses_threshold_and_limit(self) -> None:
        scored = score_jobs(
            self.jobs,
            self.profile,
            self.companies,
            today=date(2026, 7, 13),
        )
        top_jobs = filter_top_jobs(scored, limit=5, minimum_score=60)
        self.assertLessEqual(len(top_jobs), 5)
        self.assertTrue(all(item.score >= 60 for item in top_jobs))

    def test_insights_extract_repeated_market_signals(self) -> None:
        scored = score_jobs(
            self.jobs,
            self.profile,
            self.companies,
            today=date(2026, 7, 13),
        )
        top_jobs = filter_top_jobs(scored, limit=8, minimum_score=60)
        enriched = attach_skill_signals(top_jobs)
        insight = build_run_insight(enriched, self.profile)
        signal_names = {signal.signal for signal in insight.top_signals}
        self.assertIn("customer-facing technical ownership", signal_names)
        self.assertTrue(insight.recommended_focus)

    def test_extracts_responsibilities_and_key_requirements(self) -> None:
        scored = score_jobs(
            self.jobs,
            self.profile,
            self.companies,
            today=date(2026, 7, 13),
        )
        fde_score = next(item for item in scored if item.job.id == "openai-fde-001")
        responsibilities, requirements = extract_responsibilities_and_requirements(
            fde_score
        )
        self.assertTrue(responsibilities)
        self.assertTrue(requirements)
        self.assertTrue(any("Work directly" in item for item in responsibilities))
        self.assertTrue(any("Python" in item for item in requirements))

    def test_extracts_realistic_markdown_about_role_and_requirements(self) -> None:
        description = """**About The Role**

We are seeking a solutions engineer to partner with our customers and ensure they achieve tangible business value from our models through ChatGPT and the OpenAI API.

**In This Role, You Will**

- Deliver an exceptional pre-sales customer experience for prospects and customers by providing technical expertise.
- Demonstrate how leveraging OpenAI APIs and ChatGPT can meet customers' business needs.
- Create and maintain documentation, guides, and FAQs related to common questions.

**You’ll Thrive In This Role If You**

- Have 3+ years of experience in a technical pre-sales or similar role.
- Demonstrate a thorough understanding of IT security principles and customer requirements.
- Have foundational training in programming languages like Python or Javascript.
"""
        scored_job = JobScore(
            job=Job(
                id="openai-solutions-realistic",
                company="OpenAI",
                title="Solutions Engineer",
                location="San Francisco, CA",
                department="Go To Market",
                url="https://openai.com/careers/example",
                description=description,
                posted_at=None,
                seniority="senior",
            ),
            role_match=RoleMatch(
                role_family="Forward Deployed Engineer",
                role_priority=1.0,
                title_terms=("solutions engineer",),
                description_terms=(),
            ),
            score=80,
            reasons=(),
        )

        responsibilities, requirements = extract_responsibilities_and_requirements(
            scored_job
        )

        self.assertEqual(len(responsibilities), 1)
        self.assertEqual(len(requirements), 3)
        self.assertIn("seeking a solutions engineer", responsibilities[0])
        self.assertIn("3+ years", requirements[0])
        self.assertIn("Python or Javascript", requirements[2])

    def test_digest_only_contains_responsibilities_and_key_requirements(self) -> None:
        scored = score_jobs(
            self.jobs,
            self.profile,
            self.companies,
            today=date(2026, 7, 13),
        )
        top_jobs = filter_top_jobs(scored, limit=5, minimum_score=60)
        enriched = attach_skill_signals(top_jobs)
        insight = build_run_insight(enriched, self.profile)
        output = render_digest(enriched, insight)
        self.assertIn("# AI Job Shortlist", output)
        self.assertIn("### Responsibilities", output)
        self.assertIn("### Key Requirements", output)
        self.assertIn("Forward Deployed Engineer", output)
        self.assertNotIn("**Match:**", output)
        self.assertNotIn("**Why:**", output)
        self.assertNotIn("**Skill signals:**", output)
        self.assertNotIn("What This Means For Your Search", output)


if __name__ == "__main__":
    unittest.main()
