# On-Demand AI Job Search Agent Plan

## Goal

Build an on-demand agent that finds 5 to 10 high-quality AI-field job openings from extremely competitive companies, ranks them against the user's target roles, and explains why each role is worth looking at.

The deeper goal is to use those jobs as market signal. Whenever the user runs the agent, they should learn what competitive AI companies actually want and decide what skills, projects, or experiences to work on next.

The agent is not mainly an application tracker. The first version is an on-demand job discovery, filtering, and learning-direction system.

## Core User Need

The user is looking for work in the AI field, but the right opportunities may appear under many different titles.

Target role families include:

- Forward Deployed Engineer
- Forward Deployed AI Engineer
- AI Engineer
- Applied AI Engineer
- Solutions Engineer, AI
- Technical Program Manager
- Technical Program Manager, AI
- AI Product / Platform Program Manager
- Developer Relations Engineer, AI
- Field Engineer, AI
- Customer Engineer, AI
- GTM Engineer, AI

The agent should search across these title variations without requiring the user to manually check every company career page.

## Product Shape

When the user clicks a button or runs a command, the agent should produce a small shortlist:

- 5 to 10 jobs.
- From highly competitive AI companies.
- Matched to the user's preferred role families.
- Ranked by relevance.
- With a short reason for each recommendation.
- With the strongest skill signals extracted from each job.
- With direct apply links.

The output should be easy to scan and useful even if the user does not apply that day.

Example run output:

```text
AI Job Shortlist

1. Forward Deployed Engineer - OpenAI
   Location: San Francisco / Remote
   Match: 92
   Why: Strong match for AI customer-facing engineering, deployment work, and technical ownership.
   Skill signals: enterprise deployments, Python, LLM applications, customer-facing ownership
   Link: ...

2. Technical Program Manager, AI Infrastructure - Anthropic
   Location: San Francisco
   Match: 86
   Why: Matches AI program management, cross-functional delivery, and infrastructure coordination.
   Skill signals: AI infrastructure, launch management, roadmap coordination
   Link: ...

This run's learning signal:
- Competitive FDE roles repeatedly ask for production AI deployment and customer-facing technical ownership.
- TPM roles emphasize AI infrastructure coordination more than generic project tracking.
- Suggested focus: build or write up one end-to-end AI deployment project.
```

## Competitive Company Targeting

The first version should focus on a curated company list instead of the whole internet.

Initial company categories:

- Frontier AI labs:
  - OpenAI
  - Anthropic
  - Google DeepMind
  - Meta AI
  - xAI
  - Mistral AI
  - Cohere
  - Perplexity
- AI infrastructure and developer platforms:
  - Databricks
  - Snowflake
  - Scale AI
  - LangChain
  - Hugging Face
  - Modal
  - Replicate
  - Baseten
  - Together AI
  - Fireworks AI
- High-signal AI product companies:
  - Cursor
  - Harvey
  - Glean
  - Sierra
  - Hebbia
  - Cognition
  - ElevenLabs
  - Runway
  - Synthesia

This list should be configurable. The user's personal target list can be stricter than the default public list.

## MVP Scope

Version 1 should answer one question:

> What are the 5 to 10 best AI-field jobs I should look at right now?

It should also answer a second question:

> Based on those jobs, what should I work on to become a stronger candidate?

MVP features:

- Configurable target role families.
- Configurable target companies.
- Job collection from company career pages or structured job-board feeds.
- Role-title expansion for similar titles.
- Rule-based scoring for relevance.
- Skill-signal extraction from job titles and descriptions.
- Learning insight based on repeated requirements.
- Markdown, terminal, or button-triggered digest.
- Deduplication so the same job does not appear every day.
- Basic history of previously surfaced jobs.

Out of scope for MVP:

- Applying to jobs automatically.
- Cover letters.
- Resume tailoring.
- Full application CRM.
- Multi-user accounts.
- Hosted web app.
- Generic job-board scraping across the entire internet.
- OS-level scheduling or background automation.

## Trigger Model

The first version should run only when the user asks for it.

Preferred trigger path:

1. CLI command for the earliest implementation.
2. Local button in a simple web UI once the core workflow works.
3. Optional OS-level automation later, only if the user wants scheduled runs.

The button should mean:

> Find strong AI jobs now and tell me what they suggest I should work on.

This keeps the product under the user's control and avoids background behavior before the matching and insight quality are good.

## Learning Intelligence

The agent should treat job posts as evidence about the market.

For each shortlist run, it should extract:

- Technical skills.
- Product or domain signals.
- Workflow responsibilities.
- Seniority expectations.
- Customer-facing expectations.
- Repeated keywords across companies.
- Gaps between the user's current profile and the jobs.

Example extracted signals:

- `production LLM systems`
- `agent evaluation`
- `RAG`
- `Python`
- `customer deployment`
- `enterprise implementation`
- `AI infrastructure`
- `cross-functional execution`
- `technical roadmap`
- `solution architecture`

The run output should include a short learning section:

```text
What this means for your search

Top repeated signals in this run:
- production AI deployment
- customer-facing technical ownership
- AI infrastructure coordination

What to work on:
- Build a small production-style AI app with monitoring and evaluation.
- Prepare one story about working with ambiguous customer requirements.
- Practice explaining tradeoffs between prompt engineering, RAG, fine-tuning, and agents.
```

The learning section should stay practical. It should not become generic motivation or a long study plan.

## Search Strategy

The agent should use a company-first search strategy.

Preferred order:

1. Greenhouse, Lever, Ashby, Workday, or company career APIs when available.
2. Company career pages with structured metadata.
3. Curated job-board searches as fallback.
4. Manual source configuration for companies that are hard to parse.

Why company-first:

- Competitive companies often post directly on their own career pages.
- Search quality is easier to control.
- The agent can avoid noisy generic job listings.
- It is easier to explain why a job appears.

## Matching Strategy

The agent should not only search exact titles. It should search by role family.

### Forward Deployed Engineer Family

Strong title matches:

- Forward Deployed Engineer
- Forward Deployed AI Engineer
- Forward Deployed Software Engineer
- Field Engineer
- AI Field Engineer
- Solutions Engineer, AI
- Customer Engineer, AI

Signal keywords:

- customer deployment
- production AI systems
- enterprise customers
- implementation
- technical ownership
- solution architecture
- applied AI
- agentic workflows

### Technical Program Management Family

Strong title matches:

- Technical Program Manager
- Technical Program Manager, AI
- AI Program Manager
- Engineering Program Manager
- Product Operations, AI
- Platform Program Manager

Signal keywords:

- cross-functional execution
- roadmap coordination
- AI infrastructure
- model deployment
- launch management
- engineering operations
- stakeholder management

### AI Engineer Family

Strong title matches:

- AI Engineer
- Applied AI Engineer
- Machine Learning Engineer
- LLM Engineer
- Product Engineer, AI
- Software Engineer, AI

Signal keywords:

- LLMs
- agents
- RAG
- evaluation
- model integration
- applied machine learning
- Python
- production systems

## Scoring Draft

Each job should receive a score from 0 to 100.

Suggested scoring:

- Company priority: 0 to 25 points.
- Title match: 0 to 25 points.
- AI relevance: 0 to 20 points.
- Location or remote fit: 0 to 10 points.
- Seniority fit: 0 to 10 points.
- Freshness: 0 to 10 points.

Each score should include a short explanation.

Example:

```text
Score: 91
Reason:
- Company is in top priority list.
- Title is an exact Forward Deployed Engineer match.
- Description mentions enterprise AI deployment and production LLM systems.
- Posted within the last week.
```

## Learning Signal Draft

Each run should also summarize the market signals from the selected jobs.

Suggested learning categories:

- `technical_skills`: tools, frameworks, programming languages, infrastructure, AI concepts.
- `execution_skills`: launch management, cross-functional alignment, customer delivery.
- `domain_signals`: enterprise AI, developer tools, AI infrastructure, model evaluation.
- `portfolio_ideas`: projects or writeups the user could build to match the market.
- `interview_stories`: experience narratives the user should prepare.

The agent should count repeated signals across the shortlist and prioritize suggestions that appear in multiple competitive-company postings.

## On-Demand Workflow

1. Load target role families and company list.
2. Fetch open jobs from configured company sources.
3. Normalize all jobs into one internal format.
4. Deduplicate against previous runs.
5. Expand title matching by role family.
6. Score each job.
7. Extract skill and responsibility signals.
8. Keep the top 5 to 10 jobs above the minimum score.
9. Generate a run output with links, score reasons, and learning signals.
10. Save surfaced jobs and extracted signals to history.

## Suggested Architecture

```text
daily-job-search-agent/
  main.py
  config/
    profile.yaml
    companies.yaml
  src/
    job_agent/
      cli.py
      config.py
      models.py
      sources/
        greenhouse.py
        lever.py
        ashby.py
        manual.py
      matching.py
      scoring.py
      insights.py
      digest.py
      history.py
  data/
    surfaced_jobs.db
  docs/
    plan.md
```

Core modules:

- `config.py`: loads target roles, company priorities, location preferences, and minimum score.
- `sources/`: fetches jobs from supported career systems.
- `models.py`: defines normalized job records.
- `matching.py`: maps job titles and descriptions to role families.
- `scoring.py`: ranks jobs using transparent rules.
- `insights.py`: extracts repeated skills and suggests what to work on.
- `digest.py`: renders the shortlist for the current run.
- `history.py`: stores previously surfaced jobs to avoid repeats.
- `cli.py`: exposes commands like `run`, `companies`, and `sources`.

## Data Model Draft

### Company

- `name`
- `priority`
- `category`
- `careers_url`
- `source_type`
- `source_config`

### Job

- `id`
- `company`
- `title`
- `location`
- `department`
- `url`
- `description`
- `posted_at`
- `fetched_at`
- `source`

### Job Match

- `job_id`
- `role_family`
- `score`
- `score_reason`
- `matched_title_terms`
- `matched_description_terms`
- `is_new`

### Learning Signal

- `job_id`
- `signal_type`
- `signal`
- `evidence`
- `importance`

### Run Insight

- `run_date`
- `top_signals`
- `recommended_focus`
- `project_ideas`
- `interview_story_prompts`

## Build Phases

### Phase 1: Config and Digest Skeleton

Create the project structure, company config, role-family config, and a sample digest using mock job data.

Success criteria:

- Running the CLI prints a shortlist.
- The shortlist contains 5 to 10 mock jobs.
- Each job has a score and reason.
- The digest includes a short "what to work on" section.

### Phase 2: Company Source Integrations

Add real job fetching for one or two common career systems.

Start with:

- Greenhouse
- Lever
- Ashby

Success criteria:

- The agent can fetch real jobs from at least 5 target companies.
- Jobs are normalized into one shared model.
- Fetching can be repeated without duplicating history.

### Phase 3: Role Matching and Scoring

Implement title expansion, keyword matching, and transparent scoring.

Success criteria:

- Forward Deployed Engineer-style roles are found even when titles differ.
- Technical Program Manager roles are included when AI-related.
- Poor matches are filtered out.
- Every surfaced job includes a reason.

### Phase 4: Skill and Learning Insights

Extract repeated skill signals and turn them into practical recommendations.

Success criteria:

- The agent identifies repeated technical and execution skills across the shortlist.
- The digest suggests 1 to 3 concrete areas to work on.
- Recommendations are tied to evidence from the jobs, not generic advice.

### Phase 5: Run History

Store surfaced jobs locally.

Success criteria:

- Jobs shown in previous runs are not repeated unless still highly relevant and marked as previously seen.
- The user can review past shortlists.
- The user can review repeated skill signals over time.

### Phase 6: Personalization

Tune the profile around the user's real search.

Personalization inputs:

- preferred locations
- willingness to relocate
- remote preference
- role family priority
- company priority
- minimum score
- seniority level
- must-have and avoid keywords
- current skills and projects
- target skills to build

Success criteria:

- The output feels like the user's actual search, not a generic AI jobs feed.
- The learning suggestions reflect the user's current background and gaps.

### Phase 7: Extension for Other Users

After the personal version works, separate the user profile from the engine.

Possible additions:

- multiple profile files
- optional scheduler
- email digest
- Slack digest
- simple web dashboard
- user-owned company lists

## Open Decisions

- What exact companies should be in the first personal target list?
- Which role family matters most: Forward Deployed Engineer, Technical Program Management, or AI Engineer?
- What locations are acceptable?
- Should remote roles be preferred, neutral, or lower priority?
- What skills or projects does the user already have?
- Should the learning advice optimize for getting interviews, choosing projects, or deciding what to study?
- Should the first real source be Greenhouse, Lever, Ashby, or manual configured URLs?
- Should the first trigger be terminal-only, a local web button, or both?
- Should each run save a Markdown file?

## Recommended Next Step

Start with Phase 1:

1. Add config files for target companies and role families.
2. Add mock jobs that represent the kinds of roles the user wants.
3. Build scoring and digest output against the mock jobs.
4. Add simple skill-signal extraction from the mock descriptions.
5. Use that output to tune the product before adding real fetching.

This keeps the first implementation focused on the core judgment: selecting the right 5 to 10 jobs and learning what those jobs imply about the user's next best work.
