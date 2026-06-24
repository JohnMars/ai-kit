---
name: compose-modifier-and-layout-style
description: >
  Use when writing or reviewing Jetpack Compose layout composables and modifier chains.
  Triggered by: "modifier parameter", "modifier chain", "fillMaxWidth", "layout composable",
  "no modifier param", "hardcoded layout", "conditional layout".
tools:
  - Read
  - Edit
---

## Rules

1. **Declare `modifier: Modifier = Modifier`** on every composable that emits layout — after required params, before trailing content lambdas. Name it exactly `modifier`.

2. **Apply the caller's modifier to the root first**, then append intrinsic modifiers:
   ```kotlin
   fun Avatar(url: String, modifier: Modifier = Modifier) {
       Image(modifier = modifier.clip(CircleShape).size(48.dp), ...)  // ✅ caller first
   }
   // ❌ Wrong: modifier applied to a child, not root
   // ❌ Wrong: modifier.then(Modifier.clip(...)) — caller is last, loses caller's sizing
   ```

3. **Never hardcode layout decisions on the root** — let the caller decide `fillMaxWidth`, `padding`, `height`:
   ```kotlin
   Button(modifier = modifier.fillMaxWidth(), ...)  // ❌ forces fill on every caller
   Button(modifier = modifier, ...)                  // ✅ caller adds .fillMaxWidth() if needed
   ```
   Exception: modifiers intrinsic to the component's identity (`.clip(CircleShape)` on an `Avatar`).

4. **Build modifier chains as one fluent `val`** — no stepwise `var` reassignment:
   ```kotlin
   var m = Modifier; m = m.padding(16.dp); m = m.fillMaxSize()  // ❌
   val m = Modifier.padding(16.dp).fillMaxSize()                 // ✅
   ```
   Conditionals stay on the chain: `.then(if (selected) Modifier.background(Color.Red) else Modifier)`.

5. **Format multiline when the chain has 3+ calls** — one call per line, indented under the value:
   ```kotlin
   modifier = modifier        // ✅
       .fillMaxSize()
       .padding(16.dp)
       .weight(1f)
   ```

6. **Hoist single conditionals out of the layout** when the layout's only content is one `if`:
   ```kotlin
   Column { if (show) { Text("A"); Text("B") } }   // ❌ layout always emitted
   if (show) { Column { Text("A"); Text("B") } }    // ✅ layout only when needed
   ```
   Keep the layout as-is when it carries its own `modifier`, alignment, or arrangement args, or has siblings.

## Anti-patterns

| Symptom | Fix |
|---|---|
| No `modifier` param on a layout composable | Add `modifier: Modifier = Modifier`, apply to root |
| `modifier` accepted but not applied | Apply to root's `modifier` arg |
| `modifier` applied to a child, not the root | Move to outermost layout |
| `modifier = Modifier.x().y().then(modifier)` — caller last | Reorder: `modifier = modifier.x().y()` |
| `var m = Modifier` + reassignments | Fluent chain on a `val` |
| `Column { if (cond) X() }` — no other content | Hoist the `if` outside |
