# Alerts Specification

## Purpose

Alerts notify users about meaningful lifecycle or score changes.

## Requirements

### Requirement: Lifecycle Alerts

The system SHALL create alerts for important lifecycle transitions.

Required alert transitions:

- dormant to resurrected
- any state to verified
- any state to debunked

#### Scenario: Dormant file resurrects

- GIVEN an intel file is dormant
- WHEN it becomes resurrected
- THEN the system creates a `resurrected` alert

### Requirement: Score Threshold Alerts

The system SHOULD create alerts when important score thresholds are crossed.

#### Scenario: Opportunity threshold crossed

- GIVEN an intel file's opportunity score crosses the configured threshold
- WHEN scoring completes
- THEN the system creates an `opportunity_up` alert

### Requirement: Alert Review State

The system SHALL allow alerts to be acknowledged or dismissed.

#### Scenario: Acknowledge alert

- GIVEN an alert is pending
- WHEN the user acknowledges it
- THEN the alert status becomes `acknowledged`

#### Scenario: Dismiss alert

- GIVEN an alert is pending
- WHEN the user dismisses it
- THEN the alert status becomes `dismissed`

### Requirement: Avoid Alert Flooding

The system SHOULD avoid duplicate alerts for the same event.

#### Scenario: Re-run lifecycle evaluation

- GIVEN a resurrection alert already exists for a transition
- WHEN lifecycle evaluation is re-run without new meaningful change
- THEN no duplicate resurrection alert is created
