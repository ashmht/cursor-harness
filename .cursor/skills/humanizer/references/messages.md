# Messages, replies, and Slack

Read this whenever the text is addressed to a specific person or group (a
reply, comment, message, or email) or lands in Slack, in every mode. Skip it
for solo artifacts such as docs and blog posts. For any of these, calibrated
or not, `~/.cursor/rules/framing.mdc` wins where it conflicts with this file,
including what leads for each audience.

## Answer first

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

## Layer the message

Lead with the point in words and let the detail arrive in layers, so the
reader can stop after any layer and still have the point:

1. The point: the answer, what happened, or the ask.
2. What it means for this reader: what is fixed, what they should do, what
   you need from them and by when.
3. The numbers that back it up.
4. Many exact figures, ids, timelines, or queries: a list, the thread, a
   link, or a pasted code block.

A number can ride in the first sentence as the size of the point ("we closed
a ~$50M reconciliation gap"). What reads as AI is opening on a number the
reader has to interpret before they know what it means, or stacking several
figures before the point. Where `framing.mdc`'s audience table says a reader
leads with the amount (finance asking how much, a partner reconciliation ask)
or with exact evidence (developers debugging), follow it.

Layering moves facts; it does not drop them. Cutting a fact is a separate
decision, made only when it does not change what the reader will do, and
every number, id, or caveat you cut is named in the note to the author. Keep
the author's precision: do not round an exact figure, and do not make a
rounded one exact.

- Bad: "14 payouts ($212k) sat unmatched for two days after the Oct 21
  ingest job was OOM-killed, but payouts were unaffected. I added a retry
  and a row-count alert."
- Good: "No, payouts went out on schedule. The Oct 21 ingest job was
  OOM-killed, so 14 payouts ($212k) sat unmatched in reconciliation for
  two days. I added a retry and a row-count alert."

Answer-first is about the first sentence, not a template for the whole reply.
After it, write ordinary sentences in the order the reader needs them. Do not
rebuild the reply as labeled sections (`Root cause:`, `Impact:`,
`Next steps:`, `Evidence`), and do not re-explain background the reader wrote
or already knows.

## Evidence gate for agreement

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

- No "great", "excellent", "amazing", or "incredible" as flattery.
- Shared "we" is for a real shared goal. Use "I" for owned claims.
- Persuasion never overrides truth.

## Slack formatting

Apply when `--slack`, `--purpose slack`, or the destination is clearly Slack.
Slack uses mrkdwn, not standard Markdown.

| Intent | Emit |
| --- | --- |
| Bold | `*bold*` |
| Italic | `_italic_` |
| Strikethrough | `~strike~` |
| Inline/code block | Backticks; omit code-block language |
| Quote | `> line` |
| Bullets | `• item` |
| Numbered list | `1. item` |
| Section label (recurring formats only) | The label on its own line, plain or `*bold*` as the author wrote it |
| Link | Bare URL or `label: URL` |

Non-negotiable:

1. No `**double bold**`, `~~double strike~~`, Markdown headings, pipe tables,
   horizontal rules, Markdown links, or API-only `<url|label>` syntax.
2. Bold at most one phrase, and usually none.
3. Use exactly one blank line between paragraphs, none at the beginning or end.
4. The answer is one short paragraph, usually one to three sentences.
5. Split into a second message only when the supporting detail is long enough
   that the reader would scroll past the answer: logs, query results, a
   timeline. Write that message as normal sentences, not labeled sections, and
   do not repeat the answer in it.
6. Do not add emoji. Keep the ones the author used. A launch or ship post is
   a destination that expects one emoji after the headline, which
   `framing.mdc` allows ("unless the destination clearly expects them").
7. Strip AI-tool tracking parameters from URLs.
8. Separate explanation from identifiers: do not cram multiple UUIDs, invoices,
   and dates inline into one dense bullet. Put copy-pasteable IDs on their own
   `•` bullets (one ID per bullet) under a one- or two-sentence explanation.
9. Collapse non-actionable items ("all good" / no-change) into one clause; give
   detail only to items that need action.
10. In paste-ready blocks shown in chat, write `@Name` rather than raw
    `<@U...>` Slack user IDs (use raw IDs only inside Slack API tool payloads).

## Match where it lands

In a fast thread where people are trading short messages, a reply can be one
or two short sentences rather than a composed paragraph, but short never
means dropping a caveat. If the author's draft says the card rows are
reverted and the other rows are not checked yet, the reply carries both
halves, not only "reverted". To get a thread reply short, drop in this order:
greetings and thanks, the restated question, how you found out ("I've
checked..."), and promises the thread already implies ("I'll update once it's
fixed").

Keep the author's own capitalization and abbreviations; do not add lowercase
or slang they do not use. A new message that is mainly an ask puts the
question on the first line and the reason under it. A short reply whose first
line already gives the status keeps its closing ask where the author put it. A
launch post goes headline, what it does, then details, with any shoutout at the
end. Recurring team formats, such as a weekly Progress / Plans / Problems
update, keep their labels.

For compressed chat register, read the Slack-native section in
[generic-voice-content.md](generic-voice-content.md).

## Emitting

Emit each message as its own paste-ready fenced code block. When there are
two, say in plain words which one goes in the thread.

Before emitting, search the output for `**`, `~~`, `##`, `---`, pipe tables,
`[label](url)`, and `<url|label>`. Any survivor is a bug. Then check each `→`
and each `Label:` line: keep a UI path ("settings → payments"), an arrow or
label the author wrote, and the labels of a recurring format; rewrite the
rest as sentences. Confirm the first message answers the question without the
thread.
