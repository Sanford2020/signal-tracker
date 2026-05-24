# Tasks: P1-03 Manual Signal Submission

## 1. OpenSpec

- [x] 1.1 Create change package.

## 2. Backend

- [x] 2.1 Add API envelope schemas.
- [x] 2.2 Add inbox request/response schemas.
- [x] 2.3 Implement inbox service (hash, manual source, dedupe).
- [x] 2.4 Add inbox routes.
- [x] 2.5 Enable CORS for local frontend.

## 3. Tests

- [x] 3.1 Submit text creates RawItem.
- [x] 3.2 Submit URL-only with null content.
- [x] 3.3 Manual source fallback.
- [x] 3.4 Duplicate hash returns existing item.
- [x] 3.5 List inbox with analysis status.

## 4. Frontend

- [x] 4.1 API client and types.
- [x] 4.2 Submission form.
- [x] 4.3 Inbox list with pending status.

## Done When

- `pytest tests/test_inbox.py` passes.
- Frontend type-check and build pass.
- No extraction, intel file, or lifecycle logic added.
