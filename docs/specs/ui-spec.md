# UI Spec

## Product Surface

The MVP UI should feel like an intelligence workbench, not a marketing site and not a generic news feed.

Primary navigation:

- Inbox
- Intel Files
- Briefing
- Alerts
- Sources

## Page: Inbox

Purpose:

Review newly submitted raw signals.

Required elements:

- Submission form for URL and text.
- List of submitted raw items.
- Analysis status.
- Action: Analyze.
- Action: Create Intel File.

States:

- Empty inbox.
- Submission loading.
- Analysis pending.
- Analysis complete.
- Error.

## Page: Intel Files

Purpose:

Browse tracked intelligence files.

Required elements:

- Filters: status, search, minimum opportunity.
- Sort: recently updated, opportunity, heat, first seen.
- File rows/cards showing:
  - title
  - status
  - first seen
  - last seen
  - evidence count
  - heat
  - credibility
  - opportunity
  - risk

## Page: Intel File Detail

Purpose:

Inspect one signal's full lifecycle.

Required sections:

- Header:
  - title
  - status
  - thesis
  - first seen / last seen
- Score strip:
  - novelty
  - heat
  - credibility
  - opportunity
  - risk
- Entities and keywords.
- Evidence timeline.
- Lifecycle history.
- Alerts related to file.
- Actions:
  - attach evidence
  - evaluate lifecycle
  - rescore

## Page: Briefing

Purpose:

Daily operating summary.

Required sections:

- New intel files.
- Updated intel files.
- Resurrected signals.
- High opportunity.
- Risk/noise candidates.

Each item should show:

- file title
- current status
- score summary
- reason it appears in briefing
- link to detail

## Page: Alerts

Purpose:

Show high-signal notifications.

Required elements:

- Alert list.
- Filters by type, severity, status.
- Alert message.
- Linked intel file.
- Acknowledge/dismiss action.

## Page: Sources

Purpose:

Manage source metadata.

MVP can be simple:

- List sources.
- Source type.
- Trust tier.
- Enabled flag.

## Design Rules

- Dense and scannable.
- Avoid landing-page hero treatment.
- Favor tables/lists with clear status indicators.
- Use badges for lifecycle status.
- Show score explanations near scores.
- Avoid hiding evidence behind too many clicks.

## MVP UX Success Criteria

- User can go from submitted item to intel file detail in under 3 steps.
- User can understand why a file is `resurrected`.
- User can see which evidence caused the latest state change.
- User can scan daily briefing in under 2 minutes.
