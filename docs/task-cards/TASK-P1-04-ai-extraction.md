# TASK-P1-04: AI Extraction Prompt And Mock Fallback

## Owner Skill

Backend

## Goal

Analyze a `RawItem` into structured `SignalAnalysis`.

## Dependencies

- `TASK-P1-02`
- Can run after `TASK-P1-03` for live submission integration.

## Read

- `docs/methodology/source-taxonomy.md`
- `docs/methodology/scoring-methodology.md`
- `docs/specs/ai-extraction-contract.md`

## Owned Files

- AI client abstraction.
- Prompt templates.
- Extraction service.
- SignalAnalysis schema.
- Tests with mock mode.

## Avoid

- Do not require a real API key for tests.
- Do not let AI directly mutate lifecycle state.
- Do not create intel files automatically unless later task asks for it.

## Acceptance Criteria

- `RawItem` can be analyzed into `SignalAnalysis`.
- Mock mode produces deterministic structured output.
- Live AI mode can be configured later via env.
- Output includes summary, signal_type, entities, keywords, claims, suggested_tracking_queries, initial scores, and rationale.
- Invalid AI output is normalized or rejected safely.

## Validation

```powershell
cd backend
python -m pytest tests/test_extraction.py -q
```

## Output

```text
Changed:
Verified:
Risks:
Next:
```
