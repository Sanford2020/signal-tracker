# Proposal: P1-03 Manual Signal Submission

## Intent

Allow operators to submit candidate signals via URL and/or pasted text and review them in Inbox.

## Problem

The domain model exists but users cannot yet intake raw signals. The MVP lifecycle loop starts with manual submission.

## Scope

In scope:

- `POST /api/v1/inbox/submit`
- `GET /api/v1/inbox`
- Manual source fallback
- Content hash dedupe
- Inbox UI with submission form and list
- Analysis status display (pending only; no extraction logic)

Out of scope:

- AI extraction implementation
- Intel file creation
- Lifecycle, scoring, alerts, briefing
- URL fetching / crawlers

## Success

User submits URL or text, sees item in Inbox with pending analysis status.
