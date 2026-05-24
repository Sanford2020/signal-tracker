# Design: P1-04 AI Extraction

## Flow

```text
RawItem + Source
  -> build ExtractionInput
  -> extractor (mock default)
  -> normalize/validate output
  -> persist SignalAnalysis
```

## Components

| Module | Role |
| --- | --- |
| `extraction/schemas.py` | Input/output pydantic models |
| `extraction/mock.py` | Deterministic mock extractor |
| `extraction/client.py` | Provider selection via env |
| `extraction/normalize.py` | Enum/score/array normalization |
| `extraction/service.py` | Orchestration + DB persist |
| `api/v1/extraction.py` | HTTP route |

## Config

- `AI_EXTRACTION_MODE=mock` (default)
- `AI_API_KEY` optional for future live mode

## Rules

- Extraction never creates IntelFile or lifecycle events.
- Invalid provider output: preserve raw_output, return readable error.
- Re-analyze returns existing analysis (idempotent).
