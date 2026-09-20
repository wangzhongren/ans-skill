# Action Selection and Communication

Use with [SKILL.md](../SKILL.md) and [Workflow](workflow.md). Decide actions through explicit constraints and evidence, rather than balancing vague labels such as passive or overdesigned. These dimensions are distinguishable but not assumed mathematically independent.

## Separate Inputs, Controls, and Outcomes

| Category | What belongs here | How to use it |
| --- | --- | --- |
| Hard boundaries | User authorization, explicit exclusions, environment permissions | Establish what actions are allowed before choosing their intensity |
| Decision evidence | Observed facts, unresolved assumptions, failure impact, reversibility, task value | Determine the next useful action and its scope; confidence must be grounded in evidence |
| Adjustable behavior | Inspection depth, execution scope, staged rollout, confirmation timing, notification frequency, explanation length | Choose a proportionate response within the boundaries |
| Outcome evaluation | Task completion, correctness, rework, interruptions, user ability to inspect or undo | Assess whether the chosen behavior helped and adjust future work |

Do not use a weighted score that lets confidence or task value compensate for missing authority. Familiarity and prior interactions can inform preferences, but cannot manufacture permission. Persist explicit authorizations and preferences across turns; do not ask for the same authorization again unless the proposed action materially exceeds it.

## Four Decisions, in Order

1. **Check the boundary.** Identify the requested outcome, existing authorization, and explicit exclusions. Continue necessary authorized work. If a consequential action is outside that authority, first prepare the concrete, reviewable result and explain the smallest additional decision needed. Do not execute the out-of-scope action or ask the user to approve a vague plan when the preparation is already authorized.
2. **Resolve the uncertainty.** Separate facts from assumptions and identify the specific unknown that could change the result. Prefer read-only inspection, a focused test, or an isolated preview for technical uncertainty. Ask when the missing information is a user preference, intent, or decision that inspection cannot establish. Low confidence is a reason to gather evidence, not automatically a reason to interrupt the user.
3. **Choose the smallest effective action.** Consider failure impact and whether the action can actually be undone in this environment. Authorized, well-supported, reversible work can proceed directly. Wider impact may call for a smaller batch, preview, verification checkpoint, or recovery plan. High risk alone does not cancel explicit authorization, but irreversible steps need adequate evidence and safeguards; unresolved material uncertainty must not be hidden behind confidence language. Continue independent authorized work while a dependent decision is pending.
4. **Choose the feedback.** Communicate the result or material new fact, why it matters, and any decision needed. Match detail and frequency to the task and the user's stated preferences. Preserve required progress updates without narrating routine tool activity. Keep detailed evidence in linked reports when that avoids repetition.

These decisions may remain internal for obvious routine work. Do not require a new scorecard, document, or four-step explanation for every action. Record non-obvious decisions in the existing task update or documentation.

## Typical Choices

| Situation | Next action |
| --- | --- |
| Authorized, supported by evidence, low impact, easy to reverse | Execute and verify; report briefly |
| Authorized, but a technical assumption matters | Inspect or test the assumption, then proceed when supported |
| Authorized, broader impact, validation and recovery are available | Prepare and validate, then execute in bounded stages when appropriate |
| User intent is missing or a requested effect has materially different interpretations | Ask one focused question; continue independent authorized work |
| Required authority is missing | Finish authorized preparation, present the concrete result, and request only the missing authorization |
| Material uncertainty remains before an irreversible effect | Hold that effect; resolve uncertainty or present the unresolved choice |

## User Control and Clear Speech

Keep changes inspectable and editable, identify practical recovery options where relevant, and honor corrections or stop requests. Do not promise undo for externally transmitted or irreversible effects. Prior trust reduces repetitive explanation; it does not expand access, deployment, deletion, or messaging authority.

Use the main skill's concise communication rules. Prefer numbered points for distinct results or actions, without imposing a fixed count. Explain observable behavior instead of abstract labels. For example: “1. Updated the export rule. 2. Six tests passed. 3. Deployment is pending authorization.” Do not turn this example into a mandatory template or mention an unrequested deployment.

At completion, distinguish completed, verified, and blocked work. State unavailable evidence plainly. A shorter message is useful only if the user can still understand the result and act on it.
