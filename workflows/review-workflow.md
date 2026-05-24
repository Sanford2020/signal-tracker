# Review Workflow

## Purpose

Review keeps AI-generated work aligned with product methodology and architecture decisions.

## When To Review

- Planning scaffold completion.
- Data model changes.
- API contract changes.
- Lifecycle state logic.
- Scoring logic.
- Evidence matching logic.
- Alert behavior.
- Pre-release.

## Review Output

Use this structure:

```text
Findings:
- P0/P1/P2 with file references and rationale.

Open Questions:
- Anything requiring owner or Master decision.

Validation:
- Commands run and result.

Verdict:
- APPROVE / REQUEST_CHANGES / BLOCK
```

## Severity

| Severity | Meaning |
| --- | --- |
| P0 | Must fix; breaks core behavior, data integrity, security, or lifecycle methodology |
| P1 | Important; should fix before milestone unless explicitly deferred |
| P2 | Improvement or follow-up |

## Planning Review Checklist

- Does the product avoid becoming a generic news reader?
- Is `IntelFile` clearly the main object?
- Are lifecycle states testable?
- Are score formulas explainable?
- Is evidence matching conservative?
- Are MVP and out-of-scope boundaries clear?
- Are P1 tasks small enough for AI execution?
