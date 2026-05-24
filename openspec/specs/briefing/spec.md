# Briefing Specification

## Purpose

Briefing summarizes meaningful signal changes for daily operation.

## Requirements

### Requirement: Daily Briefing Sections

The system SHALL generate a daily briefing with structured sections.

Required sections:

- new intel files
- updated intel files
- resurrected signals
- high opportunity files
- risk or noise candidates

#### Scenario: Generate empty briefing

- GIVEN no meaningful changes occurred in the selected time window
- WHEN the user opens the briefing
- THEN the system returns an empty briefing with a clear explanation

#### Scenario: Include resurrected file

- GIVEN an intel file became resurrected in the selected time window
- WHEN the briefing is generated
- THEN the file appears in the resurrected signals section

### Requirement: Briefing Item Explanation

The system SHALL explain why each item appears in the briefing.

#### Scenario: High opportunity item

- GIVEN an intel file has high opportunity score
- WHEN it appears in the briefing
- THEN the item includes the score and reason

### Requirement: Configurable Time Window

The system SHOULD support configurable briefing windows.

#### Scenario: 48 hour briefing

- GIVEN the user requests a 48 hour briefing
- WHEN the briefing is generated
- THEN it includes qualifying changes from the last 48 hours
