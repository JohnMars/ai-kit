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

## Scope ownership

1. Only UI state holders (ViewModel) call `viewModelScope.launch { }` — this is the one permitted
   fire-and-forget boundary where synchronous UI events translate into async work.
2. All other classes (repositories, managers, data sources) expose `suspend` functions and let
   callers own scope selection. Never store `CoroutineScope` as a class property in non-UI classes.
3. Never launch from `init { }` blocks — move async work to explicit `suspend` methods called by the owner.
4. Use `supervisorScope` when child failures must not cancel siblings.

## Dispatchers

5. `Dispatchers.IO` — network and disk. `Dispatchers.Default` — CPU-bound. `Dispatchers.Main` — UI only.
6. Switch context with `withContext(Dispatchers.IO) { }` inside a coroutine, not inside `collect`.
7. Apply `flowOn(Dispatchers.IO)` on the producer chain, before terminal operators.

## Primitive selection: StateFlow vs Channel vs SharedFlow

8. **StateFlow** — UI state. Hot, sticky, always has a value, replays last to new collectors.
   - Back with `MutableStateFlow(initialValue)`, expose via `asStateFlow()`.
   - Use `.update { current -> current.copy(...) }` for atomic mutations — never direct `.value =`.
   - Do not use sentinel initial values (`NoUser`, `Empty`) — model absence explicitly with `sealed interface`, `T?`, or `Result<T>`.

9. **Channel** — single-consumer one-time events (navigation, snackbar). Guarantees delivery.
   ```kotlin
   private val _effect = Channel<UiEffect>(Channel.BUFFERED)
   val effect: Flow<UiEffect> = _effect.receiveAsFlow()
   // send: viewModelScope.launch { _effect.send(UiEffect.Navigate(...)) }
   ```

10. **SharedFlow** — multi-consumer broadcasts or event buses. Use `replay = 0, extraBufferCapacity = 1`.
    Prefer `Channel` for ViewModel → single UI consumer effects.

## Building flows

11. Convert cold sequences with `flow { emit(...) }`.
12. Convert callbacks to Flow with `callbackFlow { ... awaitClose { unregister() } }`.
13. Convert a cold Flow to a hot StateFlow — assign to a property, never call inside a function:
    ```kotlin
    val items: StateFlow<List<Item>> = repository.observeItems()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
    ```

## Operators

14. `flatMapLatest` — cancel previous on new emission (search, reactive queries).
15. `combine(flowA, flowB) { a, b -> }` — emit whenever either source emits.
16. `debounce(300)` — wait for silence before emitting (user input).
17. `distinctUntilChanged()` — suppress re-emissions of equal values.
18. `catch { emit(fallback) }` — handle errors without stopping collection; place before `collect`.

## Collecting in UI

19. Always collect inside `repeatOnLifecycle(Lifecycle.State.STARTED)` — never `lifecycleScope.launch { flow.collect { } }` directly.
20. Use `collectLatest { }` when only the latest value matters and processing may be slow.

## Anti-patterns

21. **Swallowed `CancellationException`** — always rethrow, or use `ensureActive()` after a `catch`:
    ```kotlin
    try { ... } catch (e: Exception) { ensureActive(); handleError(e) }
    ```
22. **`runBlocking` in app code** — make the calling function `suspend` instead. Reserve `runBlocking` for tests and main entry points only.
23. **Stored scope as class property** in non-UI classes — future `launch` calls on a cancelled scope silently do nothing; expose `suspend` instead.
