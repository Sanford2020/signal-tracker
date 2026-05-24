# Lifecycle Specification

## Purpose

Lifecycle behavior tracks how a signal changes over time.

## Requirements

### Requirement: Explicit Lifecycle States

The system SHALL use a fixed lifecycle state set.

Allowed states:

- new
- watching
- spreading
- validating
- cooling
- dormant
- resurrected
- verified
- debunked
- noise
- archived

#### Scenario: Invalid state

- GIVEN a lifecycle update contains an unsupported state
- WHEN the update is validated
- THEN the system rejects it

### Requirement: Lifecycle Evaluation Produces Explanation

The system SHALL explain every lifecycle evaluation.

#### Scenario: State changes

- GIVEN lifecycle evaluation changes status
- WHEN the transition is stored
- THEN an event is created
- AND a lifecycle snapshot is created
- AND the reason references evidence or score changes

### Requirement: Dormancy

The system SHALL mark files dormant after a configured inactivity period.

#### Scenario: No meaningful evidence for dormancy period

- GIVEN an intel file has no meaningful evidence after the dormancy threshold
- WHEN lifecycle evaluation runs
- THEN the file status becomes `dormant`

### Requirement: Resurrection

The system SHALL mark a dormant file as resurrected when meaningful new evidence appears.

#### Scenario: Dormant file receives meaningful evidence

- GIVEN an intel file is `dormant`
- WHEN meaningful new evidence is attached
- AND lifecycle evaluation runs
- THEN the file status becomes `resurrected`
- AND the transition reason explains why the evidence is meaningful

### Requirement: Verification And Debunking

The system SHALL support verified and debunked states.

#### Scenario: Claim confirmed by strong evidence

- GIVEN an intel file receives strong primary or corroborated evidence
- WHEN lifecycle evaluation runs
- THEN the file MAY become `verified`

#### Scenario: Claim disproven by strong evidence

- GIVEN an intel file receives strong contradictory evidence
- WHEN lifecycle evaluation runs
- THEN the file MAY become `debunked`
