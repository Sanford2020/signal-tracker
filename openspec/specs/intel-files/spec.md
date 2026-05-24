# Intel Files Specification

## Purpose

Intel files are durable case files for tracked signals.

## Requirements

### Requirement: IntelFile As Primary Object

The system SHALL treat `IntelFile` as the primary product object for signal tracking.

#### Scenario: Create file from analysis

- GIVEN a raw item has structured analysis
- WHEN the user creates an intel file
- THEN the system creates an `IntelFile`
- AND attaches the raw item as first evidence
- AND creates a file creation event

### Requirement: First Seen Preservation

The system SHALL preserve first seen and last seen timestamps for each intel file.

#### Scenario: First evidence attached

- GIVEN an intel file is created from first evidence
- WHEN the file is stored
- THEN `first_seen_at` and `last_seen_at` are set

#### Scenario: Follow-up evidence attached

- GIVEN an intel file already exists
- WHEN newer evidence is attached
- THEN `last_seen_at` updates
- AND `first_seen_at` remains unchanged

### Requirement: Evidence Timeline

The system SHALL show evidence and derived events as a timeline.

#### Scenario: Evidence attached

- GIVEN a raw item is attached to an intel file
- WHEN the user opens the file detail page
- THEN the timeline shows the evidence attachment event
- AND includes the evidence type and rationale

### Requirement: Conservative Matching

The system SHOULD avoid automatically merging low-confidence evidence.

#### Scenario: Low-confidence match

- GIVEN a raw item partially resembles an existing intel file
- WHEN match confidence is below threshold
- THEN the system suggests the match instead of auto-attaching
