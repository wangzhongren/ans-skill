---
name: evidence-definition
description: What counts as evidence in ANS governed construction
metadata:
  type: feedback
---

**Evidence is the key code or key configuration that supports a conclusion.** Not logs, not coverage numbers, not "looks fine to me."

Examples:
- Fix claim → fix diff + the test that catches it
- Refactor safety claim → existing test coverage + interface contracts
- Section 1 completeness claim → file tree confirming no omission
- Dependency upgrade claim → changed import paths + passing downstream tests

See also: references/evidence.md in the skill directory, Governing Invariant #4

**Why:** Without a concrete definition, "evidence" is an abstract placeholder and Invariant #4 (evidence provenance) has no enforcement anchor. AI needs to know what to produce; human needs to know what to check.

**How to apply:** When any task asks for or claims "evidence," match it against this definition. If no key-code/config artifact is produced, the claim is unsupported.