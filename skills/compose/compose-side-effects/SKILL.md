---
name: compose-side-effects
description: >
  Use when managing side effects in Jetpack Compose — LaunchedEffect, DisposableEffect,
  SideEffect, rememberCoroutineScope, snapshotFlow. Triggered by: "side effect",
  "LaunchedEffect", "DisposableEffect", "collect flow in composable", "register listener",
  "coroutine in composable".
tools:
  - Read
  - Edit
---

## Pick the right API

| Need | API |
|---|---|
| Publish Compose state to non-Compose code after every recomposition | `SideEffect` |
| Register/unregister a listener, observer, or resource | `DisposableEffect(keys...)` |
| Suspending or keyed one-shot work | `LaunchedEffect(keys...)` |
| Launch suspending work from a user event | `rememberCoroutineScope()` |
| Convert snapshot reads into a Flow | `snapshotFlow { }` inside `LaunchedEffect` |

## Effect keys

1. Use the thing whose lifecycle the effect follows as the key — never `Unit` when the input changes:
   ```kotlin
   LaunchedEffect(userId) { repository.events(userId).collect { handle(it) } }  // ✅
   LaunchedEffect(Unit) { repository.events(userId).collect { handle(it) } }     // ❌ stale userId
   ```
2. Do not use broad objects (`viewModel`, `state`) as keys when only one property matters.
3. Do not add lambdas as keys unless you want restarts on every lambda instance change.

## rememberUpdatedState

4. Use when the effect must NOT restart but needs the latest callback value:
   ```kotlin
   val latestOnTimeout by rememberUpdatedState(onTimeout)
   LaunchedEffect(Unit) { delay(1_000); latestOnTimeout() }
   ```
5. Do NOT read it eagerly inside `remember {}` — it captures once and never refreshes:
   ```kotlin
   val latest by rememberUpdatedState(id)
   val obj = remember { Obj(id = latest) }     // ❌ captured once
   val obj = remember(id) { Obj(id = id) }     // ✅ keyed on the changing value
   ```

## DisposableEffect

6. Every setup path must have a matching `onDispose` cleanup:
   ```kotlin
   DisposableEffect(owner, observer) {
       owner.lifecycle.addObserver(observer)
       onDispose { owner.lifecycle.removeObserver(observer) }
   }
   ```

## User events

7. Use `rememberCoroutineScope()` in click callbacks — do not use an event-flag state to trigger a `LaunchedEffect`:
   ```kotlin
   val scope = rememberCoroutineScope()
   Button(onClick = { scope.launch { snackbarHostState.showSnackbar("Saved") } }) { ... }
   ```

## Anti-patterns

| Mistake | Fix |
|---|---|
| Side work (network, analytics) in the composable body | Move to ViewModel or `LaunchedEffect` |
| `LaunchedEffect(Unit)` with changing `id` inside | Key by `id` |
| `snapshotFlow { }.map { }` with no terminal `collect` | Add `.collect { }` |
| Listener added in `LaunchedEffect`, no cleanup | Use `DisposableEffect` |
| `var shouldShow = true` state triggering `LaunchedEffect` | `rememberCoroutineScope()` in the click |
| `rememberUpdatedState` delegate read inside `remember {}` | Key `remember` on the changing value |
