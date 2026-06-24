---
name: compose-animations
description: >
  Use when implementing Jetpack Compose animations. Triggered by: "AnimatedVisibility",
  "AnimatedContent", "Crossfade", "rememberTransition", "animate*AsState",
  "animateContentSize", "Animatable", "AnimationSpec", "animateFloatAsState",
  "animateDpAsState", "animateColorAsState".
tools:
  - Read
  - Edit
---

## Pick the right API

| Need | API |
|---|---|
| Show/hide a subtree; content unmounts after exit | `AnimatedVisibility` |
| One property toward a target value | `animate*AsState` (`Float`, `Dp`, `Color`, `Offset`, …) |
| Several values driven by one enum/state | `rememberTransition` + child animations |
| Animate size when layout dimensions change | `Modifier.animateContentSize()` |
| Swap different composable trees in one slot | `AnimatedContent` or `Crossfade` |
| User-driven gesture motion (drag, fling, interruptible) | `Animatable` + coroutine APIs |

## Rules

1. Use `AnimatedVisibility` when content should unmount after hiding — never `animateFloatAsState(alpha)` for show/hide (alpha-only keeps content in composition and layout).
2. Animate background color with `Modifier.drawBehind { drawRect(color.value) }`, not `Modifier.background(animatedColor)`.
3. Use `Modifier.animateContentSize()` for expanding/collapsing — do not animate width/height manually.
4. Set a distinct `label` string on every `animate*AsState` call.
5. When one state drives multiple animated values that must stay in sync, use `rememberTransition` — not separate `animate*AsState` calls that can drift:
   ```kotlin
   val t = rememberTransition(phase, label = "phase")
   val alpha by t.animateFloat(label = "alpha") { if (it == Phase.Visible) 1f else 0f }
   val offset by t.animateDp(label = "offset") { if (it == Phase.Visible) 0.dp else 24.dp }
   ```
6. Set `contentKey` on `AnimatedContent` to map state to visual shape; without it every data refresh triggers a transition:
   ```kotlin
   AnimatedContent(
       targetState = result,
       contentKey = { when (it) { is Loading -> 0; is Success -> 1; is Error -> 2 } },
       label = "result",
   ) { ... }
   ```
7. Never use `LaunchedEffect` + `Animatable` for a simple target value — use `animate*AsState`.

## Anti-patterns

| Mistake | Fix |
|---|---|
| `animateFloatAsState(alpha)` for show/hide | `AnimatedVisibility` |
| Three `animateDpAsState` for one enum | One `rememberTransition` with child animations |
| `LaunchedEffect` + `Animatable` for a target | `animate*AsState` |
| `AnimatedContent` without `contentKey` | Add `contentKey` based on visual shape |
| `Modifier.background(animatedColor)` | `Modifier.drawBehind { drawRect(color) }` |
