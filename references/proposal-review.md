# Project Management Proposal Review

Use before presenting an application-code or test proposal for customer implementation approval. Project management is responsible for judging the proposal's quality and system impact, not merely forwarding it. This is a duty of the existing accepted project management role, not another role or an automatic permission to implement.

## Submit and Review

1. **Owner prepares the proposal.** The owning role investigates the actual entry, behavior and dependencies, then writes the relevant feature draft or dated design/change/fix proposal in its authorized scope. Identify the intended result, affected files and public contracts, dependencies, necessary versus optional changes, alternatives worth considering and validation. Send the document link and version to project management before requesting implementation approval from the customer. Read-only investigation, review and proposal refinement can proceed without code implementation approval, within existing assignment authorization.
2. **Project management evaluates the evidence.** Read the actual proposal and relevant code, contracts, architecture and feature documents. Check requirement fit, five-layer rules, role ownership, reusable capabilities and unnecessary duplication. Trace relevant callers and consumers to assess changes to interfaces, shared data, errors, lifecycle and dependent tests. Compare realistic alternatives when they would improve simplicity, maintenance, cost or behavior; explain the tradeoff rather than inventing speculative options. A short contained change needs a proportionate review, not a mandatory meeting or new design document.
3. **Affected owners assess impact.** When another role's interface, data, behavior, implementation or verification is affected, obtain its scoped read-only assessment in an independent context bound to that role. Request concrete compatibility concerns, required caller/consumer changes, prerequisites and verification. Follow existing assignment authorization; reading a role card does not authorize dispatch. Use a requested or otherwise authorized [meeting](meeting.md) for unresolved disagreements, not for every review. An unavailable required assessment remains an explicit gap; do not claim no impact or invent that role's agreement.
4. **Conclude and return revisions.** Record one recommendation: `recommend approval`, `needs revision`, or `not ready`. Support it with findings, affected roles and their responses, material alternatives and unresolved questions. The original owner revises its proposal; management does not edit that owner's files or switch roles. Project management may revise its own integration design within its scope. Recheck material revisions against the affected evidence and update the conclusion for the actual version.
5. **Present the approval brief.** Once the proposal is ready to recommend, give the customer the short decision brief below with a link to the full proposal and review. If not ready, explain the gap or decision needed; do not present it as a routine ready-to-implement approval. The customer may explicitly decide a documented tradeoff or unresolved risk; retain that decision and its conditions rather than silently relabeling missing evidence as verified.

Management's own shared-code or integration proposal receives the same substantive assessment. Obtain affected owners' feedback where needed and disclose management's authorship; do not invent an independent reviewer or a second project-management role. Scope/ownership changes still go to Governance in its own context.

## Record and Brief

Write review findings in project management's existing authorized design/change/fix scope, linking the owner's canonical proposal/version rather than copying it. A bounded new review directory is not required. If no review record path is authorized, provide a chat review and route any necessary scope update to Governance; do not expand permission yourself. Keep customer authorization, management recommendation and runtime verification as separate facts. A meeting's minutes may supply review evidence but consensus alone is not a completed review.

The customer-facing brief should be understandable without opening all technical records:

- **Problem and outcome:** What the user needs and what changes on success.
- **Recommendation and reason:** The reviewed approach and why it fits better than any material alternative.
- **Impact and cost:** Affected roles, required coordination, meaningful risks and verification; evidence supporting a contained change if no other role is affected.
- **Open decisions and options:** Unresolved disagreement, missing assessments and optional item IDs with benefits, costs and pending selection. Do not hide these to shorten the summary.
- **Approval requested:** Exact proposal link/version, implementation scope and option selection; distinguish approval to implement from a request to choose an alternative or resolve uncertainty.

Use a short paragraph or compact bullets, scaling detail to the decision. Summarize the reasoning, not just role names and technical headings. The brief points to the full proposal and review; it is not a second independently maintained specification.

## Implementation Gate and Changes

Before implementation dispatch, project management checks that the reviewed proposal version matches the customer's confirmation and instruction to implement, accepted role boundaries and actual task scope. Its recommendation does not grant authority or prove working behavior. Reuse valid same-version, same-scope customer authorization; do not request duplicate approval because review or a later turn occurs.

Material changes to behavior, contracts, role impact, implementation scope or optional selection require a revised review and presentation of the affected decision before implementing it. An unchanged proposal does not require repeated review for every stage; recheck only when new evidence undermines the conclusion. Role isolation applies throughout: standalone owners hand off to a separate authorized management context for review, then receive the result in their original context. If no management context can be started, preserve the draft, report the missing review and continue authorized investigation/document preparation instead of self-reviewing as another role.
