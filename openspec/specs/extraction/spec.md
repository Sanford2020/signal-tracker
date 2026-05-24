# Extraction Specification

## Purpose

Extraction turns raw candidate signals into structured signal analysis.

## Requirements

### Requirement: Structured Signal Analysis

The system SHALL analyze a `RawItem` into structured fields that can support tracking and file creation.

Required fields:

- summary
- signal type
- entities
- keywords
- claims
- suggested tracking queries
- novelty score
- relevance score
- credibility hint
- risk hint
- opportunity types
- rationale

#### Scenario: Analyze hiring signal

- GIVEN a raw item titled "Example AI hiring hardware supply chain lead"
- WHEN extraction runs
- THEN the analysis signal type is `hiring`
- AND the analysis includes an organization entity
- AND the analysis includes tracking keywords

### Requirement: Mock Mode

The system MUST support deterministic mock extraction without external AI credentials.

#### Scenario: No API key configured

- GIVEN no AI API key is configured
- WHEN extraction runs
- THEN the system returns deterministic mock analysis
- AND tests can run without network access

### Requirement: Invalid AI Output Handling

The system SHALL handle invalid model output safely.

#### Scenario: AI returns invalid JSON

- GIVEN the AI provider returns invalid JSON
- WHEN the system parses the result
- THEN the raw output is preserved
- AND a clear extraction error is returned or normalized according to backend rules

### Requirement: Extraction Does Not Mutate Lifecycle

Extraction SHALL NOT directly change an intel file lifecycle state.

#### Scenario: Analysis completes

- GIVEN extraction completes for a raw item
- WHEN `SignalAnalysis` is stored
- THEN no lifecycle transition is created by extraction alone
