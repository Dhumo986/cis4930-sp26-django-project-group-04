# Automated Data Pipeline from Web APIs

**Course:** CIS 4930 — Introduction to Python (Spring 2026)  
**Group:** 04

## Group Members

| Name | FSU ID |
|---|---|
| Thomas Schmidt | tns23 |
| Imran Ahmed | ia24c |
| Dhruv Upadhyay | dtu24 |

---

## Project Title

**GitHub Repository Activity Tracker**

## Project Description

This project builds an automated Python data pipeline that collects repository metadata from the GitHub REST API for education-related Python projects. On each run, the pipeline fetches multiple pages of results, handles request errors safely, and appends structured records to a local CSV and SQLite data store for longitudinal analysis.

Real-world context: this can be used to monitor trends in open-source learning resources, repository popularity, and language usage over time.

---

## API Documentation

- GitHub REST API docs: https://docs.github.com/en/rest
- Search repositories endpoint: https://docs.github.com/en/rest/search/search#search-repositories

---

## Why This API

The GitHub API is relevant because it provides real, high-volume public data that changes over time. It supports meaningful pagination and query parameters, making it ideal for demonstrating robust HTTP requests, JSON parsing, and incremental data collection.

### API Constraints

- **Rate limits:** unauthenticated requests are limited to 10 requests/minute (GitHub rate limiting applies).
- **Pagination:** page-based (`page`, `per_page`) with finite result windows.
- **Auth:** optional token can increase limits; this project works without auth for classroom-scale runs.

---

## Data Pipeline Goals

1. Fetch repository data for a configurable query (default: `python education`).
2. Collect multiple pages per run (e.g., 3–5 pages, `per_page=30`).
3. Extract and store at least 5 meaningful fields per repository.
4. Handle failures (timeouts/request errors) without crashing silently.
5. Append new rows to a persistent dataset on repeated runs.

---

## Repository Structure

```text
P2WebAPI/
├── README.md
├── RUN_NOTES.md
├── ReportOfContribution.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── pipeline.py          # Main orchestration script
│   ├── api_client.py        # HTTP requests + pagination
│   └── storage.py           # CSV/SQLite write helpers
├── data/
│   └── processed/
│       ├── github_repos.csv
│       └── github_repos.db
└── logs/
    └── pipeline.log
```

---

## Minimum Technical Features

The implementation demonstrates:

- `requests.get(..., params=..., timeout=...)`
- JSON parsing via `response.json()`
- Safe field access with `.get()` defaults
- Pagination loop over multiple pages
- `try/except` with `raise_for_status()` and `RequestException`
- Conversion to `pandas.DataFrame`
- Persistent local storage with CSV and SQLite append

### Example Fields Collected

| Field | Description |
|---|---|
| `run_timestamp` | When the pipeline ran |
| `repo_id` | Unique GitHub repo ID |
| `full_name` | Owner/repo name |
| `html_url` | Link to repository |
| `description` | Repo description |
| `stargazers_count` | Number of stars |
| `forks_count` | Number of forks |
| `open_issues_count` | Number of open issues |
| `language` | Primary language |
| `created_at` | Repo creation date |
| `updated_at` | Last update date |

---

## Data Output

- `data/processed/github_repos.csv` — appended across runs
- `data/processed/github_repos.db` — SQLite database
  - Table name: `repo_snapshots`
  - Key columns: `run_timestamp`, `repo_id`, `full_name`, `stargazers_count`

---

## How to Run

From the `P2WebAPI` directory, install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline with defaults:

```bash
python3 src/pipeline.py
```

Run with custom CLI arguments (bonus feature):

```bash
python3 src/pipeline.py --query "python machine learning" --max-pages 5 --per-page 20
```

### CLI Arguments

| Argument | Default | Description |
|---|---|---|
| `--query` | `python education` | GitHub search query |
| `--max-pages` | `3` | Number of pages to fetch |
| `--per-page` | `30` | Results per page (max 100) |

### Example Console Output

```
2026-04-09 22:20:37,519 [INFO] Starting pipeline run...
2026-04-09 22:20:37,519 [INFO] Query: python education
2026-04-09 22:20:38,724 [INFO] fetched page 1 — 30 items
2026-04-09 22:20:39,887 [INFO] fetched page 2 — 30 items
2026-04-09 22:20:41,051 [INFO] fetched page 3 — 30 items
2026-04-09 22:20:41,053 [INFO] Collected 90 repositories.
2026-04-09 22:20:41,067 [INFO] Appended 90 rows to data/processed/github_repos.csv
2026-04-09 22:20:41,072 [INFO] Pipeline completed successfully.
```

---

## Error Handling Strategy

- Timeout handling with clear fallback message
- Request-level exception handling (`requests.exceptions.RequestException`)
- Status validation with `response.raise_for_status()`
- Graceful skip/continue behavior instead of silent failure
- Log persistence to `logs/pipeline.log`

---

## Automation Hook

Example cron schedule (every day at 8:00 AM):

```
0 8 * * * /usr/bin/python3 /path/to/P2WebAPI/src/pipeline.py
```

---

## Team Workflow

- Feature branches per member, PR-based merges into main
- Commit history reflects contributions from all members

| Role | Responsibility |
|---|---|
| API client lead | HTTP requests, pagination, error handling |
| Data/storage lead | DataFrame, CSV/SQLite append logic |
| Pipeline/orchestration lead | pipeline.py, repo setup, CLI args, documentation |

---

## Stretch Goals (Bonus)

- ✅ CLI arguments (`--query`, `--max-pages`, `--per-page`) — implemented in `pipeline.py`
- Add retry/backoff for temporary API failures
- Add a mini EDA notebook with 1–2 plots from generated CSV
