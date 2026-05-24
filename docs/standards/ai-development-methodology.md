# AI Development Methodology

Signal Tracker should be developed with a planning-first AI workflow.

## Method

```text
OPC business clarity
  -> PRD user scenarios
  -> Taxonomy
  -> Lifecycle methodology
  -> Scoring methodology
  -> Architecture and data model
  -> ADRs
  -> TASKS
  -> scoped Skill execution
  -> tests
  -> review
```

## Why This Matters

AI tools are good at generating code, but they drift when product objects and boundaries are unclear.

The project must preserve these anchors:

- The primary object is `IntelFile`.
- The product loop is lifecycle tracking.
- Scoring must be explainable.
- Evidence attachment must be conservative.
- Alerts should be meaningful, not noisy.

## Planning Before Code

Before implementation begins, the project should have:

- `PROJECT_BRIEF.md`
- `docs/prd.md`
- `docs/architecture/system-architecture.md`
- `docs/architecture/data-model.md`
- `docs/methodology/lifecycle-methodology.md`
- `docs/methodology/scoring-methodology.md`
- `docs/methodology/source-taxonomy.md`
- `DECISIONS.md`
- `TASKS.md`
- `AGENTS.md`
- `SKILLS.md`

## Task Discipline

Each task must define:

- Goal.
- Owner Skill.
- Scope.
- Avoided files.
- Acceptance criteria.
- Validation command.

No implementation task should ask AI to "build the app" broadly.

## Review Gates

Use review gates at:

- End of planning.
- After database model implementation.
- After lifecycle engine implementation.
- After scoring engine implementation.
- Before UI polish.
- Before deployment.

## Suggested First AI Prompt

```text
You are the Master Agent for Signal Tracker.
Read AGENTS.md, SKILLS.md, TASKS.md, PROJECT_BRIEF.md, docs/prd.md,
docs/architecture/system-architecture.md, docs/architecture/data-model.md,
docs/methodology/lifecycle-methodology.md, and docs/methodology/scoring-methodology.md.

Your job is not to write code yet.
Review P0 planning for contradictions, missing decisions, and implementation risks.
Then propose the exact TASK-P1-01 implementation scope.
```
