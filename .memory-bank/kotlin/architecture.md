# Service Architecture

## Tech Stack

- **Language & Build**: JDK 17+, Kotlin, Gradle
- **Frameworks**: (list your frameworks here)
- **Data Storage**: (list your databases here)
- **Observability**: (list your observability stack here)
- **Testing**: JUnit 5, MockK, (others)

## Project Structure

```
<service>/
├── build.gradle.kts           # Module build configuration
└── src/
    ├── main/kotlin/           # Production source
    ├── main/resources/        # Runtime resources
    └── test/kotlin/           # Tests
```

## Dependencies

**Rule**: To find all dependencies and versions, check sources in this order:

1. **Module build**: `<service>/build.gradle.kts`
2. **Version catalog**: `gradle/libs.versions.toml`
3. **Dependency locks**: the repository's Gradle lockfiles, when enabled
