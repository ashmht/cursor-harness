# The review loop

The citation checker proves paths exist. It cannot prove a sentence is true. Close that gap with two
independent reviewers per round, each a fresh subagent that has not seen your drafting.

## Round

1. Run `scripts/check_citations.py`. Fix every ERROR and WARN first.
2. Launch both reviewers in parallel with the prompts below.
3. Verify each finding yourself before acting on it; reviewers are wrong sometimes too.
4. Fix, re-run the checker, re-render, start the next round.

**Stop** when two rounds in a row pass both tests. **Cap** at 10 rounds; if still failing, report what
remains to the user instead of looping.

## Reader test

> You are a new `<audience>` at `<company>` on day one. Using only `<skill path>`, answer these
> questions: `<8 to 12 questions a real newcomer asks, including at least three from the staff
> coverage gate for a staff audience>`. For each, say which file answered it, whether the answer was
> complete, and where you got stuck or had to guess. Do not read the codebase. End with "READER:
> PASS" if every question was answerable without guessing, else "READER: FAIL".

## Accuracy test

> You are a strict fact-checker. For every claim in `<files changed this round, or all files>`, open
> the cited path and verify the path belongs to what the claim says, the sentence matches what the
> code does, and any legacy or unclear status is backed by the citation. Search for at least five
> names on any "not found" list under two or more spellings. Flag significant omissions. Do not edit.
> Classify problems as WRONG (contradicted by code), MISLEADING (high or low impact) or MISSING.
> End with "VERDICT: PASS" if there are zero WRONG and zero high-impact MISLEADING, else
> "VERDICT: FAIL".

## What fails a round

- Any WRONG finding, or any high-impact MISLEADING one.
- A reader question that needed a guess.
- For a staff audience, any unanswered row of the staff coverage gate in `SKILL.md`.
