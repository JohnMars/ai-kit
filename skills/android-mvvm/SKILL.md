---
name: android-mvvm
description: >
  Use when building a new screen, feature, or UI component in Android following MVVM
  with a ViewModel contract, Jetpack ViewModel, and Kotlin Coroutines. Triggered by:
  "ViewModel", "MVVM", "screen", "UI state", "new feature", "architecture".
tools:
  - Read
  - Edit
---

## Contract

1. Define a contract object per feature with three nested types:
   - `UiState` — data class, all state needed to render the screen. Default to empty/non-loading.
   - `UiEvent` — sealed class, user-initiated actions dispatched from the View.
   - `UiEffect` — sealed class, one-time side effects the View must consume (navigation, toasts).

```kotlin
object FeatureContract {
    data class UiState(val isLoading: Boolean = false, val items: List<Item> = emptyList())
    sealed class UiEvent { data object Refresh : UiEvent() }
    sealed class UiEffect { data class ShowError(val msg: String) : UiEffect() }
}
```

## ViewModel

2. Extend `ViewModel()` from `androidx.lifecycle`.
3. Expose `uiState: StateFlow<UiState>` backed by `MutableStateFlow(UiState())`.
4. Expose `uiEffect: SharedFlow<UiEffect>` backed by `MutableSharedFlow(extraBufferCapacity = 1)`.
5. Accept all user actions through a single `fun onEvent(event: UiEvent)` entry point.
6. Launch all coroutines in `viewModelScope`. Update state with `_uiState.update { it.copy(...) }`.
7. Never hold a reference to Context, View, or Fragment in the ViewModel.
8. Use `@HiltViewModel` + constructor injection when using Hilt; otherwise use a `ViewModelProvider.Factory`.

## View (Fragment / Composable)

9. Observe `uiState` and `uiEffect` only inside `repeatOnLifecycle(Lifecycle.State.STARTED)`.
10. Dispatch actions with `viewModel.onEvent(UiEvent.X)` — no logic in the View.
11. Keep Fragment/Composable dumb: render state, dispatch events, react to effects.

```kotlin
// Fragment
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        launch { viewModel.uiState.collect { render(it) } }
        launch { viewModel.uiEffect.collect { handle(it) } }
    }
}
```
