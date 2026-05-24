# Delta for Domain Model

## ADDED Requirements

### Requirement: Source Storage

The system SHALL store source metadata for raw items.

#### Scenario: Create source

- GIVEN source metadata
- WHEN the source is saved
- THEN it can be used by raw items

### Requirement: Raw Item Storage

The system SHALL store immutable raw captured items.

#### Scenario: Store raw item

- GIVEN a source and raw item content
- WHEN the item is saved
- THEN title, URL, content, hash, and capture time are stored

### Requirement: Signal Analysis Storage

The system SHALL store structured analysis for raw items.

#### Scenario: Attach analysis

- GIVEN a raw item
- WHEN structured analysis is saved
- THEN the analysis references that raw item

### Requirement: Intel File Storage

The system SHALL store intel files as primary signal case records.

#### Scenario: Create intel file record

- GIVEN file title, thesis, entities, keywords, and status
- WHEN the file is saved
- THEN the file can be queried by status and updated time

### Requirement: Evidence Linkage

The system SHALL link raw items to intel files as evidence.

#### Scenario: Attach evidence

- GIVEN an intel file and raw item
- WHEN evidence is created
- THEN the evidence stores type, confidence, attached_by, and rationale

### Requirement: Timeline Events

The system SHALL store timeline events for intel files.

#### Scenario: Create event

- GIVEN an intel file changes
- WHEN an event is stored
- THEN the event appears in file timeline order

### Requirement: Lifecycle Snapshots

The system SHALL store lifecycle state and score snapshots.

#### Scenario: Store snapshot

- GIVEN an intel file is evaluated
- WHEN a snapshot is stored
- THEN status and scores are preserved for history

### Requirement: Alert Events

The system SHALL store alert events linked to intel files.

#### Scenario: Store alert

- GIVEN an alert-worthy change
- WHEN an alert event is saved
- THEN it can be listed and later acknowledged or dismissed
