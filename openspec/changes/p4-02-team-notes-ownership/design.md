# Design

Add:

- `intel_files.owner_user_id`
- `intel_files.last_reviewed_at`
- `intel_files.review_note`
- `intel_file_comments`

APIs:

- `PATCH /api/v1/intel-files/{id}/collaboration`
- `GET /api/v1/intel-files/{id}/comments`
- `POST /api/v1/intel-files/{id}/comments`
