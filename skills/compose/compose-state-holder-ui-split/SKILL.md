---
name: compose-state-holder-ui-split
description: >
  Use when structuring a Jetpack Compose screen to separate ViewModel state collection from
  UI rendering. Triggered by: "screen composable", "ViewModel in composable", "preview not
  working", "testable UI composable", "collect flow in composable", "collectAsStateWithLifecycle".
tools:
  - Read
  - Edit
---

## The split

Every screen has two layers:

- **State-holder composable** — connects to ViewModel, collects flows, handles navigation and `UiEffect`. Not directly previewable.
- **UI composable** — receives plain `UiState` and callbacks. Previewable, testable, KMP-compatible.

```kotlin
// State-holder layer — same name, different signature
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

// UI layer — pure layout, no ViewModel reference
@Composable
fun ProfileScreen(
    state: ProfileUiState,
    onEvent: (ProfileUiEvent) -> Unit,
    modifier: Modifier = Modifier,
) {
    // layout only
}

@Preview
@Composable
private fun ProfileScreenPreview() {
    ProfileScreen(state = ProfileUiState.preview(), onEvent = {})
}
```

## Rules

1. The state-holder composable collects `StateFlow`/`SharedFlow`/`Channel`, reads from ViewModel, and handles one-time effects.
2. The UI composable takes only plain data classes and callbacks — no `ViewModel` reference, no `Flow`, no coroutines.
3. Every UI composable must be `@Preview`-able with a hardcoded or `preview()` state instance.
4. On Android, use `collectAsStateWithLifecycle()` (not `collectAsState()`) to stop collection when the UI is not visible.
5. Name both composables identically — the state-holder overload is the public entry point; the UI overload is the internal/testable surface.
6. Pass a single `onEvent: (UiEvent) -> Unit` callback rather than individual lambdas per action (matches `android-mvvm`).

## When NOT to apply

- Tiny one-off composables with no ViewModel dependency and no preview need.
- Design-system primitives (`Button`, `Card`) that have no state collection.
