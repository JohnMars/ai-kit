---
name: android-coroutines-flow
description: >
  Use when implementing reactive/async data streams, coroutine-based async operations,
  or Flow-based data observation in Android/Kotlin. Triggered by: "Flow", "coroutines",
  "reactive", "observe", "StateFlow", "SharedFlow", "collect", "emit", "async data".
tools:
  - Read
  - Edit
---

## Coroutine scopes

1. Use `viewModelScope` in ViewModel, `lifecycleScope` in Fragment/Activity — never `GlobalScope`.
2. Use `supervisorScope` when child coroutine failures must not cancel siblings.

## Dispatchers

3. `Dispatchers.IO` — network and disk. `Dispatchers.Default` — CPU-bound. `Dispatchers.Main` — UI only.
4. Switch context with `withContext(Dispatchers.IO) { }` inside a coroutine, not inside `collect`.
5. Apply `flowOn(Dispatchers.IO)` on the producer chain, before terminal operators.

## StateFlow vs SharedFlow

6. `StateFlow` — UI state. Hot, always has a value, replays last to new collectors.
   - Back with `MutableStateFlow(initialValue)`, expose as `StateFlow` via `asStateFlow()`.
7. `SharedFlow` — one-time events (navigation, toasts). Use `replay = 0, extraBufferCapacity = 1`.
   - Back with `MutableSharedFlow(...)`, expose as `SharedFlow` via `asSharedFlow()`.

## Building flows

8. Convert cold sequences with `flow { emit(...) }`.
9. Convert callbacks to Flow with `callbackFlow { ... awaitClose { unregister() } }`.
10. Convert a cold Flow to a hot StateFlow in ViewModel:
    ```kotlin
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), initialValue)
    ```

## Operators

11. `flatMapLatest` — cancel previous on new emission (search, reactive queries).
12. `combine(flowA, flowB) { a, b -> }` — emit whenever either source emits.
13. `debounce(300)` — wait for silence before emitting (user input).
14. `distinctUntilChanged()` — suppress re-emissions of equal values.
15. `catch { emit(fallback) }` — handle errors without stopping collection; place before `collect`.

## Collecting in UI

16. Always collect inside `repeatOnLifecycle(Lifecycle.State.STARTED)` — never `lifecycleScope.launch { flow.collect { } }` directly.
17. Use `collectLatest { }` when only the latest value matters and processing may be slow.
