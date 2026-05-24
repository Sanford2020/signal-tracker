# Commercial PRD

## Product Vision

Signal Tracker Commercial turns the personal early-signal tracker into a repeatable intelligence operations platform for operators, analysts, investors, media teams, and small strategy teams.

The commercial product helps teams answer:

```text
What weak signals appeared early?
Which ones are gaining evidence?
Which ones revived after silence?
Which ones are becoming opportunities?
Which ones should we ignore?
```

## Commercial Positioning

Signal Tracker Commercial is an intelligence lifecycle workbench.

It is not a generic monitoring dashboard. It sells continuity, judgment, and team workflow around early signals.

## Target Segments

| Segment | Buyer | Core value | Will pay for |
| --- | --- | --- | --- |
| AI founders / operators | Founder, chief of staff | Early opportunity discovery | AI/product/source packs, daily briefings, alerts |
| Investors / analysts | Fund partner, analyst | Weak-signal tracking and evidence history | Watchlists, credibility changes, revived signals |
| Media / content teams | Editor, content lead | Early topic pipeline | Trending-before-mainstream briefs |
| Strategy / research teams | Strategy lead | Cross-source intelligence memory | Team files, notes, archive, exports |
| Agencies / consultants | Principal, research lead | Repeatable client intelligence workflows | Client workspaces, reports, white-label exports |

## Commercial Jobs To Be Done

1. Monitor a niche without manually checking many sources.
2. Preserve the first appearance and evidence history of a signal.
3. Know when a dormant signal becomes active again.
4. Compare whether a signal is noise, trend, opportunity, or risk.
5. Share a signal file with teammates or clients.
6. Produce daily/weekly intelligence reports.
7. Build a reusable source and topic asset library.

## Product Tiers

### Personal Pro

For one operator.

Features:

- Manual capture.
- Limited automated tracking.
- Personal watchlists.
- Daily briefing.
- Resurrection alerts.
- Export to Markdown/Notion.

### Team

For small teams.

Features:

- Shared intel files.
- Comments and owner assignment.
- Team watchlists.
- Role-based access.
- Alert routing.
- Weekly reports.
- Source packs.

### Commercial Intelligence

For research-heavy teams and agencies.

Features:

- Multiple workspaces.
- Client/project spaces.
- Advanced source packs.
- Custom scoring profiles.
- Report builder.
- API/webhook access.
- Audit log.
- Data retention controls.

## Commercial Feature Roadmap

### C1: Team Workspace

Goal: Move from personal tool to shared workflow.

Features:

- Auth and user accounts.
- Workspaces.
- Roles: admin, analyst, viewer.
- Shared intel files.
- Comments.
- Assign owner.
- Saved watchlists.

Success criteria:

- A team can jointly track one topic area.
- Every file has owner, status, and last review time.

### C2: Notification And Delivery Layer

Goal: Deliver value without requiring users to open the app constantly.

Features:

- Email digest.
- Feishu/Slack/Telegram/webhook delivery.
- Alert rules by lifecycle event.
- Alert quiet hours.
- Weekly executive briefing.

Success criteria:

- Users receive meaningful updates without alert fatigue.
- Resurrection and verification alerts have high perceived value.

### C3: Source Packs

Goal: Productize setup for specific niches.

Initial packs:

- AI/technology opportunities.
- Open-source AI projects.
- AI policy and regulation.
- Startup/funding signals.
- Cybersecurity incidents.
- China tech and policy.

Each source pack includes:

- Sources.
- Source trust tiers.
- Suggested watch themes.
- Prompt/scoring presets.
- Example briefing templates.

Success criteria:

- New user can start getting useful signals within 10 minutes.

### C4: Report Builder

Goal: Turn intelligence files into shareable outputs.

Features:

- Daily brief.
- Weekly trend review.
- Signal file export.
- Client-ready PDF/Markdown.
- Evidence appendix.
- Score and lifecycle explanation.

Success criteria:

- Analysts can produce a client or internal report without copying from multiple pages.

### C5: Advanced Tracking And Matching

Goal: Improve automation while keeping human trust.

Features:

- Similarity suggestions.
- Entity graph.
- Cross-file relationship detection.
- Merge and split workflow.
- Duplicate/noise clustering.
- Tracking query optimization.

Success criteria:

- System finds more relevant follow-up evidence with fewer false merges.

### C6: Commercial Operations

Goal: Make the product sellable and operable.

Features:

- Billing and plan limits.
- Usage quotas.
- Team audit logs.
- Admin dashboard.
- Backup and retention policy.
- Source compliance notes.
- AI cost guardrails.

Success criteria:

- Product can support paying customers without manual babysitting.

## Commercial Modules

| Module | Commercial value |
| --- | --- |
| Workspaces | Team/client separation |
| Source Packs | Faster onboarding and vertical specialization |
| Watchlists | User-specific priority themes |
| Lifecycle Alerts | High-signal notifications |
| Report Builder | Externalizable output |
| Team Review | Collaboration and accountability |
| Audit Trail | Trust and compliance |
| API/Webhooks | Integration with existing workflows |
| Cost Controls | Sustainable margins |

## Pricing Hypothesis

These are planning assumptions, not final pricing.

| Plan | Target | Possible price |
| --- | --- | --- |
| Personal Pro | Solo operator | $19-$49/month |
| Team | 3-10 users | $99-$299/month |
| Commercial Intelligence | teams/agencies | $499+/month |

Pricing should map to:

- Number of workspaces.
- Number of tracked intel files.
- Automated source checks.
- Alert channels.
- Report exports.
- Source packs.
- AI usage.

## Commercial MVP

The first sellable version should include:

- Personal Pro plus limited team features.
- One strong source pack: AI/technology opportunities.
- Daily and weekly briefings.
- Resurrection alerts.
- Markdown/PDF export.
- Basic auth.
- Usage limits.

Do not wait for advanced graph, vector search, or all source packs.

## Differentiation

Most tools provide:

```text
More feeds
More alerts
More dashboards
```

Signal Tracker sells:

```text
First appearance memory
Evidence history
Lifecycle state
Resurrection detection
Opportunity judgment
Reportable intelligence files
```

## Commercial Risks

| Risk | Mitigation |
| --- | --- |
| Users see it as another RSS reader | Center UI and messaging around intel files and lifecycle |
| Alert fatigue | Alert only on lifecycle and score changes |
| Source setup is hard | Sell source packs |
| AI costs hurt margin | Add quotas, caching, mock fallback, batch analysis |
| Trust is low | Explain scores and show evidence |
| False merges damage confidence | Conservative matching and review workflow |

## Commercial Acceptance Criteria

- A new user can select a source pack and start tracking within 10 minutes.
- A team can create, assign, comment on, and review intel files.
- A dormant signal can trigger a clear resurrection alert.
- A weekly report can be exported with evidence and score explanations.
- Admin can see usage, AI cost, and source health.
- Plan limits can be enforced.

## Open Commercial Questions

- Should the first paid wedge be Personal Pro or Team?
- Which notification channel matters most for first customers?
- Should source packs be bundled or sold separately?
- What is the minimum useful automation frequency?
- Should reports be positioned for internal strategy or client delivery first?
