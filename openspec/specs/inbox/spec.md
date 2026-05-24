# Inbox Specification

## Purpose

Inbox is where raw candidate signals enter the system before they become intelligence files.

## Requirements

### Requirement: Manual Signal Submission

The system SHALL allow a user to submit a URL, pasted text, or both as a candidate signal.

#### Scenario: Submit pasted text

- GIVEN a user has pasted signal text
- WHEN the user submits the form
- THEN the system creates a `RawItem`
- AND the item appears in Inbox

#### Scenario: Submit URL only

- GIVEN a user has a URL but no pasted body text
- WHEN the user submits the URL
- THEN the system creates a `RawItem`
- AND stores the URL
- AND marks missing body text as acceptable for later extraction

#### Scenario: Duplicate submission

- GIVEN a raw item with the same content hash already exists
- WHEN the user submits duplicate content
- THEN the system SHALL not create an unbounded duplicate
- AND SHALL return the existing item or a clear duplicate response

### Requirement: Manual Source Fallback

The system SHALL associate manually submitted items with a `manual` source when no source is provided.

#### Scenario: No source provided

- GIVEN a user submits a signal without selecting a source
- WHEN the item is stored
- THEN it is associated with the default manual source

### Requirement: Inbox Review State

The system SHOULD show whether each item has been analyzed and whether it has become an intel file.

#### Scenario: Newly submitted item

- GIVEN a raw item was just submitted
- WHEN the user opens Inbox
- THEN the item shows analysis status as pending
