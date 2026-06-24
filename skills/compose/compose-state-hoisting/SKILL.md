---
name: compose-state-hoisting
description: >
  Use when deciding where to place state in Jetpack Compose. Triggered by:
  "remember in Compose", "rememberSaveable", "hoist state Compose",
  "plain state holder Compose", "remember vs ViewModel Compose",
  "Compose state holder class", "@Stable class", "rememberXxxState".
tools:
  - Read
  - Edit
---

## Decision: hoist only as far as the logic needs

| Tier | Use when | Mechanism |
|---|---|---|
| **Local** | Only one composable reads/writes it | `remember { }` or `rememberSaveable { }` |
| **Hoisted** | Sibling composables share it | Move to nearest common ancestor |
| **Plain state holder** | Several coordinated UI values + named operations | `@Stable` class + `remember { XxxState() }` |
| **ViewModel** | Repository calls, persistence, or business rules | Jetpack `ViewModel` |

## Rules

1. Start local. Hoist only when a second composable needs the same state.
2. Use `rememberSaveable` instead of `remember` when the state must survive process death or config change.
3. Extract a plain `@Stable` state holder class when: several `remember` values are coordinated by the same logic, or the composable body is hard to read due to state management volume.
4. Never put repository calls or business rules inside a plain Compose state holder — that belongs in a ViewModel.
5. Never run animation `suspend` functions from `viewModelScope` — animations are composition-scoped, not ViewModel-scoped.
6. Provide a `rememberXxxState()` factory function for every state holder class:
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

- Hoisting every state to ViewModel "just in case" — start local, promote when a second composable needs it.
- Repository calls inside a Compose `@Stable` state holder.
- `viewModelScope.launch { animate(...) }` — move animations to a `rememberCoroutineScope()` inside composition.
