# Product capabilities to code

Verified against commit `{{commit}}` ({{date}}). Paths are repo-relative.

What {{company}} sells, and where each piece lives. Start here when someone names a product and you
need the folders that implement it, the flow that traces it, the vendors behind it, the runbook for
when it breaks and the team that owns it.

The capability table in `{{html}}` is built from this file by `scripts/build_card.py`. Edit here,
never in `card.json`. Keep the field names below exactly; the build script reads them.

## <Group, for example Sell>

### <Capability name>

<What the user sees, in one sentence>.

- **Backend:** `<path>`, `<path>`
- **Client:** `<path>`
- **Flow:** [§1](flows.md#1-<anchor>)
- **Vendors:** [<section>](vendors.md#<anchor>)
- **When it breaks:** [<runbook>](debugging.md#<anchor>)
- **Owner:** <team>
- **Read next:** `<skill>`
