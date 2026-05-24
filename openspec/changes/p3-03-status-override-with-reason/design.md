# Design

`POST /api/v1/intel-files/{intel_file_id}/status`

The route requires a target status and reason. It creates a `LifecycleSnapshot` and, when status changes, an `IntelEvent` with previous/next status metadata.
