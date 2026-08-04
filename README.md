# MBU_Respekt_For_Graenser_Notify_When_Down

Fallback bot for **Respekt for grænser** reports in Aarhus Kommune, Børn og Unge.

When the journalizing robot can't create a case in GO, the report is left unhandled. This bot picks up those failed reports, mails the submitted PDF to the responsible team so it can be handled manually, and marks the form as `Manual` so it isn't picked up again.

## How it works

1. **Queue** (`--queue`) — finds the relevant reports in the journalizing database: those with status `Failed`, plus those still unresolved more than 30 minutes after submission. Each form is added to the ATS workqueue with `form_id` as its reference and the OS2Forms attachment URL as its data.
2. **Process** (`--process`) — downloads the attachment from OS2Forms, emails it as `respekt-for-graenser.pdf` to the recipient in the `rfg_email` constant, and sets the form's status to `Manual` in the journalizing database.
3. **Finalize** (`--finalize`) — currently a no-op.

Unexpected failures fail the work item and trigger an error mail; `BusinessError`s set the item to *pending user*.

## Requirements

- Python **3.13+** and [uv](https://docs.astral.sh/uv/)
- An ODBC driver for SQL Server (`pyodbc`)
- Access to the ATS automation server, the RPA database, and OS2Forms

## Setup

```sh
uv sync
```

Create a `.env` with:

| Variable | Purpose |
| --- | --- |
| `ATS_URL`, `ATS_TOKEN` | Automation server API — also used directly to page through existing queue items |
| `DBCONNECTIONSTRINGPROD` | ODBC connection string for the journalizing database |

Recipients, SMTP settings and the OS2Forms API key are **not** in `.env` — they're read from the RPA database at runtime: credential `os2_api`, and constants `rfg_email`, `E-mail`, `smtp_adm_server`, `smtp_port` (plus `Error Email`, `Email Friend`, `smtp_server` for error mails).

## Run

```sh
uv run main.py --queue      # find failed reports and populate the workqueue
uv run main.py --process    # mail them out and mark them Manual
uv run main.py --finalize   # finalize
```

The flags are independent and can be combined in a scheduled run, e.g. `--queue --process`.

## Layout

```
main.py                   Entry point — queue / process / finalize
helpers/                  Config and ATS API helpers
processes/                Queue population, item processing, error handling
processes/subprocesses/   Database, OS2Forms and email handlers
```

## Development

CI runs `ruff` (lint + format check) and verifies that the version in `pyproject.toml` is bumped on pull requests.

```sh
uv run ruff check .
uv run ruff format .
```
