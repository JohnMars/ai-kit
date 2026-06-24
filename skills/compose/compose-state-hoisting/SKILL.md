---
name: compose-state-hoisting
description: >
  Use when deciding where to place state in Jetpack Compose — local remember, plain state
  holder class, or ViewModel. Triggered by: "state hoisting", "where to put state",
  "lift state", "remember vs ViewModel", "state holder class", "rememberSaveable".
tools:
  - Read
  - Edit
---

## Decision: hoist only as far as the logic needs

| Tier | Use when | How |
|---|---|---|
| **Local** | Only one composable needs it | `remember { }` or `rememberSaveable { }` |
| **Hoisted** | Sibling composables share it | Move to nearest common ancestor |
| **Plain state holder** | Multiple coordinated UI values + named operations | `@Stable` class + `remember { XxxState() }` |
| **ViewModel** | Repository calls, persistence, or business logic | Jetpack `ViewModel` — see `android-mvvm` |

## Rules

1. Start local — hoist only when a second composable needs the same state.
2. Use `rememberSaveable` instead of `remember` when the state must survive process death or config changes.
3. Extract a plain state holder class when:
   - Several related `remember` values are coordinated by the same callbacks.
   - Scroll, focus, text selection, or sheet state needs named operations.
   - The composable body becomes hard to read due to state management volume.
4. Never put repository calls or business rules in a plain Compose state holder — that belongs in a ViewModel.
5. Never run animation `suspend` functions from `viewModelScope` — animation is composition-scoped, not ViewModel-scoped.

## Plain state holder pattern

```kotlin
@Stable
class SearchState(initialQuery: String = "") {
    var query by mutableStateOf(initialQuery)
    var isExpanded by mutableStateOf(false)

    fun clear() { query = ""; isExpanded = false }
}

@Composable
fun rememberSearchState(initial: String = "") = remember { SearchState(initial) }
```

## Anti-patterns

- Lifting every state to ViewModel "just in case" — start local, promote only when needed.
- Repository calls inside a Compose state holder class.
- `viewModelScope.launch { animate(...) }` — animations must live in composition scope.
