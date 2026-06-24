---
name: compose-stability-diagnostics
description: >
  Use when diagnosing Jetpack Compose recomposition or performance issues caused by
  unstable parameter types or skippability. Triggered by: "unstable parameter",
  "compose compiler report", "ImmutableList in Compose", "@Stable annotation",
  "@Immutable annotation", "composable not skipping", "recomposition too frequent",
  "List unstable Compose".
tools:
  - Read
  - Edit
  - Bash
---

## Kotlin 2.0.20+ strong skipping

1. All restartable composables are skippable even with unstable params. Focus on whether parameters *compare correctly*, not skippability alone.
2. **Stable** params: compared with `equals`. **Unstable** params: compared with `===` (identity). A new unstable instance on every parent recomposition defeats skipping.

## Generate compiler reports

Add to `build.gradle.kts`:
```kotlin
if (providers.gradleProperty("composeReports").orNull == "true") {
    composeCompiler {
        reportsDestination = layout.buildDirectory.dir("compose_compiler")
        metricsDestination = layout.buildDirectory.dir("compose_compiler")
    }
}
```
Run: `./gradlew :app:assembleRelease -PcomposeReports=true`

Read `<module>-classes.txt` for type stability, `<module>-composables.txt` for param stability per composable.

## Fix unstable types

3. Replace `List<T>`, `Set<T>`, `Map<K,V>` in UI state with `ImmutableList`, `ImmutableSet`, `ImmutableMap` (`kotlinx.collections.immutable`). Convert at the ViewModel boundary: `.toImmutableList()`.
4. Annotate with `@Immutable` only when: all properties are val, all property types are stable, and `equals` captures all observable state.
5. Annotate with `@Stable` only when: mutable state is exposed via `MutableState` properties observable by Compose.
6. Never add `@Stable`/`@Immutable` solely to silence a compiler report — a false promise causes stale UI.
7. For third-party types the compiler can't inspect, add a stability config file:
   ```
   # compose_stability.conf
   java.math.BigDecimal
   java.time.*
   kotlinx.datetime.*
   ```
   Wire it in `build.gradle.kts`:
   ```kotlin
   composeCompiler {
       stabilityConfigurationFiles.add(rootProject.layout.projectDirectory.file("compose_stability.conf"))
   }
   ```

## Lazy list items

8. `remember` per-item lambdas and derived values — new lambda instances on every parent recomposition force row recomposition even when data is unchanged:
   ```kotlin
   items(list, key = { it.id }) { item ->
       val onClick = remember(item.id) { { onItemClick(item.id) } }
       val isSelected = remember(item.id, selectedId) { item.id == selectedId }
       RowCard(onClick = onClick, isSelected = isSelected)
   }
   ```

## Anti-patterns

| Symptom | Fix |
|---|---|
| `unstable val items: List<Item>` in UI state | `ImmutableList<Item>` |
| `unstable val price: BigDecimal` | Add `java.math.BigDecimal` to stability config |
| `@Immutable` on a type with mutable internals | Remove annotation or fix the type |
| Lazy rows recompose despite unchanged item data | `remember(item.id)` for per-item lambdas |
