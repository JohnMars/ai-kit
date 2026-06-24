---
name: compose-stability-diagnostics
description: >
  Use when diagnosing Jetpack Compose recomposition issues caused by parameter stability,
  unstable types, or skippability. Triggered by: "recomposition", "stability", "skippable",
  "ImmutableList", "@Stable", "@Immutable", "compose compiler report", "unstable parameter".
tools:
  - Read
  - Edit
  - Bash
---

## Kotlin 2.0.20+ strong skipping (default on)

1. Restartable composables are skippable even with unstable parameters — focus on whether parameters *compare correctly*, not on skippability alone.
2. **Stable** parameters compare with `equals`. **Unstable** parameters compare with `===` (instance identity).
3. A new unstable instance on every parent recomposition defeats skipping regardless of strong skipping mode.

## Generate compiler reports

```kotlin
// build.gradle.kts
if (providers.gradleProperty("composeReports").orNull == "true") {
    composeCompiler {
        reportsDestination = layout.buildDirectory.dir("compose_compiler")
        metricsDestination = layout.buildDirectory.dir("compose_compiler")
    }
}
```

```bash
./gradlew :app:assembleRelease -PcomposeReports=true
```

Key output files: `<module>-classes.txt` (type stability), `<module>-composables.txt` (param stability + skippability).

## Fix unstable types

4. Replace `List<T>`, `Set<T>`, `Map<K,V>` in UI state with `ImmutableList`, `ImmutableSet`, `ImmutableMap` from `kotlinx.collections.immutable`. Convert at the ViewModel boundary with `.toImmutableList()`.
5. Use `@Immutable` on data classes where all properties are effectively immutable and `equals` captures all observable state.
6. Use `@Stable` for classes with mutable state observable by Compose via `MutableState` properties.
7. Do NOT annotate to silence a compiler report — a false stability promise can produce stale UI.
8. For third-party immutable types, add a stability config file:
   ```text
   # compose_stability.conf
   java.math.BigDecimal
   java.time.*
   kotlinx.datetime.*
   ```
   ```kotlin
   composeCompiler { stabilityConfigurationFiles.add(rootProject.layout.projectDirectory.file("compose_stability.conf")) }
   ```

## Lazy list items

9. Remember per-item lambdas and derived values to prevent new instances on every parent recomposition:
   ```kotlin
   items(list, key = { it.id }) { item ->
       val onClick = remember(item.id) { { onItemClick(item.id) } }
       val isHighlighted = remember(item.id, selectedId) { item.id == selectedId }
       RowCard(onClick = onClick, isHighlighted = isHighlighted)
   }
   ```

## Anti-patterns

| Symptom | Fix |
|---|---|
| `unstable val items: List<Item>` in UI state | `ImmutableList<Item>` |
| `unstable val price: BigDecimal` | Add to stability config |
| `@Immutable` on a type with mutable internals | Remove or fix the type |
| Lazy items recompose despite unchanged data | `remember(item.id) { }` per-item lambda |
