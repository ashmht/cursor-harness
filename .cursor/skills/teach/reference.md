# /teach — Reference: the science and the playbook

Read this when you want the *why* behind the Teaching Card, or when a topic is
hard enough that the default workflow isn't enough.

## Why the Feynman Technique works

Named for Richard Feynman, the method is four steps: pick a concept, explain it in
plain language as if to a child, find where the explanation breaks down, return to
the source to fix that specific gap, and repeat until it flows.

It works because it stacks three of the most reliably effective mechanisms in
cognitive science at once:

1. **Retrieval practice** — explaining from memory (not re-reading) strengthens
   recall far more than review does.
2. **Self-diagnosis of gaps** — the moment you reach for jargon or hand-wave is a
   precise signal of what you don't actually understand. Most people never get this
   signal because re-reading feels like understanding.
3. **Elaborative re-encoding** — rebuilding the idea in your own words and analogies
   ties it to what you already know, which is what makes it stick and transfer.

The punchline Feynman is quoted for: *if you can't explain it simply, you don't
understand it yet.* The jargon you can't unpack is the boundary of your real knowledge.

## The six evidence-based learning strategies

Replicated across decades (Dunlosky et al.; Weinstein, Madan & Sumeracki). The
Teaching Card is designed to trigger all six:

| Strategy | What it is | Where the card uses it |
|---|---|---|
| **Retrieval practice** | Recall without cues | "Check yourself" quiz; 60-second teach-back from memory |
| **Spaced practice** | Distribute over time | The quiz doubles as a spaced re-test tomorrow/next week |
| **Interleaving** | Mix related problem types | Depth ladder + curveball defense force switching altitude and angle |
| **Elaboration** | Ask/answer how & why | Curveball defense is elaborative interrogation, weaponized |
| **Concrete examples** | Real instances, not abstractions | The traced worked example |
| **Dual coding** | Verbal + visual together | "The picture" — diagram alongside the words |

Two amplifiers for hard skills:

- **Worked examples** — a fully traced solution reduces the cognitive load of a
  novice trying to hold the whole procedure in their head. That's why the card
  traces *one* object end to end rather than describing the general procedure.
- **Fading** — as expertise grows, remove scaffolding. The depth ladder is fading
  made explicit: ELI5 is full scaffold, expert is scaffold removed.

Caveat from the research: visuals must be *purposeful*. A decorative diagram adds
cognitive load without adding understanding. Every picture in a card must carry
information the words don't.

## The curveball-generation playbook

This is the part with no textbook. The goal: manufacture the questions a sharp
skeptic will ask, before they ask them, so the user is never caught flat.

### The six lenses, expanded

**1. Misconception.** Start from the wrong mental model most people carry. What's
the intuitive-but-false version? Naming it and correcting it is more memorable than
stating the truth alone, because it patches the specific bug in the listener's head.
- Prompt: "What do smart people usually get wrong about this on their first day?"

**2. Boundary.** Every simple explanation is a model, and every model has a domain
where it holds. Find the edge.
- Prompt: "At what scale / input / condition does the simple story stop being true?"
- Examples: "works until the queue backs up," "true unless the merchant is
  cross-border," "holds below ~1000 RPS."

**3. Why-not-X.** The audience will propose the obvious alternative. If you can't say
why it wasn't chosen, you don't understand the design — you understand the outcome.
- Prompt: "What's the obvious simpler/cheaper alternative, and what does it cost you?"
- This is where tradeoffs live. Name the axis being traded (latency vs consistency,
  cost vs safety, simplicity vs flexibility).

**4. Second-order.** Consequences three steps downstream. Experts think in these;
novices stop at first-order.
- Prompt: "If we changed this one thing, what breaks that nobody would predict?"

**5. Adjacent confusion.** The concept most often confused with this one. A crisp
this-vs-that boundary is one of the highest-value things you can give a learner.
- Prompt: "What's the neighbor concept people mix this up with, and what's the
  one-sentence difference?"
- Answer in the Fowler Bliki register: "**X** is … It differs from **Y** because …"

**6. Operator's caveat.** The thing you only know from running it in production /
having been burned. Docs describe the happy path; operators know the failure modes.
- Prompt: "What does the person who got paged at 3am know that the docs don't say?"

### Ordering and honesty

- **Worst-first.** Lead the defense with the question you'd least want. If you can
  answer that one cold, the rest are downhill, and you'll never be rattled.
- **`OPEN` beats bluff.** If a lens produces a question you can't answer, write
  `OPEN: <question>` and treat it as the top thing to go learn. Audiences trust
  "I don't know yet, here's how I'd find out" and distrust a confident dodge — and
  they can almost always tell the difference.
- **The nervousness test.** A real curveball makes you slightly uncomfortable. If
  every question on your list is one you already answered in the body, you generated
  softballs. Push harder.

## Depth ladder guidance

Three rungs, because most explanations pick one altitude and get stuck there:

- **ELI5** — no prerequisites, one analogy, zero jargon. The test: a smart person
  from a different field gets it.
- **Practitioner** — assumes the shared vocabulary of someone who uses this daily.
  Includes the "how to actually use / operate it" detail. Drops the analogy.
- **Expert** — the underlying mechanism, the edge cases, the caveats. Assumes the
  practitioner rung and goes beneath it to *why it's built this way*.

The user should be able to start at any rung and move up or down live, based on the
question in front of them. That mobility is what "understanding deeper than others"
actually feels like in a room.

## Visual selection

| Topic shape | Use |
|---|---|
| Flow / sequence / request path | Mermaid `sequenceDiagram` or `flowchart` |
| State machine / lifecycle | Mermaid `stateDiagram-v2` |
| Comparison / tradeoff | Markdown table |
| Quick structural sketch | ASCII boxes-and-arrows |
| Data / distribution | A chart (via canvas or a plot) — never a fake ASCII bar chart of real numbers |
| Architecture, many components | `architecture-diagram` skill |

Rule: the picture should let the reader grasp the *shape* before they read a word.
If it needs a paragraph to decode, it's the wrong picture.

## Sources

- Feynman Technique: [fs.blog](https://fs.blog/feynman-learning-technique/),
  [chunks.app](https://chunks.app/blog/the-feynman-technique-explained)
- Six strategies: Weinstein, Madan & Sumeracki, *Teaching the science of learning*
  ([Cognitive Research, 2018](https://link.springer.com/article/10.1186/s41235-017-0087-y));
  learningscientists.org
- Worked examples & fading: cognitive load theory (Sweller); medical-education
  application ([PMC10368606](https://pmc.ncbi.nlm.nih.gov/articles/PMC10368606/))
