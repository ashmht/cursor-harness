---
name: notion-mcp
description: Search, fetch, create, and update Notion pages and databases via Notion MCP. Use when the user asks to search Notion, read or edit a Notion page, create docs in Notion, query a Notion database, or work with Notion runbooks and wikis.
---

# Notion MCP Skill

Use the **Notion MCP** (user-notion) to search the workspace, fetch pages/databases, create or update content, and query databases. Apply this skill when the user wants to work with Notion (search docs, create/update pages, runbooks, wikis, or databases).

## When This Skill Applies

- User asks to **search Notion** (e.g. "find the runbook for X", "search Notion for design docs").
- User provides a **Notion URL or page ID** and wants to read or edit it.
- User wants to **create** a Notion page, doc, or database entry.
- User wants to **update** an existing Notion page (properties or content).
- User wants to **query a Notion database** (filter, aggregate, export).
- User mentions **runbooks, wikis, or team docs** in Notion.

## Prerequisites

- **Notion MCP** must be enabled in Cursor (user-notion server).
- User must have access to the Notion workspace; MCP uses their connected Notion account.

## Core Workflows

### 1. Search workspace

- Use **notion-search** with `query_type: "internal"` for semantic search.
- **Important:** Set `content_search_mode: "workspace_search"` to search Notion pages only. The default `ai_search` includes connected sources (Slack, Google Calendar, etc.) and often returns irrelevant results like calendar events. Only use `ai_search` when you explicitly want cross-source results.
- Use **notion-search** with `query_type: "user"` to find users by name or email.
- Optional: `teamspace_id`, `page_url`, `data_source_url`, or `filters` (e.g. `created_date_range`, `created_by_user_ids`).
- After search, use **notion-fetch** with a result page ID/URL to get full content.

### 2. Read a page or database

- Use **notion-fetch** with `id` = page URL or ID (UUID with or without dashes).
- Pages return **Notion-flavored Markdown**. For the full spec, fetch MCP resource `notion://docs/enhanced-markdown-spec`.
- Databases return data sources; use `<data-source url="collection://...">` IDs for **notion-query-data-sources** and **notion-create-pages** (parent `data_source_id`).

### 3. Create pages

- Use **notion-create-pages** with `pages` (each: `properties`, optional `content`).
- **Parent**: `page_id`, `database_id`, or `data_source_id`. For databases, fetch first to get `data_source_id` (collection URL); use it when the DB has multiple sources.
- **Properties**: For DB pages, fetch the database first and use exact property names from the schema. Use expanded formats for dates (`date:Prop:start`, etc.), checkboxes (`__YES__`/`__NO__`), numbers as numbers.
- **Content**: Notion Markdown; do not put the title in content (only in `properties`). Fetch `notion://docs/enhanced-markdown-spec` before guessing syntax.

### 4. Update a page

- Use **notion-update-page** with `page_id` and a command:
  - `update_properties`: set/change properties (same value rules as create).
  - `update_content`: targeted edits using `content_updates` array with `old_str`/`new_str` pairs (supports `replace_all_matches`).
  - `replace_content`: full body replacement with new content string.
  - `apply_template`: apply a template to the page by `template_id`.
  - `update_verification`: set verification status and expiry.
- Always **fetch** the page first when updating content so selections and schema are correct. Preserve child pages/databases by including `<page url="...">` / `<database url="...">` when replacing content; confirm with user before deleting child content.

### 5. Query a database

- **Fetch** the database to get `data_source_urls` (collection URLs).
- Use **notion-query-data-sources** with either:
  - **SQL mode**: `data_source_urls`, `query` (SQLite), optional `params`; checkbox values `__YES__`/`__NO__`.
  - **View mode**: `view_url` to run a view’s filters/sorts.

### 6. Views

- **notion-create-view**: create a database view (table, board, list, calendar, timeline, gallery, form, chart, map, dashboard). Use `configure` with the View DSL.
- **notion-update-view**: update an existing view's name or configuration. Supports CLEAR directives for resetting filters/sorts.
- For the View DSL spec, fetch MCP resource `notion://docs/view-dsl-spec`.

### 7. Meeting notes

- **notion-query-meeting-notes**: query meeting notes with filters on title, attendees, created/edited times. Useful for pulling action items from 1:1s and syncs.

### 8. Other actions

- **notion-duplicate-page**, **notion-move-pages**: duplicate or move pages.
- **notion-create-comment**, **notion-get-comments**: add or list comments on a block.
- **notion-get-teams**, **notion-get-users**: list teams/users.
- **notion-create-database**, **notion-update-data-source**: create/update databases and data sources.

## Conventions

- **IDs**: Use page/database/data-source IDs with or without dashes; full Notion URLs are also accepted.
- **Markdown**: Never guess Notion Markdown; fetch `notion://docs/enhanced-markdown-spec` when creating or updating content.
- **Databases**: Prefer `data_source_id` (from fetch) over `database_id` when creating pages if the DB has multiple data sources.
- **Safety**: On update, if the tool requires `allow_deleting_content` for child pages, list what would be deleted and ask for user confirmation before proceeding.

## References

- MCP tool details and examples: [reference.md](reference.md).
- Notion Markdown spec: fetch MCP resource `notion://docs/enhanced-markdown-spec` when editing content.
- View DSL spec: fetch MCP resource `notion://docs/view-dsl-spec` when creating or updating views.
