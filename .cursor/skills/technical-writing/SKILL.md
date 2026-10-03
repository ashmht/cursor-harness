---
name: technical-writing
description: >-
  Write short public technical posts about shipped code by reading git history
  and implementation files, then producing reviewable Markdown with grounded
  claims. Use for feature announcements, implementation walkthroughs, and
  "help me write about what I shipped." Use `engineering-blog` for incident,
  migration, or long-form essays.
---

# Technical Writing

Turn shipped code into a concise public post. The code and commit history are
the source of truth; the post must not reveal private implementation details,
customer data, internal identifiers, or unsupported outcomes.

## Inputs

Infer what is available and ask only when a missing choice changes the result:

- Change, feature, commit range, or pull request to explain.
- Intended reader.
- Destination: Markdown, blog draft, or another publishing system.
- Desired depth and approximate length.
- Facts that may be public.

## 1. Establish scope

Write one sentence:

> This post helps [reader] understand [change] so they can [useful outcome].

Choose the smallest coherent change. A post about one decision is stronger than
a release-note dump.

## 2. Read the implementation

Use bounded source-control and code reads:

1. Inspect the relevant commit range and changed paths.
2. Read the public entry point and one or two load-bearing implementation
   details.
3. Identify the problem, chosen approach, rejected alternative, and proof.
4. Record exact source paths for factual claims.

Do not infer business outcomes from code. Use measured evidence supplied by the
user or label the expected outcome as a hypothesis.

## 3. Select a shape

Pick one:

- **Feature note:** problem → behavior → implementation detail → how to try it.
- **Walkthrough:** concrete request → numbered path → surprising decision →
  boundary.
- **Decision note:** constraint → options → choice → trade-off → evidence.
- **Lessons post:** initial belief → observed counterexample → correction →
  reusable check.

Avoid an agenda, generic introduction, or list of everything that changed.

## 4. Draft

Load one voice rule from `~/.cursor/rules/` and then `framing.mdc`.

Defaults:

- 400–700 words for one feature.
- One concrete example.
- Code snippets of 5–15 lines.
- One diagram only when it explains a relationship better than prose.
- Links on descriptive labels.
- No claim without source evidence or an explicit qualifier.

Use this frontmatter when the destination accepts Markdown:

```yaml
---
title: Short concrete title
slug: short-slug
status: draft
---
```

Do not repeat the title as an H1 unless the publishing system requires it.

## 5. Public-data review

Before saving, remove or generalize:

- Private repository, service, team, and project names.
- Ticket, incident, customer, merchant, account, and transaction identifiers.
- Internal domains, document links, dashboards, and query text.
- Exact volumes, financial figures, dates, or thresholds not approved for
  publication.
- Secrets, credential shapes, and authentication details.

Generalization must preserve the mechanism. Never invent a replacement number,
anecdote, or outcome.

## 6. Review

Run:

1. **Grounding:** each technical claim maps to a path, commit, public document,
   or supplied measurement.
2. **Reader value:** the post teaches one portable mechanism or decision.
3. **Confidentiality:** the public-data review is clean.
4. **Humanizer:** run the `humanizer` skill in detect mode, then apply only
   evidence-preserving edits.

## 7. Save

Use the user-specified destination. Otherwise save under `.drafts/` using:

```text
YYYY-MM-DD-short-slug.md
```

Publishing, changing visibility, or posting externally requires explicit user
authorization. Saving a local draft does not.

## Completion report

Return:

- Draft path.
- Title and word count.
- Source paths used.
- Claims left qualified or omitted.
- Publication action, if explicitly requested and completed.
