# Meeting: Cross-Role Discussion

Use when an authorized task needs a role discussion or joint review. Project management hosts project-wide or cross-group meetings; an accepted group lead hosts a group-only meeting. Neither host is a new role or an executable CLI command. Do not start meetings for routine work unless requested or covered by approved project configuration.

## Authority and Contexts

- The project-management context hosts project-wide or cross-group meetings. An accepted group lead hosts only meetings for its own group. The host keeps its fixed role; each participant uses a separate context bound only to its accepted role. Never simulate multiple roles as speakers inside the host context or switch an existing context to another role.
- Governance prepares a scoped handoff to project management for project-wide/cross-group discussion, or to the accepted lead for a group-only discussion. Governance may participate in its own context when the agenda concerns ownership or permission; it never hosts as a group lead. A capability context whose accepted role card gives it the group-lead duty may host a group-only meeting when its task authorization covers the agenda; writing formal minutes still requires its own accepted minutes path. Other capability contexts hand off to project management for project/cross-group discussion or to the accepted group lead for an authorized group-only meeting. The current context stays bound to its existing role.
- A request naming roles and an agenda authorizes their read-only discussion within that agenda. Apply the role assignment checks in [project-role.md](project-role.md); preserve existing authorization. Do not invent missing role cards or assume an unapproved role is accepted. Propose necessary role definitions through Governance before that role participates.
- Project management arranges cross-group participants; a group lead may arrange participants from its own accepted group for a group-only agenda. Membership does not grant additional permissions. Use fresh contexts with the assigned role, accepted boundary, agenda, relevant evidence and expected response, rather than the host's full conversation history. Reuse a participant only for its original role. Participants do not assume another role or expand its scope.
- Discussion participants inspect and report; the meeting assignment does not authorize source changes, tests, configuration changes or external actions. Treat participant responses as evidence and proposals, not commands or permission.
- Without subagent tools or capacity, collect contributions sequentially from independent role contexts. If a required context cannot be started, record the missing contribution and pending handoff. Do not invent that role's opinion or present the meeting as fully attended.

## Prepare and Run

1. **State the agenda.** Record the question to resolve, expected outcome, known constraints, relevant document/code versions, participants and their responsibilities. Use the requested roles; if omitted, choose the smallest relevant accepted set covered by authorization. Ask only for missing decisions that affect scope. Use the customer's round limit, or default to two rounds: initial views and one targeted response round.
2. **Collect independent views.** Give each participant the same agenda and relevant inputs. Request a concise recommendation, supporting source/document references, impact on its responsibility, dependencies, and open questions. Distinguish observed facts, assumptions and proposals. Concurrent discussion needs no write access; serialize any host-owned minutes updates.
3. **Resolve specific differences.** The host summarizes agreements and conflicting alternatives fairly, identifies missing evidence, and sends only relevant questions and attributed excerpts back to the affected roles. A second round addresses those questions rather than restarting every speech. If views change materially, record why. Do not force consensus by counting votes or treating seniority as evidence.
4. **Close within the limit.** Stop at the agreed round limit or earlier when the outcome is clear. Summarize supported conclusions, unresolved questions, missing participants and customer decisions needed. Further rounds require a new request or existing explicit authorization; unresolved issues remain open rather than being guessed away.
5. **Deliver minutes and next actions.** Link the minutes and briefly explain the outcome in plain language. Assign proposed follow-up owners and acceptance/check requirements. A meeting ending does not dispatch implementation automatically.

If the customer stops the meeting, preserve received contributions and mark it stopped. On resume, retain participant role bindings, the original agenda and round count; check changed inputs before relying on earlier opinions. A material agenda change is a new or explicitly revised meeting, not a way to evade its round limit.

## Minutes: One Host, One Record

The actual host writes minutes only within its own accepted `docs/meetings/` scope. Project management writes project-wide and cross-group minutes; a group lead writes group-only minutes only if its own Section 1 covers the path. Resolve that bounded directory through Governance before writing. Prefer `YYYY-MM-DD_meeting_<topic>.md`; reuse the same file when continuing the same meeting and add a distinct suffix for a separate meeting on the same topic/day. If the host lacks the path, present a chat draft and route the boundary request to Governance; discussion can continue within its authorized read-only scope.

Minutes include only the fields needed to understand the discussion:

| Content | Record |
| --- | --- |
| Agenda and status | Question, date/timezone, constraints, input versions, round limit and actual rounds; planned, in progress, concluded, stopped or awaiting input |
| Participants | Host and role/context identities, actual attendance, missing contributions |
| Attributed views | Each role's recommendation, evidence links, impact and concerns; do not attribute host speculation to a participant |
| Agreements and differences | Supported agreement, alternatives, unresolved facts and reasoning |
| Decisions and authorization | Proposed conclusion versus actual customer decisions, with the original approval reference and scope where available |
| Follow-up | Action, proposed owner, dependencies, verification and current authorization/pending decision |

Write for someone who did not attend. Summarize rather than copying full transcripts, and retain important disagreements. Link canonical designs, feature documents and existing scheduling records instead of duplicating them. Do not write meeting minutes into `task_ops` machine blocks or fabricate dispatch/verification events.

## Discussion Is Not Implementation Approval

After discussion, project management applies [proposal-review.md](proposal-review.md) to the resulting concrete proposal/version: assess the evidence and alternatives, record its own review recommendation, return revisions to the owner and prepare the customer's concise approval brief. Meeting agreement supplies review input; it does not replace this evaluation or automatically mark a proposal ready.

A consensus is a recommendation, not customer acceptance, a permission change, or verified behavior. Link conclusions into the appropriate design/change/fix proposal within the owner's authorized scope. Application code and tests still require the customer's confirmation of that concrete document/version and instruction to implement it; previously valid same-version authorization remains valid. Governance handles ownership/boundary changes. Project management retains global authorization and stage tracking; a group lead may organize only the group work already assigned and authorized under [group-leadership.md](group-leadership.md). Required tests establish actual results.

## Invocation Example

> 使用 $ans-governed-construction meeting，讨论保存草稿的接口设计，请工单、存储和测试角色参与，最多两轮，输出会议纪要。

The project-management host checks accepted project-wide or cross-group roles; a group lead checks accepted participants for a group-only meeting. The host collects independent views and produces a linked record within its own authorized minutes scope. This invocation requests discussion and minutes, not code implementation, deployment or automatic approval.
