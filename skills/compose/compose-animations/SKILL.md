---
name: compose-animations
description: >
  Use when implementing animations in Jetpack Compose. Triggered by: "animate",
  "animation", "AnimatedVisibility", "transition", "fade", "slide", "expand",
  "animateContentSize", "AnimatedContent", "Crossfade".
tools:
  - Read
  - Edit
---

## Pick the smallest API

| Need | API |
|---|---|
| Show/hide a subtree with enter/exit; content removed after exit | `AnimatedVisibility` |
| One property toward a target value | `animate*AsState` (`Float`, `Dp`, `Color`, `Offset`, …) |
| Several values driven by one piece of state | `rememberTransition` + child animations |
| Animate size when layout dimensions change | `Modifier.animateContentSize()` |
| Swap different composable trees in the same slot | `AnimatedContent` or `Crossfade` |
| User-driven gesture motion (drag, fling, interruptible) | `Animatable` + coroutine APIs |

## Rules

1. Prefer `AnimatedVisibility` over `animateFloatAsState(alpha)` when content should unmount — alpha-only fading keeps content in composition and layout.
2. Animated background color: use `Modifier.drawBehind { drawRect(color.value) }`, not `Modifier.background(animatedColor)`.
3. `Modifier.animateContentSize()` for expanding/collapsing content — do not hand-roll width/height animations.
4. Set a distinct `label` on every `animate*AsState` call for tooling and debugging.
5. When one state drives multiple animated values that must stay in sync, use `rememberTransition` + child animations — not several independent `animate*AsState` calls that can drift:
   ```kotlin
   val transition = rememberTransition(targetState = phase, label = "phase")
   val alpha by transition.animateFloat(label = "alpha") { if (it == Phase.Visible) 1f else 0f }
   val offset by transition.animateDp(label = "offset") { if (it == Phase.Visible) 0.dp else 24.dp }
   ```
6. `AnimatedContent`: always set `contentKey` to map rich state to visual shape — without it every data refresh triggers a transition:
   ```kotlin
   AnimatedContent(
       targetState = result,
       contentKey = { when (it) {
           is Loading -> "loading"; is Success -> "content"; is Error -> "error"
       } },
       label = "screen-content",
   ) { ... }
   ```
7. `stateIn` values that feed `Modifier.offset` or `Modifier.graphicsLayer` should use block-form (deferred-read) modifiers, not value-form — see `compose-state-deferred-reads`.

## Anti-patterns

| Mistake | Fix |
|---|---|
| `animateFloatAsState(alpha)` but expects content to unmount | `AnimatedVisibility` |
| Three `animateDpAsState` in sync with one enum | One `rememberTransition` |
| `LaunchedEffect` + `Animatable` for simple target animation | `animate*AsState` |
| `AnimatedContent(result)` without `contentKey` | Add `contentKey` based on visual shape |
| Animated color on `Modifier.background` | `drawBehind { drawRect(animatedColor) }` |
