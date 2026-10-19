# Governance Rule Changes

## 2026-10-19 — Separate team formation, scheduling and acceptance

Introduced ANS Team Formation (ANS 团队组建, formerly ANS Governance) as the sole built-in owner of recruitment, role cards and mutation boundaries, preserving its existing identity and scope. The default project intake is now a separate scheduler; a separate project planner prepares new product/requirements proposals, followed by project management for technical architecture, implementation design/review, abstractions and shared code; tests produce real execution evidence; independent acceptance defines criteria and judges pass, rework or insufficient evidence. Project roles still require accepted cards and boundaries. Existing projects migrate explicitly.

The customer subsequently removed the group-lead object: only group classification remains, and the scheduler directly dispatches to and receives original feedback from each role. Current entry points and templates were updated; dated history remains intact and the old group-leadership URL is a compatibility note. The implemented task API is documented against the current source, including separate credentials, preflight and verdict requests, legacy read-only limits and current validity. The developer has delivered its own unit/timer results; independent QA is preparing its final source evidence and final acceptance remains pending. The later planner addition changes future proposal routing, not historical authorship or the CLI contract; this entry does not claim final completion.

## 2026-10-10 — Project engineering rules and role memos

Added shared guidance for one project-wide engineering rules document maintained by project management and private, concise work memos maintained by each role. Integrated the shared file and role memo into task reading, bootstrap sequencing, proposal review, testing, templates, and navigation. Project-specific rules require actual evidence and confirmation; examples do not automatically apply. Missing rules do not block bootstrap, and the new documentation paths do not grant mutation authority.

## 2026-10-07 — Substantive proposal review and customer brief

Added `proposal-review.md` and integrated it into the main skill, project-management responsibilities, owner role-card template, scheduler, meeting workflow and Chinese documentation. Management now evaluates requirement/architecture fit, reuse, cross-role impact and material alternatives before presenting a concise customer approval brief. Affected owners review in independent contexts, proposal revisions stay with their owner, and management recommendation remains separate from customer implementation authorization and runtime verification. Valid same-version approvals remain valid; material changes trigger review of the changed decision. No runtime CLI enforcement is added.

## 2026-10-01 — Requested cross-role meetings

Added `meeting.md` and discovery links in the main skill, Chinese guide, README and project-management responsibilities. Meetings use a fixed project-management host, independent read-only role participants, a default two-round limit, attributed minutes in the host's accepted documentation scope and explicit unresolved/customer-decision records. Consensus remains a proposal; it does not authorize implementation or broaden boundaries. This adds a skill workflow without a CLI command or runtime code changes.

## 2026-10-01 — One fixed role per context

Customer approved replacing same-context role switching with lifetime role binding. Each conversation or agent context keeps its initial role across turns, task completion, resume and compaction. Other roles receive scoped handoffs in independent contexts; sequential execution does not waive isolation. Worker reuse retains the original role. Bootstrap Governance hands off to separate project management and does not become the scheduler.

Updated `SKILL.md`, `SKILL.zh.md`, `README.md` and the bootstrap, project management, scheduler, role-card, built-in boundary and test-role references. Existing proposal confirmations, role authorization and file boundaries still apply. This is an instruction change; it does not add runtime enforcement to the task CLI.
