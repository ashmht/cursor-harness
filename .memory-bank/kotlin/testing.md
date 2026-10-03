# Testing Standards

## Testing Tools

- JUnit 5 (test framework)
- MockK (mocking library)
- (add your tools here)

## Naming Conventions

- Test classes: `[ClassName]Test.kt`
- Test methods: backtick format `` `should [behavior] when [condition]` ``

## Test Structure

- Use `@Nested` to group related scenarios
- One behavior per test method
- Follow AAA pattern (Arrange, Act, Assert)

## Commands

- `./gradlew test` — Run all tests
- `./gradlew :module:test --tests "package.ClassName"` — Run a specific test file
- `./gradlew check` — Run tests, linting, and coverage
