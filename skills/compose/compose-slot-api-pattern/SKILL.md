---
name: compose-slot-api-pattern
description: >
  Use when designing or reviewing a reusable Jetpack Compose component whose visual
  content varies by caller. Triggered by: "reusable component", "slot API", "content
  parameter", "composable lambda param", "boolean flag", "shape variant".
tools:
  - Read
  - Edit
---

## Core rule

Replace primitive content parameters (`title: String`, `icon: ImageVector`) with `@Composable () -> Unit` slots. The component describes structure; the caller provides content.

## Rules

1. **Convert primitive content params to slots**:
   ```kotlin
   // ❌ BAD — primitives lock content shape
   fun SettingsRow(title: String, leadingIcon: ImageVector?, subtitle: String?)

   // ✅ GOOD — caller provides any content
   fun SettingsRow(
       headlineContent: @Composable () -> Unit,
       modifier: Modifier = Modifier,
       leadingContent: (@Composable () -> Unit)? = null,
       supportingContent: (@Composable () -> Unit)? = null,
       trailingContent: (@Composable () -> Unit)? = null,
   )
   ```

2. **Replace boolean shape flags** (`showChevron`, `showSwitch`, `mode: Mode`) with a single nullable slot.

3. **Use nullable slots with `null` default** for optional areas — lets the component omit spacing when absent:
   ```kotlin
   leadingContent: (@Composable () -> Unit)? = null  // ✅ component branches on null
   leadingContent: @Composable () -> Unit = {}        // ❌ component always allocates the slot
   ```

4. **Add scope receivers** when the slot renders inside a layout scope:
   ```kotlin
   actions: @Composable RowScope.() -> Unit = {}   // renders inside a Row
   content: @Composable BoxScope.() -> Unit         // renders inside a Box
   ```

5. **Name slots** with `xxxContent` convention (`headlineContent`, `trailingContent`), matching Material 3. Use a bare noun (`title`, `actions`) only when the component name disambiguates.

6. **Put shared defaults in `XxxDefaults`**:
   ```kotlin
   object SettingsRowDefaults {
       @Composable fun Chevron() = Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null)
   }
   // Call site: trailingContent = { SettingsRowDefaults.Chevron() }
   ```

## When NOT to apply

- True single-use composables (one call site, no plan to reuse).
- Design-system primitives where every caller must look identical (`Heading2(text: String)`).
- Boolean parameters that are constraints, not content (`Switch(checked: Boolean)`).
