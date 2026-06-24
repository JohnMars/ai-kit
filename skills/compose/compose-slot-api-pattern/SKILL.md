---
name: compose-slot-api-pattern
description: >
  Use when designing or reviewing a reusable Jetpack Compose component that accepts
  variable content from callers. Triggered by: "slot API", "composable lambda parameter",
  "@Composable () -> Unit parameter", "content lambda", "RowScope content",
  "trailing composable", "XxxDefaults object", "optional content slot".
tools:
  - Read
  - Edit
---

## Core rule

Replace primitive content parameters (`title: String`, `icon: ImageVector`) with `@Composable () -> Unit` slots. The component owns structure; the caller owns content.

## Rules

1. Replace primitive content params with composable slots:
   ```kotlin
   // ❌ primitives lock content shape
   fun SettingsRow(title: String, leadingIcon: ImageVector?, subtitle: String?)

   // ✅ caller provides any content
   fun SettingsRow(
       headlineContent: @Composable () -> Unit,
       modifier: Modifier = Modifier,
       leadingContent: (@Composable () -> Unit)? = null,
       supportingContent: (@Composable () -> Unit)? = null,
       trailingContent: (@Composable () -> Unit)? = null,
   )
   ```

2. Replace boolean shape flags (`showChevron: Boolean`, `mode: RowMode`) with a nullable `@Composable` slot — the caller passes `null` to omit, or provides content to show.

3. Use `null` default (not `{}`) for optional slots — lets the component skip layout and spacing when absent:
   ```kotlin
   leadingContent: (@Composable () -> Unit)? = null  // ✅ component branches on null
   leadingContent: @Composable () -> Unit = {}        // ❌ always allocated, can't skip spacing
   ```

4. Add a scope receiver when the slot renders inside a layout scope:
   ```kotlin
   actions: @Composable RowScope.() -> Unit = {}   // inside a Row
   content: @Composable BoxScope.() -> Unit         // inside a Box
   ```

5. Name slots with the `xxxContent` convention (`headlineContent`, `trailingContent`), matching Material 3. Use a bare noun (`title`, `actions`) only when the component name disambiguates.

6. Provide shared defaults in an `XxxDefaults` object:
   ```kotlin
   object SettingsRowDefaults {
       @Composable fun Chevron() = Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null)
   }
   // Caller: trailingContent = { SettingsRowDefaults.Chevron() }
   ```

## When NOT to apply

- Single-use composables (one call site, not shared).
- Design-system primitives where all callers must look identical (`Heading2(text: String)`).
- Boolean parameters that are constraints, not content (`Switch(checked: Boolean, onCheckedChange: ...)`).
- Components used in fewer than 3 places with no plans for reuse.
