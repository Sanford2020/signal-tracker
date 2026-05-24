# Source And Signal Taxonomy

## Purpose

This taxonomy defines source categories and signal types used by Signal Tracker.

The system tracks signals, not just news.

## Source Categories

| Code | Name | Examples | Typical role |
| --- | --- | --- | --- |
| `social` | Social and UGC | X, Reddit, Hacker News, forums | Early weak signals and chatter |
| `github` | Code and open-source | GitHub releases, commits, issues | Technical evidence |
| `careers` | Hiring and org signals | Company career pages, LinkedIn jobs | Strategic direction clues |
| `product` | Product surfaces | App updates, changelogs, screenshots | Product movement |
| `official` | Official sources | Company blogs, regulators, filings | Verification |
| `news` | News and media | Reuters, TechCrunch, Bloomberg | Spread and mainstream pickup |
| `research` | Academic and technical research | arXiv, papers, patents | Technical trend evidence |
| `market` | Financial and market data | SEC, funding databases, pricing pages | Commercial evidence |
| `policy` | Regulation and government | Draft rules, agency posts | Policy signals |
| `aggregator` | Trend aggregators | Google Trends, Product Hunt, trend sites | Heat and discovery |
| `manual` | User-submitted | Notes, screenshots, pasted text | Human capture |

## Source Trust Tiers

| Tier | Meaning |
| --- | --- |
| 0 | Primary or highly reliable source |
| 1 | Reliable secondary source |
| 2 | Useful but unverified source |
| 3 | Unknown, noisy, or low-trust source |

Trust tier is not the same as usefulness. A Tier 2 social source can be excellent for first discovery, while a Tier 0 official source is better for verification.

## Signal Types

| Code | Meaning |
| --- | --- |
| `hiring` | Job posts, role changes, team expansion |
| `product` | Product launch, feature leak, screenshot, changelog |
| `github` | Repo creation, release, commit burst, issue activity |
| `funding` | Financing, acquisition, investor movement |
| `policy` | Regulation, draft policy, legal change |
| `research` | Paper, benchmark, patent, technical finding |
| `market` | Pricing, demand, search trend, customer behavior |
| `rumor` | Unverified claim or leak |
| `incident` | Outage, breach, crisis, conflict |
| `community` | Social discussion, meme, recurring user pain |
| `partnership` | Business relationship or ecosystem signal |
| `other` | Anything not yet classified |

## Evidence Types

| Code | Meaning |
| --- | --- |
| `first_seen` | Earliest known signal |
| `follow_up` | New related mention |
| `corroboration` | Supports the core claim |
| `contradiction` | Weakens or disputes the claim |
| `primary` | Direct evidence from an official or source of truth |
| `mainstream_pickup` | Larger outlet/community begins spreading it |
| `duplicate` | Repeated mention without new value |
| `noise` | Low-quality or irrelevant |

## Recommended AI Extraction Output

```json
{
  "summary": "A concise factual summary.",
  "signal_type": "hiring",
  "entities": [
    {"name": "Example AI", "type": "org"},
    {"name": "AI hardware", "type": "topic"}
  ],
  "keywords": ["Example AI hardware", "AI device hiring"],
  "claims": [
    "Example AI appears to be hiring for hardware supply chain roles."
  ],
  "novelty_score": 7.5,
  "relevance_score": 8.0,
  "credibility_hint": 6.0,
  "suggested_tracking_queries": [
    "Example AI hardware hiring",
    "Example AI supply chain role"
  ]
}
```
