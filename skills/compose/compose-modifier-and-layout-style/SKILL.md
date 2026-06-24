---
name: compose-modifier-and-layout-style
description: >
  Use when writing or reviewing Jetpack Compose layout functions and modifier chains.
  Triggered by: "Modifier parameter", "modifier chain", "Compose modifier",
  "fillMaxWidth on composable", "Column modifier", "Row modifier", "Box modifier",
  "missing modifier param", "Modifier.then", "Modifier order".
tools:
  - Read
  - Edit
---

## Rules

1. Declare `modifier: Modifier = Modifier` on every `@Composable` that emits layout — after required params, before trailing content lambdas. Use exactly the name `modifier`.

2. Apply the caller's modifier to the root element first, then append component-intrinsic modifiers:
   ```kotlin
   // ✅ caller modifier first
   fun Avatar(url: String, modifier: Modifier = Modifier) {
       Image(modifier = modifier.clip(CircleShape).size(48.dp), ...)
   }
   // ❌ caller modifier last — loses caller's sizing intent
   fun Avatar(url: String, modifier: Modifier = Modifier) {
       Image(modifier = Modifier.clip(CircleShape).size(48.dp).then(modifier), ...)
   }
   ```

3. Never hardcode sizing or spacing on the root — let callers decide `fillMaxWidth`, `padding`, `height`:
   ```kotlin
   Button(modifier = modifier.fillMaxWidth(), ...)  // ❌ forces fill on every caller
   Button(modifier = modifier, ...)                  // ✅
   ```
   Exception: modifiers intrinsic to the component's identity (`.clip(CircleShape)` on `Avatar`).

4. Build modifier chains as a single fluent expression — never stepwise `var` reassignment:
   ```kotlin
   var m = Modifier; m = m.padding(16.dp); m = m.fillMaxSize()  // ❌
   val m = Modifier.padding(16.dp).fillMaxSize()                 // ✅
   ```
   Inline conditionals with `.then(if (selected) Modifier.background(Color.Red) else Modifier)`.

5. Format chains with 3+ calls one-per-line:
   ```kotlin
   modifier = modifier
       .fillMaxSize()
       .padding(16.dp)
       .weight(1f)
   ```

6. Hoist a single `if` out of an otherwise-empty layout composable:
   ```kotlin
   Column { if (show) { Text("A"); Text("B") } }  // ❌ Column always emitted
   if (show) { Column { Text("A"); Text("B") } }   // ✅
   ```
   Keep the layout when it carries its own `modifier`, `arrangement`, `alignment`, or sibling content.

## Anti-patterns

| Symptom | Fix |
|---|---|
| No `modifier` param on a layout `@Composable` | Add `modifier: Modifier = Modifier`, apply to root |
| `modifier` accepted but not forwarded | Apply to root element's `modifier` argument |
| `modifier` applied to a child, not the root | Move to outermost layout |
| `Modifier.x().y().then(modifier)` — caller last | `modifier.x().y()` — caller first |
| `var m = Modifier` + reassignments | Fluent `val` chain |
| `Column { if (cond) Content() }` sole content | Hoist `if` outside `Column` |
