# Ruby Architecture

Ruby is the primary language for projects that use this harness. Read the
repo before assuming a framework. The Gemfile is the source of truth.

## Stack

- **Language:** CRuby. The version pin is `.ruby-version` when that file exists.
- **Dependencies:** Bundler. Add a gem only by editing the `Gemfile` and updating
  `Gemfile.lock` in the same change.
- **Web:** use the framework the Gemfile already declares. Do not add a second
  web framework.
- **Autoload:** use the loader the app already uses (Zeitwerk in modern Rails).
  Do not introduce another loader.
- **Data:** use the database adapter already in the Gemfile. Do not assume
  Postgres, MySQL, or Redis when the Gemfile says otherwise.

## Layout

Rails applications keep the conventional tree: `app/`, `config/`, `db/`,
`lib/`, `spec/` or `test/`.

Gems and non-Rails services keep loadable code in `lib/`, executables in
`exe/` or `bin/`, and tests in `spec/` or `test/`.

## Boundaries

- Keep request parsing, persistence, and network calls at the edge.
- Domain calculations take their inputs as arguments. They do not read the
  clock, randomness, or a database connection unless the existing code in that
  directory already does.
- A new directory or gem needs a reason the current layout cannot express.
