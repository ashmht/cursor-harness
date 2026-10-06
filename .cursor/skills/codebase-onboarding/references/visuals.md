# The diagram set

Diagrams go in `card.json` under `picture` (a list) and render through `scripts/render_card.py`. Two
types work well: `graph` (nodes with `col` and `row`, edges with optional labels; renders to SVG with
no network) and `mermaid` (needs the Mermaid CDN when viewed). Keep each to about ten nodes; split
anything bigger.

| # | Diagram | Shows | Audience |
|---|---|---|---|
| 1 | System context | Clients, the product, and the outside systems it calls | Everyone |
| 2 | Runtime map | Services, APIs, workers, datastores, and how requests move between them | Everyone |
| 3 | Core data model | The five to ten models everything hangs off, with their public ids | Everyone |
| 4 | The main flow, traced | One purchase, signup or request end to end, with its decision points | Everyone |
| 5 | Async and event topology | Queues, topics, schedulers, webhooks in and out | Staff |
| 6 | Path to production | PR checks, merge, build, deploy, rollout, rollback | Staff |
| 7 | Ownership map | Areas colored by owning team | Staff |
| 8 | Trust boundaries | Untrusted input, auth points, privileged zones, sensitive data stores | Staff |

The capability table is not a diagram you draw: `scripts/build_card.py` generates it from
`references/capabilities.md`.

## graph example

```json
{
  "type": "graph",
  "nodes": [
    {"id": "client", "label": "Web and mobile", "col": 1, "row": 0, "shape": "pill"},
    {"id": "api", "label": "API", "col": 1, "row": 1},
    {"id": "jobs", "label": "Workers", "col": 0, "row": 2},
    {"id": "db", "label": "Primary database", "col": 1, "row": 2, "shape": "cloud"}
  ],
  "edges": [
    {"from": "client", "to": "api"},
    {"from": "api", "to": "jobs", "label": "enqueue"},
    {"from": "api", "to": "db"}
  ],
  "caption": "Runtime map. One sentence on what to notice."
}
```

Shapes: `box` (default), `pill`, `cloud`, `diamond` (a decision). Set `color` to mark the happy path
(green), failure (red) or money (amber). Every caption says what to notice, not what the boxes are.

Run `python3 scripts/render_card.py --schema` for the full card contract.
