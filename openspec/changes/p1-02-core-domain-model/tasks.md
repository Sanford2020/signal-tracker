# Tasks: P1-02 Core Domain Model

## 1. Models

- [x] 1.1 Implement `Source`.
- [x] 1.2 Implement `RawItem`.
- [x] 1.3 Implement `SignalAnalysis`.
- [x] 1.4 Implement `IntelFile`.
- [x] 1.5 Implement `Evidence`.
- [x] 1.6 Implement `IntelEvent`.
- [x] 1.7 Implement `LifecycleSnapshot`.
- [x] 1.8 Implement `AlertEvent`.

## 2. Migrations

- [x] 2.1 Create migration for all MVP tables.
- [x] 2.2 Add indexes for source, timestamps, status, and hashes.
- [x] 2.3 Add uniqueness constraints for raw item hashes and evidence links.

## 3. Schemas

- [x] 3.1 Add create/read schemas for core models.
- [x] 3.2 Ensure JSON fields have safe defaults.
- [x] 3.3 Ensure score fields clamp or validate 0-10 where appropriate.

## 4. Tests

- [x] 4.1 Test creating a source and raw item.
- [x] 4.2 Test attaching signal analysis to raw item.
- [x] 4.3 Test creating intel file from raw item.
- [x] 4.4 Test evidence relationship.
- [x] 4.5 Test timeline event creation.
- [x] 4.6 Test lifecycle snapshot creation.
- [x] 4.7 Test alert event creation.
- [x] 4.8 Test full sample chain.

## 5. Docs Sync

- [x] 5.1 Update implementation notes if actual model names or constraints differ.
- [x] 5.2 Keep `docs/architecture/data-model.md` aligned.

## Done When

- Migration runs.
- Model tests pass.
- Full sample chain can be created.
- No lifecycle/scoring business logic is implemented prematurely.
