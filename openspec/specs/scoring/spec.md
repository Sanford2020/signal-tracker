# Scoring Specification

## Purpose

Scoring helps users compare signals while keeping judgment explainable.

## Requirements

### Requirement: Explainable Scores

The system SHALL calculate and store explainable scores for intel files.

Required scores:

- novelty
- heat
- credibility
- opportunity
- risk

#### Scenario: Score file

- GIVEN an intel file has evidence
- WHEN scoring runs
- THEN all required scores are produced
- AND each score is between 0 and 10
- AND the system stores a reason or input summary

### Requirement: Score Snapshots

The system SHALL preserve score history.

#### Scenario: Score changes

- GIVEN an intel file is rescored
- WHEN any score changes
- THEN the system creates a lifecycle snapshot or score snapshot
- AND the latest scores are visible on the intel file

### Requirement: Opportunity Threshold

The system SHOULD identify high-opportunity files.

#### Scenario: Opportunity crosses threshold

- GIVEN an intel file has opportunity score below threshold
- WHEN rescoring increases opportunity score above threshold
- THEN the system can emit an opportunity alert

### Requirement: No Black Box In MVP

The system MUST NOT rely only on opaque model judgment for v1 scoring.

#### Scenario: AI suggests a score

- GIVEN extraction includes AI score hints
- WHEN scoring runs
- THEN deterministic scoring logic may use hints as inputs
- BUT the final score calculation remains inspectable
