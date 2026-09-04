<p align="center">
  <!-- PROJECT LOGO PLACEHOLDER: replace assets/logo-placeholder.svg with the final logo. -->
  <img src="assets/logo-placeholder.svg" width="680" alt="Lead Generation Automation project logo placeholder">
</p>

<h1 align="center">Lead Generation Automation</h1>

<p align="center">
  <a href="https://github.com/wtyck/lead-generation-automation/actions/workflows/ci.yml"><img alt="Build Status" src="https://github.com/wtyck/lead-generation-automation/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-22c55e"></a>
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-6366f1">
  <a href="https://github.com/wtyck/lead-generation-automation/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/wtyck/lead-generation-automation?style=flat"></a>
</p>

<p align="center"><strong>Collect, qualify, route, and follow up with leads through one observable API pipeline.</strong></p>

> **Open-source portfolio edition.** This clean-room implementation recreates the capabilities of an earlier personal automation project. It does not claim production parity, customer usage, or business results.

## 🎬 Demo

<!-- DEMO PLACEHOLDER: add docs/demo.gif or a high-quality pipeline screenshot here. -->

Run the API, import the included n8n sample, and submit a test lead. Interactive API docs are available at **http://127.0.0.1:8000/docs**.

## ✨ Features

- Accept webhook-style lead payloads with strict validation.
- Normalize email, phone, names, company, title, and source fields.
- Deduplicate contacts by normalized email.
- Score and segment leads with documented deterministic rules.
- Queue follow-up drafts only when contact consent is present.
- Record generic CRM outbound events for downstream adapters.
- Persist leads, follow-ups, and CRM events in SQLite.
- Expose read endpoints for pipeline observability.
- Include an inactive, credential-free n8n workflow sample.
- Test privacy, deduplication, scoring, and workflow behavior.

No conversion, revenue, throughput, or campaign-performance metrics are claimed.

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| API | Python 3.11+, FastAPI, Pydantic |
| Persistence | SQLite via `sqlite3` |
| Automation | n8n workflow JSON |
| Server | Uvicorn |
| Testing | pytest, HTTPX |
| Quality | GitHub Actions |

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or newer
- `pip`
- n8n is optional and only required to import the sample workflow

### Installation

```bash
git clone https://github.com/wtyck/lead-generation-automation.git
cd lead-generation-automation
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --env-file .env
```

### Usage

Submit a lead:

```bash
curl -i http://127.0.0.1:8000/webhooks/leads \
  -H 'Content-Type: application/json' \
  -d '{"email":"ada@example.com","first_name":"Ada","last_name":"Lovelace","phone":"+1 (555) 010-2020","company":"Analytical Engines","job_title":"Founder","source":"portfolio-demo","consent_to_contact":true}'
```

Inspect persisted work:

```bash
curl http://127.0.0.1:8000/leads
curl http://127.0.0.1:8000/follow-ups
curl http://127.0.0.1:8000/crm-events
```

Import `n8n/lead-intake-workflow.json` into n8n, replace the placeholder service URL, review authentication, and keep the workflow inactive until configured.

Run tests:

```bash
pytest -q
```

## 📚 API Reference / Configuration

### API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Return service status. |
| `POST` | `/webhooks/leads` | Validate, normalize, deduplicate, score, and store a lead. |
| `GET` | `/leads` | List stored leads. |
| `GET` | `/follow-ups` | List queued follow-up drafts. |
| `GET` | `/crm-events` | List outbound CRM integration events. |
| `GET` | `/docs` | Open interactive Swagger documentation. |

### Environment variables

| Property | Type | Description | Default |
|---|---|---|---|
| `DATABASE_PATH` | string | SQLite database file path. | `data/leads.db` |

### Qualification model

| Property | Type | Description | Default |
|---|---|---|---|
| Valid email | integer | Base score for every accepted lead. | `40` |
| Phone | integer | Score added when a phone is present. | `25` |
| Company | integer | Score added when a company is present. | `20` |
| Job title | integer | Score added when a title is present. | `10` |
| Contact consent | integer | Score added when consent is true. | `5` |

Segments: `high_intent` = 80–100, `qualified` = 60–79, `nurture` = 0–59.

## 🗺️ Roadmap

- [x] **Completed:** validated webhook intake and contact normalization
- [x] **Completed:** deduplication, scoring, segmentation, and SQLite persistence
- [x] **Completed:** consent-aware follow-up queue and generic CRM event log
- [x] **Completed:** safe n8n sample, automated tests, and CI
- [ ] **In progress:** signed webhook authentication example
- [ ] **Future:** pluggable CRM adapters and retry workers
- [ ] **Future:** configurable scoring policies and campaign templates
- [ ] **Future:** audit log, retention controls, and production observability

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/short-description`.
3. Add or update tests.
4. Run `pytest -q`.
5. Push the branch and open a focused pull request.

Never commit credentials or real personal data. Preserve consent-aware behavior and document any outbound integration.

## 📄 License

Released under the [MIT License](LICENSE). Copyright © 2026 wtyck.
