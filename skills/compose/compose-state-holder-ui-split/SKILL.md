---
name: compose-state-holder-ui-split
description: >
  Use when structuring a Jetpack Compose screen with a ViewModel. Triggered by:
  "screen composable with ViewModel", "collectAsStateWithLifecycle", "Compose preview
  with ViewModel", "testable screen composable", "hiltViewModel in composable",
  "separate state collection from UI Compose".
tools:
  - Read
  - Edit
---

## Rules

1. Every screen has two composable overloads with the same name — a state-holder layer and a UI layer.
2. The **state-holder composable** takes a `ViewModel` param, collects flows, and handles `UiEffect`. It is not directly previewable.
3. The **UI composable** takes only plain `UiState` and `onEvent` — no `ViewModel`, no `Flow`, no coroutines. It must be `@Preview`-able.
4. Use `collectAsStateWithLifecycle()` (not `collectAsState()`) — stops collection when the UI is not visible on Android.
5. Pass a single `onEvent: (UiEvent) -> Unit` callback, not individual lambdas per action.
6. Handle one-time effects with `LaunchedEffect(Unit) { viewModel.uiEffect.collect { ... } }` in the state-holder layer — never in the UI layer.

## Pattern

```kotlin
// State-holder layer — connects ViewModel to UI
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel(),
    modifier: Modifier = Modifier,
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    LaunchedEffect(Unit) {
        viewModel.uiEffect.collect { effect ->
            when (effect) {
                is UiEffect.Navigate -> navigator.navigate(effect.route)
            }
        }
    }
    ProfileScreen(state = state, onEvent = viewModel::onEvent, modifier = modifier)
}

// UI layer — layout only, no ViewModel
@Composable
fun ProfileScreen(
    state: ProfileUiState,
    onEvent: (ProfileUiEvent) -> Unit,
    modifier: Modifier = Modifier,
) { /* layout */ }

@Preview @Composable
private fun ProfileScreenPreview() {
    ProfileScreen(state = ProfileUiState.preview(), onEvent = {})
}
```

## Anti-patterns

| Mistake | Fix |
|---|---|
| `hiltViewModel()` inside the UI-layer composable | Move to state-holder layer only |
| `collectAsState()` instead of `collectAsStateWithLifecycle()` | Replace on Android targets |
| Individual `onClick`, `onDismiss` lambdas on the UI layer | Single `onEvent: (UiEvent) -> Unit` |
| `UiEffect` collected in UI-layer composable | Move collection to state-holder layer |
| No `@Preview` on the screen | UI-layer composable must have a preview |

## When NOT to apply

- Composables with no ViewModel dependency.
- Design-system components (`Button`, `Card`) — these have no state collection.
