---
name: money-ledger-invariants
author: ashmht
status: alpha
description: >-
  Playbook for implementing or reviewing double-entry ledger / money-movement
  code. Use when adding a new money path, account type, or settlement rail to
  a financial system.
args:
  - name: target
    description: The money-movement feature being added (e.g. "withdrawal endpoint", "new settlement rail")
    required: true
  - name: language
    description: Implementation language/stack, to pick the right idempotency and property-test tooling
    required: false
---

# Money & Ledger Invariants

In a money path, correctness is scarcer than features. Preserve the accounting
invariant before optimizing throughput or adding another entry point.

## When This Skill Applies

- Adding or modifying any code that debits/credits a balance, posts a
  ledger entry, or settles a transfer.
- Adding a new settlement rail, account type, or asset to an existing
  ledger.
- Reviewing a PR that touches money movement.

## Prerequisites

- The ledger's existing balance invariant and posting model (read the
  domain layer before adding to it).
- Know whether the DB layer already enforces a balance-floor / no-mutation
  trigger — don't rely on the application layer alone.

## Non-negotiables (apply all of these)

1. **No floats in any money path.** Use integer minor units, integer
   ticks/lots, BigInt, or scaled Decimal — never float/double. Pick whichever
   the codebase already uses; don't mix representations.
2. **Money moves through exactly one code path.** If you're tempted to post
   a balance update anywhere other than the single canonical posting
   service/function, that's the bug. Route through it instead of adding a
   second entry point.
3. **Entries balance before anything is touched.** Validate the balance
   invariant in a smart constructor (reject an unbalanced entry before any
   account is mutated), not after the fact.
4. **Double-entry, immutable, append-only.** Corrections are reversals,
   never edits. If the DB supports it, add a trigger that physically rejects
   UPDATE/DELETE on posted entries — the application-layer check alone is
   not enough. A database constraint or trigger should catch callers that
   bypass the domain layer.
5. **Idempotency at every layer that can retry.** Require an
   `Idempotency-Key` (or equivalent) on the mutating endpoint; back it with
   a `UNIQUE(scope, idempotency_key)` DB constraint; and decide up front how
   a constraint-race resolves (typically: the loser re-reads and returns
   the winner's entry, rather than erroring).
6. **No lost updates under concurrency.** Lock the balance row (`FOR UPDATE`
   or equivalent) before applying a debit/credit, and add an
   optimistic-lock defense (`@Version` or equivalent) as a second layer.
7. **Atomicity of entry + balance + event.** The ledger write, the balance
   update, and any outbox/event write happen in one transaction boundary —
   never split across transactions with a "fix it up later" reconciliation
   as the only safety net.
8. **Property-test the conservation invariant, not just example cases.**
   Across arbitrary sequences of valid operations, the sum of all postings
   must be zero per asset (trial balance), and no operation should be able
   to produce a negative balance on an account that isn't explicitly
   allowed one. Use Hypothesis/fast-check/seeded fuzzing — this is the
   highest-leverage test in the whole system.
9. **Independent reconciliation.** If two views of the same activity exist
   (ledger vs. recomputed-from-raw-events, or internal vs. external venue),
   test that the reconciler actually *catches* an injected break — a
   reconciler that's never been proven to detect a mismatch might not.

## Workflow

1. **Locate the single money path** in the existing codebase before writing
   new code — grep for the existing posting service/function.
2. **Extend, don't duplicate.** Add a new rail/account-type by implementing
   the existing adapter interface and registering it, rather than branching
   the core posting logic.
3. **Write the balance/conservation property test first**, before the
   feature code — it's usually a small addition to an existing
   property-test file.
4. **Add the idempotency test.** Same key + same body replays the original
   result; same key + different body is rejected (409 or equivalent).
5. **Add a concurrency test** if the change touches balance updates: two
   concurrent operations on the same account must not both succeed in an
   inconsistent way.
6. **Verify** by re-running the full property-test suite, not just the new
   test — conservation invariants are global properties that a local change
   can silently break elsewhere.
