# Design: P1-06 Evidence Timeline

## Attach flow

```text
POST /api/v1/intel-files/{id}/evidence
  -> validate file + raw item
  -> reject duplicate intel_file_id + raw_item_id
  -> Evidence row
  -> IntelEvent (evidence_added)
  -> update evidence_count, source_count, last_seen_at
```

## Duplicate policy

Reject with readable conflict error when the same raw item is already attached to the file.

## Counter rules

- `evidence_count`: increment by 1 per new attachment.
- `source_count`: count distinct `RawItem.source_id` values linked via evidence.
- `last_seen_at`: max of current value and attached raw item seen time.

## Timeline

Detail API returns events sorted ascending by `event_time`.
