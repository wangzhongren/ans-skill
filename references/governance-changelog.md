# Governance Rule Changes

## 2026-10-10 — Project engineering rules and role memos

Added shared guidance for one project-wide engineering rules document maintained by project management and private, concise work memos maintained by each role. Integrated the shared file and role memo into task reading, bootstrap sequencing, proposal review, testing, templates, and navigation. Project-specific rules require actual evidence and confirmation; examples do not automatically apply. Missing rules do not block bootstrap, and the new documentation paths do not grant mutation authority.

## 2026-10-07 — Substantive proposal review and customer brief

Added `proposal-review.md` and integrated it into the main skill, project-management responsibilities, owner role-card template, scheduler, meeting workflow and Chinese documentation. Management now evaluates requirement/architecture fit, reuse, cross-role impact and material alternatives before presenting a concise customer approval brief. Affected owners review in independent contexts, proposal revisions stay with their owner, and management recommendation remains separate from customer implementation authorization and runtime verification. Valid same-version approvals remain valid; material changes trigger review of the changed decision. No runtime CLI enforcement is added.

## 2026-10-01 — Requested cross-role meetings

Added `meeting.md` and discovery links in the main skill, Chinese guide, README and project-management responsibilities. Meetings use a fixed project-management host, independent read-only role participants, a default two-round limit, attributed minutes in the host's accepted documentation scope and explicit unresolved/customer-decision records. Consensus remains a proposal; it does not authorize implementation or broaden boundaries. This adds a skill workflow without a CLI command or runtime code changes.

## 2026-10-01 — One fixed role per context

Customer approved replacing same-context role switching with lifetime role binding. Each conversation or agent context keeps its initial role across turns, task completion, resume and compaction. Other roles receive scoped handoffs in independent contexts; sequential execution does not waive isolation. Worker reuse retains the original role. Bootstrap Governance hands off to separate project management and does not become the scheduler.

Updated `SKILL.md`, `SKILL.zh.md`, `README.md` and the bootstrap, project management, scheduler, role-card, built-in boundary and test-role references. Existing proposal confirmations, role authorization and file boundaries still apply. This is an instruction change; it does not add runtime enforcement to the task CLI.
