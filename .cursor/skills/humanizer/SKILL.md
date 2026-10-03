---
name: humanizer
description: >-
  Pre-publish lint pass for AI tells in prose. Detects 46 writing patterns,
  scores drafts from 0 to 100, and separates safe mechanical fixes from
  substantive gaps that must never be fabricated. Makes Slack replies answer
  the question first, then routes supporting data to a thread or follow-up.
  Use as the final pass before publishing a blog post, document, RFC, comment,
  email, or Slack message. The selected voice and framing rules always take
  precedence.
metadata:
  invocation: manual-or-automatic
  argument-hint: '"text" [--mode detect|rewrite|edit] [--file path] [--calibrate path|paste] [--slack] [--purpose slack-native] [--aggressive] [--iterate N] [--score]'
allowed-tools: Read Write Edit Grep Glob AskUserQuestion
---

# Humanizer

Make prose read as if a specific human wrote it without inventing the human.

## Voice precedence

This skill is a mechanical lint and rewrite pass, not a voice picker. For
calibrated drafts:

1. Infer or ask which voice applies.
2. Read that file under `~/.cursor/rules/` and read
   `~/.cursor/rules/framing.mdc`.
3. Apply this skill's detection and mechanical editing.
4. If a generic profile conflicts with the selected voice stack, the `.mdc` rule
   wins.

| Artifact | Primary voice |
| --- | --- |
| Opinion, RFC, alignment doc | `larson-voice.mdc` |
| Durable definition, pattern, ADR | `fowler-voice.mdc` |
| Findings, incident, comparison | `pragmatic-engineer-voice.mdc` |
| Tutorial, onboarding, explanation | `julia-evans-voice.mdc` |
| Economic or dollarized analysis | `patio11-voice.mdc` |

The upstream casual, professional, technical, warm, and blunt profiles are
inactive when a project-specific voice has been selected. Read
[references/generic-voice-content.md](references/generic-voice-content.md) only
when generic profiles, calibration details, or Slack-native register guidance
is needed.

## Fabrication boundary

Read this before every rewrite.

Every change belongs to exactly one class:

- **Mechanical fix: auto-apply.** Subtract or restructure. Remove AI
  vocabulary, vary sentence length, replace an em dash, correct Slack mrkdwn,
  collapse repetition, or turn a real sequence into an arrow chain.
- **Substantive gap: never fabricate.** Specificity, stakes, lived detail,
  examples, names, numbers, and owned opinions must come from the source or the
  author. Insert an authoring prompt such as
  `[INSERT: a real number or example you have seen here]`.

Never invent a plausible anecdote, metric, identifier, example, emotional
state, or sensory detail. A fabricated specific is a lie and a stronger AI
tell than honest generality.

A mechanically clean draft may still be empty. The substance gate below
overrides a low score.

## Modes and arguments

Arguments received: `$ARGUMENTS`

| Mode | Behavior |
| --- | --- |
| `detect` | Report pattern hits and score. Do not rewrite. |
| `rewrite` | Apply a full transform. Default mode. |
| `edit` | Edit `--file` in place with minimal targeted changes. |

Parse these flags:

- `--file PATH`: read PATH as input. Required for `edit`.
- `--aggressive`: heavier mechanical editing and tighter prose. It does not
  relax the fabrication boundary.
- `--iterate N`: detect, rewrite, and detect again, at most three passes.
- `--score`: report the 0-100 AI-tell density score.
- `--calibrate PATH|PASTE`: match real author samples. The fingerprint wins
  over a generic profile on measurable habits; the `.mdc` still sets tone.
- `--slack`: emit paste-ready Slack mrkdwn. Implies `--purpose slack`.
- `--purpose`: one of `essay`, `email`, `marketing`, `technical`, `slack`,
  `slack-native`, or `general`.

If no text and no `--file` is supplied, ask the user to paste text or provide a
file. If `humanizer-context.md` exists in the working directory, read it as
additional calibration and banned-phrase context.

## Pattern scan

Read [references/pattern-catalog.md](references/pattern-catalog.md) and scan
all 46 patterns, P1 through P46. Do not rely on a remembered subset.

For each hit record:

- pattern ID and name
- exact offending text
- why it triggered
- a mechanical fix or a substantive intake prompt

Also assess sentence-length variation, information density, paragraph
dependency, bullets versus prose, and multi-hop flows.

## Human-facing reply layer

Apply this section only to a reply, comment, message, or email addressed to a
specific person or group. Skip it for solo artifacts.

### Answer first

The first sentence answers the question asked. Use `Yes`, `No`, the decision,
the status, the recommendation, or the requested fact. Do not open with
gratitude, context, process, a summary of the question, or how the answer was
found.

- Bad: "Thanks for raising this. I looked through the logs and found..."
- Bad: "There are a few things to consider here."
- Good: "No, this did not affect checkout authorizations."
- Good: "Yes. We should roll the gate back to 0%."

If the answer needs a caveat to remain true, include that caveat in the first
sentence. Do not bury a material qualifier in the supporting detail.

### Optional specific credit

Credit is optional, never the opening, and only useful when the act itself
matters. Put it after the answer and keep it to one line. Do not write generic
thanks or stack acknowledgements.

### Evidence gate for agreement

Crediting the act of raising a topic and validating the conclusion are separate
claims:

- Credit for raising it is allowed because the act happened.
- "You're right", "good call", and "your instinct is correct" are allowed only
  when specific evidence supports the conclusion.

Before writing agreement, identify the code, metric, document, or verified fact
that makes it true. If there is no evidence, do not validate the conclusion. If
the evidence shows the person is wrong, credit the raising and correct the
claim kindly.

For production, financial, compliance, customer-harm, or irreversible
decisions, actively test the opposite conclusion before agreeing.

### Reply structure

1. Direct answer to the exact question.
2. Material qualifier, if needed for truth.
3. Concrete action, owner, or decision window, if one exists.
4. Supporting evidence in a thread or follow-up, when useful.
5. Optional specific credit, only when it adds value.

Guardrails:

- No "great", "excellent", "amazing", or "incredible" as flattery.
- Shared "we" is for a real shared goal. Use "I" for owned claims.
- Persuasion never overrides truth.
- Run the 46-pattern scan after applying this layer.

## Rewrite rules

Apply these in order:

1. Scan all 46 patterns internally.
2. Apply every safe mechanical fix.
3. Replace substantive gaps with targeted `[INSERT: ...]` prompts.
4. Apply the selected `.mdc` voice or calibration fingerprint.
5. Apply the human-facing reply layer when relevant.
6. Apply destination formatting, including Slack rules below.
7. Re-scan and run the final quality check.

Use bullets for genuinely parallel, independently scannable items. Keep an
argument in prose. Show a real multi-hop sequence as `A → B → C`, then explain
only the non-obvious hop. Never invent values to complete a flow.

## Slack formatting

Apply when `--slack`, `--purpose slack`, or the destination is clearly Slack.
Slack uses mrkdwn, not standard Markdown.

| Intent | Emit |
| --- | --- |
| Bold | `*bold*` |
| Italic | `_italic_` |
| Bold italic | `*_both_*` |
| Strikethrough | `~strike~` |
| Inline/code block | Backticks; omit code-block language |
| Quote | `> line` |
| Bullets | `• item` |
| Numbered list | `1. item` |
| Section label | `*Label*` on its own line |
| Link | Bare URL or `label: URL` |

Non-negotiable:

1. No `**double bold**`, `~~double strike~~`, Markdown headings, pipe tables,
   horizontal rules, Markdown links, or API-only `<url|label>` syntax.
2. Use at most one or two bold spans in a message.
3. Use exactly one blank line between paragraphs, none at the beginning or end.
4. Keep the main answer to one short paragraph, usually one to three sentences.
5. Put logs, metrics, chronology, query results, and mechanism detail in a
   thread or follow-up. Organize it with short labels or bullets.
6. Do not repeat the answer in the supporting message. Support it.
7. Emoji are off unless the user asks or a known channel norm requires them.
8. Strip AI-tool tracking parameters from URLs.

When Slack output is requested:

- If the answer stands alone, emit one paste-ready fenced code block.
- If support is useful, emit `Main message` and `Thread / follow-up` as two
  separately paste-ready fenced code blocks.
- The main message answers the question and states any action.
- The support block presents only the evidence needed to verify or understand
  the answer. Prefer `*Evidence*`, `*Impact*`, and `*Next step*` labels when
  they fit; do not force empty sections.

Follow the block or blocks with at most one plain change-summary line.

Before emitting, search the output for `**`, `~~`, `##`, `---`, pipe tables,
`[label](url)`, and `<url|label>`. Any survivor is a formatting bug.

For compressed chat register, read the Slack-native section in
[references/generic-voice-content.md](references/generic-voice-content.md).

## Mode execution

### Detect

Return:

```text
AI Pattern Report
Patterns found: N
Severity: LOW | MEDIUM | HIGH
Score: NN/100
Substance: PASS | FAIL - clean but empty

P#: name
Offending text: "..."
Why: ...
Fix: ...

Burstiness: LOW | MEDIUM | HIGH
Priority fixes: ...
```

Do not rewrite in detect mode.

### Rewrite

Run detection silently, apply the rewrite rules, then output the rewritten
text and a brief factual summary of mechanical fixes. Do not claim to have
"added specific examples" unless the examples came from the source or author.

### Edit

Require `--file`. Read it, apply minimal targeted edits, re-read it, and verify
the targeted patterns are gone. Preserve existing human voice where it is
already working.

## Scoring

The score measures AI-tell density. Lower is more human.

| Range | Verdict |
| --- | --- |
| 0-20 | Pristine on mechanical tells |
| 21-40 | Mostly human |
| 41-60 | Mixed |
| 61-80 | AI-leaning |
| 81-100 | Heavy AI pattern density |

Compute:

`score = 4 × patterns_hit + 25 × (1 - burstiness_normalized) + 15 × vocabulary_blacklist_ratio`

Clamp to 0-100.

### Substance gate

Before calling any score under 40 "human", require:

1. An owned claim the author would defend.
2. At least one real author-supplied number, name, example, or dated fact.
3. Context or stakes that pass the only-this-author test.

If any fail, report `Substance: FAIL - clean but empty` and insert intake
prompts. Absence of AI tells is not proof of authorship or value.

## Final quality check

Before returning output:

1. Remove all unresolved mechanical pattern hits.
2. Confirm there are zero em dashes.
3. Confirm no three consecutive sentences have the same shape or length.
4. Confirm every specific in the output existed in the source or came from the
   author.
5. Confirm every unresolved substantive gap is visibly flagged.
6. Confirm bullets, prose, and arrow flows match the information shape.
7. Confirm the opening starts with the claim, not an overview.
8. Confirm the ending is specific and does not add a generic conclusion.
9. Confirm the draft has an owned claim, real specific, and identifiable
   stakes, or mark the substance gate failed.
10. If calibrated, confirm capitalization, contraction rate, gloss ratio,
    structural habits, and harmless inconsistency match the samples.
11. If Slack, run the complete Slack formatting scan.
12. If Slack, confirm the main message answers the exact question without
    requiring the reader to open the thread.
13. If Slack support is included, confirm it contains evidence rather than a
    longer restatement of the answer.

For iteration, repeat detect and rewrite until there are no mechanical hits or
the requested limit is reached. Never exceed three passes.
