from __future__ import annotations

from collections import Counter

from job_agent.models import JobScore, LearningSignal, RunInsight, UserProfile


SIGNAL_RULES: dict[str, tuple[str, ...]] = {
    "production AI deployment": (
        "production ai",
        "production systems",
        "deploy",
        "deployment"
    ),
    "customer-facing technical ownership": (
        "customer",
        "enterprise",
        "technical ownership",
        "implementation",
    ),
    "AI infrastructure coordination": (
        "ai infrastructure",
        "roadmap",
        "cross-functional",
        "stakeholder",
    ),
    "LLM application development": (
        "llm",
        "rag",
        "agents",
        "agentic",
        "model integration",
    ),
    "evaluation and quality systems": (
        "evaluation",
        "eval",
        "monitoring",
    ),
    "solution architecture": (
        "solution architecture",
        "technical discovery",
    ),
    "Python implementation": (
        "python",
    ),
}

SIGNAL_TYPES: dict[str, str] = {
    "production AI deployment": "technical_skills",
    "customer-facing technical ownership": "execution_skills",
    "AI infrastructure coordination": "execution_skills",
    "LLM application development": "technical_skills",
    "evaluation and quality systems": "technical_skills",
    "solution architecture": "domain_signals",
    "Python implementation": "technical_skills",
}


def attach_skill_signals(scored_jobs: list[JobScore]) -> list[JobScore]:
    enriched = []
    for scored_job in scored_jobs:
        signals = tuple(extract_job_signals(scored_job))
        responsibilities, key_requirements = extract_responsibilities_and_requirements(
            scored_job
        )
        enriched.append(
            JobScore(
                job=scored_job.job,
                role_match=scored_job.role_match,
                score=scored_job.score,
                reasons=scored_job.reasons,
                skill_signals=signals,
                responsibilities=tuple(responsibilities),
                key_requirements=tuple(key_requirements),
            )
        )
    return enriched


def extract_job_signals(scored_job: JobScore) -> list[str]:
    text = f"{scored_job.job.title} {scored_job.job.description}".casefold()
    signals = []
    for signal, terms in SIGNAL_RULES.items():
        if any(term in text for term in terms):
            signals.append(signal)
    return signals


def extract_responsibilities_and_requirements(
    scored_job: JobScore,
) -> tuple[list[str], list[str]]:
    description = scored_job.job.description
    markdown_sections = _extract_markdown_sections(description)
    if markdown_sections:
        return markdown_sections

    labeled_sections = _extract_labeled_sections(description)
    if labeled_sections:
        return labeled_sections

    responsibilities: list[str] = []
    requirements: list[str] = []

    for sentence in _split_sentences(description):
        lowered = sentence.casefold()
        if _looks_like_responsibility(lowered):
            responsibilities.append(sentence)
        if _looks_like_requirement(lowered):
            requirements.append(sentence)

    if not responsibilities:
        responsibilities = _fallback_responsibilities(scored_job)
    if not requirements:
        requirements = _fallback_requirements(scored_job)

    return responsibilities[:3], requirements[:3]


def build_run_insight(scored_jobs: list[JobScore], profile: UserProfile) -> RunInsight:
    signal_counts = Counter(
        signal for scored_job in scored_jobs for signal in scored_job.skill_signals
    )
    top_signals = tuple(
        LearningSignal(
            signal_type=SIGNAL_TYPES.get(signal, "domain_signals"),
            signal=signal,
            evidence_count=count,
        )
        for signal, count in signal_counts.most_common(5)
    )
    recommendations = _recommend_focus(top_signals, profile)
    return RunInsight(
        top_signals=top_signals,
        recommended_focus=tuple(recommendations[:3]),
        project_ideas=tuple(_project_ideas(top_signals)[:2]),
        interview_story_prompts=tuple(_interview_prompts(top_signals)[:2]),
    )


def _recommend_focus(
    top_signals: tuple[LearningSignal, ...],
    profile: UserProfile,
) -> list[str]:
    current_skills = {skill.casefold() for skill in profile.current_skills}
    focus: list[str] = []
    signal_names = {signal.signal for signal in top_signals}

    if "production AI deployment" in signal_names:
        focus.append("Build or write up one production-style AI app with deployment notes.")
    if "evaluation and quality systems" in signal_names:
        focus.append("Add evaluation, monitoring, or quality checks to an LLM project.")
    if "customer-facing technical ownership" in signal_names:
        focus.append("Prepare a story about turning ambiguous customer needs into a technical solution.")
    if "AI infrastructure coordination" in signal_names:
        focus.append("Practice explaining roadmap tradeoffs across product, research, and engineering.")
    if "LLM application development" in signal_names and "llm apps" not in current_skills:
        focus.append("Build a small RAG or agent workflow and document the design choices.")
    if not focus:
        focus.append("Compare the selected jobs manually and identify one repeated skill to practice.")
    return focus


def _project_ideas(top_signals: tuple[LearningSignal, ...]) -> list[str]:
    signal_names = {signal.signal for signal in top_signals}
    ideas = []
    if "production AI deployment" in signal_names:
        ideas.append("Ship a small AI workflow with logging, retries, and a clear deployment README.")
    if "LLM application development" in signal_names:
        ideas.append("Create a RAG or agent demo with an evaluation report.")
    if "customer-facing technical ownership" in signal_names:
        ideas.append("Write a case study that starts from a customer problem and ends with an AI solution.")
    if not ideas:
        ideas.append("Build one portfolio artifact around the highest-scoring job requirement.")
    return ideas


def _interview_prompts(top_signals: tuple[LearningSignal, ...]) -> list[str]:
    signal_names = {signal.signal for signal in top_signals}
    prompts = []
    if "customer-facing technical ownership" in signal_names:
        prompts.append("Prepare an example of handling unclear requirements with a stakeholder.")
    if "AI infrastructure coordination" in signal_names:
        prompts.append("Prepare an example of coordinating a technical launch across teams.")
    if "evaluation and quality systems" in signal_names:
        prompts.append("Prepare an example of measuring whether an AI feature worked.")
    if not prompts:
        prompts.append("Prepare one story connecting your current projects to the selected roles.")
    return prompts


def _split_sentences(description: str) -> list[str]:
    normalized = " ".join(description.split())
    parts = []
    for chunk in normalized.replace(";", ".").split("."):
        sentence = chunk.strip()
        if sentence:
            parts.append(sentence)
    return parts


def _extract_labeled_sections(description: str) -> tuple[list[str], list[str]] | None:
    lowered = description.casefold()
    responsibility_marker = "responsibilities:"
    requirement_marker = "key requirements:"
    if responsibility_marker not in lowered or requirement_marker not in lowered:
        return None

    responsibility_start = lowered.index(responsibility_marker) + len(
        responsibility_marker
    )
    requirement_start = lowered.index(requirement_marker)
    requirement_content_start = requirement_start + len(requirement_marker)

    responsibilities_text = description[responsibility_start:requirement_start]
    requirements_text = description[requirement_content_start:]
    return (
        _split_section_items(responsibilities_text)[:3],
        _split_section_items(requirements_text)[:3],
    )


def _extract_markdown_sections(description: str) -> tuple[list[str], list[str]] | None:
    current_section = ""
    responsibilities: list[str] = []
    requirements: list[str] = []
    about_role_items: list[str] = []
    role_bullet_items: list[str] = []

    for raw_line in description.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading = _normalize_heading(line)
        if heading:
            current_section = _classify_heading(heading)
            continue

        item = _section_item_text(line)
        if not item:
            continue

        if current_section == "about_role":
            about_role_items.append(item)
        elif current_section == "responsibilities":
            role_bullet_items.append(item)
        elif current_section == "requirements":
            requirements.append(item)

    responsibilities = about_role_items or role_bullet_items
    if not responsibilities and not requirements:
        return None
    return responsibilities[:6], requirements[:6]


def _normalize_heading(line: str) -> str:
    stripped = line.strip()
    is_hash_heading = stripped.startswith("#")
    is_bold_heading = stripped.startswith("**") and stripped.endswith("**")
    if not is_hash_heading and not is_bold_heading:
        return ""
    normalized = stripped.strip("#").strip()
    normalized = normalized.strip("*").strip()
    return (
        normalized.casefold()
        .replace("’", "'")
        .replace("`", "")
        .replace(",", "")
        .strip()
    )


def _classify_heading(heading: str) -> str:
    if "about the role" in heading or heading == "about role":
        return "about_role"
    if (
        "thrive" in heading
        or "qualifications" in heading
        or "requirements" in heading
        or "looking for" in heading
        or "good fit" in heading
    ):
        return "requirements"
    if "in this role" in heading or "you will" in heading or "you'll do" in heading:
        return "responsibilities"
    return ""


def _section_item_text(line: str) -> str:
    if line.startswith(("-", "*")):
        return line.lstrip("-*").strip()
    return line


def _split_section_items(value: str) -> list[str]:
    items = []
    for chunk in value.replace(";", ".").split("."):
        item = chunk.strip(" -\n\t")
        if item:
            items.append(item)
    return items


def _looks_like_responsibility(sentence: str) -> bool:
    responsibility_terms = (
        "work ",
        "drive ",
        "build ",
        "own ",
        "partner ",
        "lead ",
        "create ",
        "guide ",
        "translate ",
        "deploy ",
        "design ",
        "implement ",
    )
    return any(term in f" {sentence} " for term in responsibility_terms)


def _looks_like_requirement(sentence: str) -> bool:
    requirement_terms = (
        "requires",
        "required",
        "strong",
        "comfort with",
        "using",
        "python",
        "llm",
        "rag",
        "evaluation",
        "stakeholder",
        "roadmap",
        "production systems",
    )
    return any(term in sentence for term in requirement_terms)


def _fallback_responsibilities(scored_job: JobScore) -> list[str]:
    role_family = scored_job.role_match.role_family or "the role"
    return [f"Work on responsibilities aligned with {role_family}."]


def _fallback_requirements(scored_job: JobScore) -> list[str]:
    if scored_job.skill_signals:
        return [f"Demonstrate experience with {signal}." for signal in scored_job.skill_signals]
    return ["Review the job description manually for explicit requirements."]
