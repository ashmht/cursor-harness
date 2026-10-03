---
name: loop-devils-advocate
description: >-
  Devil's advocate loop for any draft — critic sub-agent attacks design or doc,
  logs objections with evidence in /tmp/redteam-{project}.md, builder fixes or
  accepts each, stops on stalemate or when no high-impact objections remain.
  Use to stress-test RFCs, tech specs, architecture proposals, rollout plans,
  or when the user says "red team this doc", "devil's advocate", or "argue
  against my design".
---

# Loop: Devil's Advocate

**Source:** [FF Loop #024](https://signals.forwardfuture.ai/loop-library/loops/devils-advocate-design-loop/)

## Copy the loop

```
Argue against [draft/design/doc] until it survives.

In each round:
1. Critic sub-agent writes the strongest case that the current approach is wrong.
2. Record every objection in /tmp/redteam-{projectname}.md with:
   - objection (one sentence)
   - evidence (repo path, metric, prior incident, constraint)
   - impact (high | medium | low)
   - status (open | resolved | accepted)
3. Builder must either:
   - fix the weakness and verify the result against stated criteria, OR
   - record why accepting it is reasonable under the project's stated criteria
4. Critic reviews the change or acceptance rationale; may reopen unsupported closures.

Repeat until:
- No new high-impact objection appears, AND
- Every logged objection is verified resolved or explicitly accepted with evidence

Stop conditions:
- Merely answering an objection in the log does NOT resolve it
- If same unresolved objections repeat 2 rounds without new evidence → report stalemate honestly; do not claim the design survived
```

## Verify / stop

**No high-impact objection remains open.**

Every logged objection is verified resolved or explicitly accepted with evidence, or the final report truthfully records a two-round stalemate.

## When to use

- Standalone pass on an existing draft (pair with loop-design-doc Phase 3)
- Before staff review or leadership alignment
- After agent-generated architecture (FC/IS, migration, FF ramp)

## Implementation notes

- Give critic and builder separate context where possible
- Do not let builder rewrite acceptance criteria mid-run to close a hard objection
- For docs: "resolved" means the doc text changed; "accepted" means explicit risk logged with owner

## Red-team log template

Initialize `/tmp/redteam-{projectname}.md` with this exact shape so every round
uses the same evidence and closure contract:

```markdown
# Red team: {projectname}

Stated criteria: {what good enough means}
Draft under review: {path or URL}

| ID | Objection | Evidence | Impact | Owner | Status | Resolution evidence |
|----|-----------|----------|--------|-------|--------|---------------------|
| RT-001 | One-sentence falsifiable objection | Repo path, metric, incident, or constraint | high | name | open | |

## Round log

### Round 1
- Critic: {new or reopened IDs}
- Builder: {changed files or explicit acceptance rationale}
- Verification: {commands, queries, or reviewer evidence}
```

Allowed statuses are `open`, `resolved`, and `accepted`. A status change to
`resolved` requires verification evidence. A status change to `accepted`
requires an owner and the stated criterion that makes the risk acceptable.

## Invocation

```
Run loop-devils-advocate on [path or paste draft].
Project name: [slug]
Stated criteria: [what "good enough" means for this design]
```

## Memory

`/tmp/redteam-{projectname}.md` — sole source of truth for objection state across rounds.
