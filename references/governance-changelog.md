# Governance Rule Changes

## 2026-10-01 — One fixed role per context

Customer approved replacing same-context role switching with lifetime role binding. Each conversation or agent context keeps its initial role across turns, task completion, resume and compaction. Other roles receive scoped handoffs in independent contexts; sequential execution does not waive isolation. Worker reuse retains the original role. Bootstrap Governance hands off to separate project management and does not become the scheduler.

Updated `SKILL.md`, `SKILL.zh.md`, `README.md` and the bootstrap, project management, scheduler, role-card, built-in boundary and test-role references. Existing proposal confirmations, role authorization and file boundaries still apply. This is an instruction change; it does not add runtime enforcement to the task CLI.
