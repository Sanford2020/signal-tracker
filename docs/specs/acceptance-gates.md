# Acceptance Gates

## P0 Gate: Planning Ready

Required:

- Project brief exists.
- MVP PRD exists.
- Commercial PRD exists.
- Architecture exists.
- Data model exists.
- Lifecycle methodology exists.
- Scoring methodology exists.
- Source taxonomy exists.
- AI employee execution plan exists.
- P1 task cards exist.

Pass condition:

- Review verdict is `APPROVE` or `APPROVE_WITH_FOLLOWUPS`.

## P1A Gate: App Boots

Required:

- Backend health endpoint works.
- Frontend loads.
- Database migration tool exists.
- Worker starts.
- Test commands exist.

Pass condition:

- Local developer can run the stack from docs.

## P1B Gate: Domain Model

Required:

- MVP models exist.
- Migrations run.
- Tests create full sample domain chain.

Pass condition:

- `RawItem -> SignalAnalysis -> IntelFile -> Evidence -> IntelEvent -> LifecycleSnapshot` can be created in tests.

## P1C Gate: Manual Intake

Required:

- Manual submit works.
- Extraction mock works.
- Inbox UI works.

Pass condition:

- User can submit a signal and see structured analysis.

## P1D Gate: Intel File Loop

Required:

- Create intel file.
- Attach evidence.
- Detail page and timeline.

Pass condition:

- User can inspect a file's first seen, last seen, evidence, and timeline.

## P1E Gate: Differentiation

Required:

- Lifecycle engine.
- Scoring engine.
- Alerts.

Pass condition:

- Dormant signal can become resurrected and trigger alert with explanation.

## P1F Gate: MVP Complete

Required:

- Daily briefing.
- End-to-end acceptance test.
- Review.

Pass condition:

- Full lifecycle loop passes from submission to briefing.

## Commercial Gate

Not required for MVP.

Commercial planning is ready when:

- Team workspace requirements are clear.
- Source pack strategy is clear.
- Pricing hypothesis is documented.
- Report/export requirements are documented.
