---
name: android-datastore
description: >
  Use when persisting lightweight settings or typed structured data in Android using
  Jetpack DataStore. Triggered by: DataStore, PreferencesDataStore, Proto DataStore,
  persistent settings, user preferences, prefs migration.
tools:
  - Read
  - Edit
---

## Preferences DataStore — setup

1. Declare one DataStore instance per file using the `preferencesDataStore` delegate at the top level — never inside a class body.

```kotlin
private val Context.dataStore by preferencesDataStore(name = "settings")
```

2. Define keys as top-level constants using typed factories:

```kotlin
private val THEME_KEY = stringPreferencesKey("theme")
private val NOTIFICATIONS_ENABLED_KEY = booleanPreferencesKey("notifications_enabled")
```

## Reading preferences

3. Read with `dataStore.data.map { prefs -> prefs[KEY] ?: defaultValue }` — returns `Flow<T>`, never blocks.
4. Guard against `IOException` with `.catch`:

```kotlin
val themeFlow: Flow<String> = context.dataStore.data
    .catch { e -> if (e is IOException) emit(emptyPreferences()) else throw e }
    .map { prefs -> prefs[THEME_KEY] ?: "system" }
```

5. For one-shot reads outside a collector, use `dataStore.data.first()` inside `withContext(Dispatchers.IO)` — never on the main thread.

## Writing preferences

6. Write inside `dataStore.edit` — it is a `suspend` function; call from a coroutine or `viewModelScope`.

```kotlin
suspend fun setTheme(theme: String) {
    context.dataStore.edit { prefs -> prefs[THEME_KEY] = theme }
}
```

## Dependency injection (Hilt)

7. Provide as a `@Singleton`; inject into a repository or use-case, not directly into a ViewModel.

```kotlin
@Provides
@Singleton
fun provideDataStore(@ApplicationContext ctx: Context): DataStore<Preferences> =
    ctx.dataStore
```

## Proto DataStore

8. Use Proto DataStore when data has a fixed typed schema. Add `androidx.datastore:datastore` (not the `-preferences` variant) and the protobuf Gradle plugin.
9. Implement `Serializer<T>` with `defaultValue`, `readFrom`, and `writeTo`; register it in `DataStoreFactory.create`.
10. Supply migrations via `DataMigration<T>` in the `migrations = listOf(...)` parameter of the factory.

## Scope and limits

11. For multi-process access, add the `androidx.datastore:datastore-multiprocess` artifact and use `MultiProcessDataStore`.
12. For relational or large binary data, use Room — DataStore is for lightweight key-value and typed proto only.
13. Migrate from SharedPreferences in one go using `SharedPreferencesMigration`; once migrated, remove all SharedPreferences reads for that key.
