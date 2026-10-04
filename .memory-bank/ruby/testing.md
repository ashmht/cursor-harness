# Ruby Testing

Use the test library the repository already has. Do not add the other one.

- `spec/` means RSpec. Run `bundle exec rspec`.
- `test/` means Minitest. Run `bundle exec rake test`.
- Lint with RuboCop when the Gemfile includes it: `bundle exec rubocop`.
- Format is RuboCop as well. Do not add a second Ruby formatter.

## Shape

- One behavior per example.
- Name the condition and the expected result in the example name.
- Arrange, act, assert. Keep fixtures and factories that already exist. Do not
  add a second factory library.
- Unit examples do not open network connections. Stub the edge the production
  code already uses, or drive a recorded fixture.

## Commands

- `bundle exec rspec` — RSpec repositories
- `bundle exec rspec spec/path/file_spec.rb` — one file
- `bundle exec rake test` — Minitest repositories
- `bundle exec rubocop` — lint

The harness example gate in `templates/harness.yaml.example` uses RSpec. Switch
that gate to `bundle exec rake test` when the repository is Minitest.
