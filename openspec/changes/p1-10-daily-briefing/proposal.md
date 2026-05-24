# Proposal: P1-10 Daily Briefing V1

## Intent

Generate a daily operating briefing from stored intel file state, lifecycle events, score changes, and evidence updates.

## Scope

In: briefing API, deterministic section selection, frontend briefing page, tests.
Out: full report builder, email/Slack delivery, scheduled generation, AI-written narrative.

## Success

The API returns a useful briefing for a configurable window, empty states are explicit, and the UI renders all required sections.
