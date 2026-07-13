# On-Demand AI Job Search Agent

A personal on-demand agent for finding 5 to 10 high-quality AI-field jobs from highly competitive companies and turning them into signals about what to work on next.

Planning starts in [docs/plan.md](docs/plan.md).

## Run

```bash
uv run python main.py run
```

The command prints a Markdown report and saves the latest report to `reports/latest.md`.

Useful options:

```bash
uv run python main.py run --limit 5
uv run python main.py run --min-score 70
uv run python main.py run --report reports/my-run.md
uv run python main.py run --no-save-report
uv run python main.py run --no-save-history
```

## Test

```bash
uv run python -m unittest discover -s tests
```
