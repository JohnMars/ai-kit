---
name: compose-side-effects
description: >
  Use when managing Jetpack Compose side effects. Triggered by: "LaunchedEffect",
  "DisposableEffect", "SideEffect", "rememberCoroutineScope", "snapshotFlow",
  "collect flow in Composable", "register listener in Composable",
  "LaunchedEffect key", "rememberUpdatedState".
tools:
  - Read
  - Edit
---

## Pick the right API

| Need | API |
|---|---|
| Publish Compose state to non-Compose code after recomposition | `SideEffect` |
| Register/unregister a listener or resource tied to composition | `DisposableEffect(keys...)` |
| Suspending or keyed one-shot work | `LaunchedEffect(keys...)` |
| Launch suspending work from a user event | `rememberCoroutineScope()` |
| Convert snapshot reads to a Flow | `snapshotFlow { }` inside `LaunchedEffect` |

## Effect keys

1. Key `LaunchedEffect` on the value whose lifecycle the effect follows — never `Unit` when the input can change:
   ```kotlin
   LaunchedEffect(userId) { repo.events(userId).collect { handle(it) } }  // ✅
   LaunchedEffect(Unit) { repo.events(userId).collect { handle(it) } }     // ❌ stale userId
   ```
2. Do not use broad objects (`viewModel`, `state`) as keys when only one property matters.
3. Do not pass lambdas as keys — they are new instances every recomposition and will restart the effect.

## rememberUpdatedState

4. Use when the effect must NOT restart but needs the latest callback:
   ```kotlin
   val latest by rememberUpdatedState(onTimeout)
   LaunchedEffect(Unit) { delay(1_000); latest() }
   ```
5. Never read `rememberUpdatedState` eagerly inside `remember {}` — it captures once:
   ```kotlin
   val latest by rememberUpdatedState(id)
   val obj = remember { Obj(id = latest) }     // ❌ stale after first composition
   val obj = remember(id) { Obj(id = id) }     // ✅
   ```

## DisposableEffect

6. Every setup must have a matching `onDispose` cleanup:
   ```kotlin
   DisposableEffect(owner, observer) {
       owner.lifecycle.addObserver(observer)
       onDispose { owner.lifecycle.removeObserver(observer) }
   }
   ```

## User-triggered work

7. Use `rememberCoroutineScope()` in click callbacks — not an event-flag state triggering a `LaunchedEffect`:
   ```kotlin
   val scope = rememberCoroutineScope()
   Button(onClick = { scope.launch { snackbarHostState.showSnackbar("Saved") } }) { ... }
   ```

## Anti-patterns

| Mistake | Fix |
|---|---|
| Network or analytics calls in composable body | `LaunchedEffect` or ViewModel |
| `LaunchedEffect(Unit)` reads a changing `id` | Key by `id` |
| `snapshotFlow { }` with no terminal `collect` | Add `.collect { }` |
| Listener added in `LaunchedEffect`, never removed | `DisposableEffect` |
| State flag triggers `LaunchedEffect` for click action | `rememberCoroutineScope()` in the callback |
| `rememberUpdatedState` delegate read inside `remember {}` | Key `remember` on the changing value |
