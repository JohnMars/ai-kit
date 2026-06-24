---
name: android-paparazzi
description: >
  Use when writing snapshot tests for Jetpack Compose UI using Paparazzi. Triggered
  by: Paparazzi, snapshot test, screenshot test, compose snapshot, golden image,
  recordPaparazzi, verifyPaparazzi, visual regression.
tools:
  - Read
  - Edit
---

## Setup

1. Apply the Gradle plugin — no extra `testImplementation` needed, the plugin adds dependencies automatically.

In `libs.versions.toml`:
```toml
[versions]
paparazzi = "1.3.5"

[plugins]
paparazzi = { id = "app.cash.paparazzi", version.ref = "paparazzi" }
```

In the module's `build.gradle.kts`:
```kotlin
plugins {
    alias(libs.plugins.paparazzi)
}
```

## Basic snapshot test

2. Declare a `Paparazzi` JUnit4 rule and call `snapshot { }` with your composable:

```kotlin
class MyComposableTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun `renders correctly`() {
        paparazzi.snapshot {
            MyComposable(title = "Hello", onClick = {})
        }
    }
}
```

3. Always wrap the composable in your app's design system theme inside the `snapshot` block — Paparazzi provides no theme by default.
4. One visual state per test method — do not snapshot multiple states inside a single `snapshot { }` call.

## Device configuration

5. Pass a `DeviceConfig` to the rule constructor to control screen dimensions and density:

```kotlin
@get:Rule
val paparazzi = Paparazzi(
    deviceConfig = DeviceConfig.PIXEL_5,
)
```

6. For multiple device sizes, create a separate test class per config or use JUnit4 `@RunWith(Parameterized::class)`.

## Theme and dark mode

7. Test light and dark variants in separate test methods:

```kotlin
@Test
fun `light theme`() {
    paparazzi.snapshot {
        MaterialTheme(colorScheme = lightColorScheme()) { MyComposable() }
    }
}

@Test
fun `dark theme`() {
    paparazzi.snapshot {
        MaterialTheme(colorScheme = darkColorScheme()) { MyComposable() }
    }
}
```

## Composable isolation

8. Test composables with hardcoded fake data — no ViewModels, no repositories, no real data sources.
9. Cover each meaningful visual state as its own test: loading, empty, error, populated, disabled.
10. Provide composition locals (`LocalContext`, `LocalDensity`, etc.) via `CompositionLocalProvider` when the composable reads them — never rely on a real Android context for rendering.

## Recording and verifying

11. Record golden images locally before the first CI run:
```
./gradlew recordPaparazziDebug
```

12. Verify against goldens in CI — this is the task that fails the build on visual drift:
```
./gradlew verifyPaparazziDebug
```

13. Commit the generated `src/test/snapshots/images/` directory — goldens are the source of truth and must live in version control.
14. Re-record after intentional UI changes (`recordPaparazziDebug`), then commit the updated PNGs in the same PR as the UI change. Never manually edit PNG files.

## Scope and limits

15. Paparazzi renders on the JVM without a device or emulator — it captures a static frame, not behavior. Gestures, animations, and navigation belong in instrumented tests.
16. System fonts and locale-sensitive resources can differ between machines; pin `fontScale` and use string resources rather than hardcoded strings to keep goldens reproducible across environments.
