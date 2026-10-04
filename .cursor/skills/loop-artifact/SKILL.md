---
name: loop-artifact
description: >-
  Composes an end-to-end artifact workflow by selecting one authoritative
  creation/refinement skill, one optional destination adapter, and the required
  evidence, review, compression, de-pollution, and verification gates. Use when
  the user says "artifact loop" or "full loop", or combines refinement with
  critical review and finalization, such as "critically review this and make it
  better." Do not use for a single wording, concision, formatting, or review pass.
---

# Loop: artifact

Produce the smallest artifact that achieves its intended outcome and survives
the appropriate review. This is a thin composer. Never repeat phases already
owned by a selected child skill.

## Bypass

Run a named specialist skill directly when it covers the request end to end.
Bypass this composer for:

- PR or diff review
- one-off wording, formatting, concision, or humanizer work
- documentation drift checks
- requests that ask only for critique and no revision

## Classify

Before acting, identify:

- mode: `create` or `refine`
- purpose: decision, explanation, analysis, presentation, or message
- canonical artifact and destination
- audience and desired decision, understanding, or action
- supplied anchor: example, template, source, plan, or rubric
- allowed mutation targets and material invariants to preserve
- evidence boundary, including which claims can become stale
- observable done criteria

Ask only when a missing answer would materially change the result.

For `refine`, update the canonical artifact in place unless the user requests a
new version. Preserve approved language, links, formulas, permissions, stable
structure, and other named invariants.

## Track only long runs

Create `/tmp/artifact-run-{slug}-{YYYYMMDD-HHMMSS}.md` only when work spans
multiple tools, review rounds, external artifacts, or a likely handoff. Record
pointers and receipts, never raw sensitive evidence:

```markdown
# Artifact run: {slug}
- Mode, canonical artifact, destination:
- Audience, outcome, done criteria:
- Anchor and preserved invariants:
- Evidence versions and freshness windows:
- Allowed mutations and ship authorization:
- Authoritative workflow:
- Destination adapter:
- Review verdict and child log:
- Verification receipts:
- Open risks:
- Status: drafting | reviewing | ready | blocked | shipped
```

## Delegate on two axes

Choose one authoritative workflow for the artifact's purpose:

- design decision, RFC, tech spec, ADR: `loop-design-doc`
- teaching or onboarding: `loop-concept-explainer`
- general engineering prose: `staff-eng-writing`
- high-stakes multi-source analysis: `orchestrator-experts-judge`, only when all
  of its parallelism, executable-check, downside, and runtime preconditions pass
- presentation: `wow-deck`
- persistent visual document without another content workflow: `loop-html-doc`
- Google Doc without another content workflow: settle content in Markdown,
  then use a user-installed Google Docs adapter; if none is installed, stop at
  the Markdown artifact
- domain-specific artifact: the closest domain skill

Then choose at most one destination adapter:

- Google Docs after content is settled: a user-installed adapter, with Markdown
  as the portable fallback
- persistent HTML after content is settled: `loop-html-doc`, using only its
  medium-specific structure, rendering, and inspection phases
- live Cursor analysis: Cursor's optional built-in Canvas skill; fall back to
  `loop-html-doc` when Canvas is unavailable
- Slack or email: `writing-compact.mdc`, `framing.mdc`, applicable voice rule
- Markdown or repository file: native file editing and validation

If one skill owns both purpose and destination, do not add an adapter. Follow
the child skill's stop criteria. Read that skill only when this router does not
already include its phase checklist. The child workflow owns its phases, review
method, iteration limit, and stop or escalation contract.

## Add only missing gates

Apply these only when the child workflow does not already cover them:

1. **Anchor.** Copy useful structure and density, never unrelated facts or wording.
2. **Reality.** Verify only volatile sources supporting artifact claims. Record
   source timestamp, commit, query window, or document version. Separate current
   state from historical evidence.
3. **Review.** Use the child's review. If none exists, use the lightest adequate
   method: Hostile Clarity for low stakes, native visual rubric for visual work,
   or `loop-devils-advocate` for a decision with meaningful downside. If a
   selected multi-agent review cannot run, use a bounded independent review and
   disclose the reduced coverage.
4. **Revision.** Fix material findings and recheck affected context. A
   high-impact risk may be accepted only by the user or a named human owner.
   OEJ failures remain `ESCALATE`.
5. **Compression.** For prose and information design, remove repetition,
   throat-clearing, and non-decision-changing detail. Preserve evidence and
   qualifiers that change meaning, ownership, confidence, safety, or scope.
6. **De-pollution.** Remove prompts, hidden instructions, review logs, internal
   scoring, model mechanics, and process scaffolding unless readers need them
   to use or trust the artifact.
7. **Finalization.** Run `humanizer` as the last prose transformation, then
   embed or write the result and perform read-only factual and native-medium
   verification. If verification changes prose, run detection again.

Without a child iteration contract, fix the highest-impact remaining weakness
and reassess. Stop if the same material objection survives two rounds without
new evidence. Do not continue into preference churn.

## Authorization

Naming an external artifact and asking to create or update it authorizes that
specific mutation. Asking for a draft does not authorize an external write.
Sending, posting, broadly publishing, changing sharing permissions, committing,
and pushing always require explicit authorization. Never infer authorization
from "polish", "finalize", or review completion.

## Finish

The artifact is ready when the authoritative child contract passes, native
checks pass, and no high-impact finding remains open. Distinguish `ready`,
`ready with human-accepted risk`, and `blocked`.

Return the artifact or path/link, substantive changes, verification receipts,
and unresolved risks. Keep run machinery outside the artifact.
