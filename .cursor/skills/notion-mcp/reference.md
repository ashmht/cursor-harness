# Notion MCP — Tool Reference

Quick reference for Notion MCP (user-notion) tools. Use this when you need parameter details or patterns.

## Tools Overview

| Tool | Purpose |
|------|--------|
| **notion-search** | Semantic search over workspace (+ connected sources) or user search |
| **notion-fetch** | Get page or database by URL/ID (Markdown or schema + data sources) |
| **notion-create-pages** | Create one or more pages under a page, database, or data source |
| **notion-update-page** | Update properties or content (replace/insert ranges) |
| **notion-query-data-sources** | SQL or view-based queries on databases |
| **notion-duplicate-page** | Duplicate a page |
| **notion-move-pages** | Move pages to another parent |
| **notion-create-comment** / **notion-get-comments** | Comments on a block |
| **notion-get-teams** / **notion-get-users** | List teams and users |
| **notion-create-database** / **notion-update-data-source** | Create/update DBs and data sources |

## Common Patterns

### Search then fetch

1. `notion-search` with `query`, `query_type: "internal"` (or `"user"`).
2. From results, take a page ID/URL and call `notion-fetch` with that `id` for full content.

### Create page in a database

1. `notion-fetch` with the database URL/ID.
2. From the response, get `data_source_id` from `<data-source url="collection://...">`.
3. `notion-create-pages` with `parent: { type: "data_source_id", data_source_id: "..." }`, and `pages[].properties` matching the schema (incl. title and any required props). Use date/checkbox/number formats as in the main skill.

### Update page content safely

1. `notion-fetch` with the page ID to get current content and structure.
2. Fetch `notion://docs/enhanced-markdown-spec` if you need exact Markdown rules.
3. `notion-update-page` with command `update_content` and a
   `content_updates` array of exact `old_str` / `new_str` replacements. Use
   `replace_all_matches` only when every match should change.
4. For a full rewrite, use command `replace_content`. If the tool reports child
   pages/databases would be deleted, list them and ask the user before enabling
   content deletion.

### Query database with SQL

1. `notion-fetch` database to get `data_source_urls` (e.g. `collection://uuid`).
2. `notion-query-data-sources` with `mode: "sql"`, `data_source_urls`, `query` (SQLite; table name = data source URL in quotes), and `params` if using `?` placeholders. Use `__YES__`/`__NO__` for checkbox columns.

## Property value formats (create/update)

- **Title**: inline Markdown string.
- **Checkbox**: `"__YES__"` or `"__NO__"`.
- **Number**: JSON number (not string).
- **Date**: `date:{property}:start`, optional `date:{property}:end`, `date:{property}:is_datetime` (0 or 1).
- **Place**: `place:{property}:name`, `address`, `latitude`, `longitude`, optional `google_place_id`.
- **Names**: Properties named `id` or `url` (case-insensitive) use prefix `userDefined:` (e.g. `userDefined:URL`).

## Resource

- **notion://docs/enhanced-markdown-spec** — Fetch this MCP resource before writing or editing page content in Notion Markdown.
