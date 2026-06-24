---
name: android-viewmodel-test
description: >
  Use when writing unit tests for Android ViewModels that expose StateFlow or
  SharedFlow using Turbine and kotlinx-coroutines-test. Triggered by: ViewModel
  test, test StateFlow, test SharedFlow, Turbine, test UiState, test UiEffect,
  viewModelScope, test coroutines.
tools:
  - Read
  - Edit
---

## Dependencies

1. Add to the module's `build.gradle.kts`:

```kotlin
testImplementation("app.cash.turbine:turbine:1.2.0")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
```

## Dispatcher setup

2. Replace the main dispatcher with `UnconfinedTestDispatcher` before each test — this makes `viewModelScope` coroutines run eagerly on the test thread.

```kotlin
@BeforeEach
fun setUp() {
    Dispatchers.setMain(UnconfinedTestDispatcher())
}

@AfterEach
fun tearDown() {
    Dispatchers.resetMain()
}
```

3. Use `StandardTestDispatcher` instead when testing time-sensitive behavior (delays, retries, polling). With it, coroutines do not run until you advance time manually.

## Testing StateFlow (UiState)

4. Wrap assertions in `runTest { }` — never `runBlocking`.
5. Open a Turbine collector with `.test { }` and call `awaitItem()` for each expected emission:

```kotlin
@Test
fun `initial state is empty and not loading`() = runTest {
    viewModel.uiState.test {
        val initial = awaitItem()
        assertThat(initial.isLoading).isFalse()
        assertThat(initial.items).isEmpty()
        cancelAndIgnoreRemainingEvents()
    }
}
```

6. Assert state transitions in order using successive `awaitItem()` calls:

```kotlin
@Test
fun `refresh emits loading then success`() = runTest {
    viewModel.uiState.test {
        awaitItem()                                          // initial
        viewModel.onEvent(UiEvent.Refresh)
        assertThat(awaitItem().isLoading).isTrue()           // loading
        val done = awaitItem()
        assertThat(done.isLoading).isFalse()
        assertThat(done.items).isNotEmpty()
        cancelAndIgnoreRemainingEvents()
    }
}
```

7. Call `cancelAndIgnoreRemainingEvents()` to end the collector unless you want to assert no further emissions — use `expectNoEvents()` for that stricter check.

## Testing SharedFlow (UiEffect)

8. Start collecting the `SharedFlow` **before** triggering the action — `SharedFlow` with `replay = 0` drops emissions that arrive before a collector is active.

```kotlin
@Test
fun `refresh failure emits ShowError effect`() = runTest {
    coEvery { repository.getItems() } throws IOException()

    viewModel.uiEffect.test {                          // collector active first
        viewModel.onEvent(UiEvent.Refresh)
        val effect = awaitItem()
        assertThat(effect).isInstanceOf(UiEffect.ShowError::class.java)
        cancelAndIgnoreRemainingEvents()
    }
}
```

## Time control with StandardTestDispatcher

9. Inject the dispatcher into the ViewModel under test so you control the clock:

```kotlin
private val testDispatcher = StandardTestDispatcher()

@BeforeEach
fun setUp() {
    Dispatchers.setMain(testDispatcher)
    viewModel = MyViewModel(repository, testDispatcher)
}
```

10. After triggering an event, call `advanceUntilIdle()` to drain all pending coroutines before asserting:

```kotlin
viewModel.onEvent(UiEvent.Refresh)
advanceUntilIdle()
assertThat(viewModel.uiState.value.isLoading).isFalse()
```

11. Use `advanceTimeBy(millis)` to step through delays without running the entire clock:

```kotlin
advanceTimeBy(5_000)   // step past a 5-second retry delay
runCurrent()           // execute coroutines now scheduled
```

## What to mock

12. Mock repositories or use-cases injected into the ViewModel — test ViewModel logic, not collaborators.
13. Inject mocks via the ViewModel's constructor; do not use a service locator or `Dispatchers.IO` overrides inside production code that can't be swapped in tests.
