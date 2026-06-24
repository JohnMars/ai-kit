---
name: android-junit5
description: >
  Use when writing Android unit tests with JUnit5 and MockK following
  GIVEN / WHEN / THEN structure. Triggered by: "unit test", "write a test",
  "test this", "JUnit5", "mockk", "mock", "spec", "should".
tools:
  - Read
  - Edit
---

## Test structure

1. Follow GIVEN / WHEN / THEN blocks as comments. GIVEN is optional when no setup is needed.
2. Name tests with backtick syntax reflecting the scenario:
   ```kotlin
   @Test
   fun `given empty list when refresh called then loading state emitted`() { }
   ```
3. One behavior per test — split unrelated assertions into separate tests.

## MockK setup

4. Declare mocks with `@MockK` at the class level, initialize in `@BeforeEach`:
   ```kotlin
   @BeforeEach
   fun setUp() { MockKAnnotations.init(this) }
   ```
5. Use `mockk<Type>(relaxed = true)` when only specific interactions matter.
6. Use `mockk<Type>(relaxUnitFun = true)` to relax only `Unit`-returning functions.

## Stubbing

7. `every { mock.method() } returns value` — stub a regular function.
8. `coEvery { mock.suspendMethod() } returns value` — stub a suspend function.
9. `every { mock.method() } answers { firstArg() }` — derive return from arguments.
10. `justRun { mock.voidMethod() }` — stub a Unit-returning function with no behavior.
11. `every { mock.method() } throws SomeException()` — stub an exception.

## Verification

12. `verify { mock.method() }` — assert an interaction happened (after WHEN).
13. `coVerify { mock.suspendMethod() }` — for suspend functions.
14. `verify(exactly = 0) { mock.method() }` — assert an interaction did NOT happen.
15. Only verify interactions that are part of the test contract — not every mock call.

## Coroutines and Flow

16. Wrap suspending tests in `runTest { }` from `kotlinx-coroutines-test`.
17. In `@BeforeEach`, set `Dispatchers.setMain(UnconfinedTestDispatcher())`; reset in `@AfterEach`.
18. Test Flow with Turbine:
    ```kotlin
    viewModel.uiState.test {
        // GIVEN state is loaded
        // WHEN
        viewModel.onEvent(UiEvent.Refresh)
        // THEN
        assertEquals(expected, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
    ```
