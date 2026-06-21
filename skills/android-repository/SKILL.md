---
name: android-repository
description: >
  Use when implementing data access in Android following the repository pattern
  with separate remote and local data sources. Triggered by: "repository", "data source",
  "fetch from API", "cache data", "Room", "Retrofit", "offline-first", "sync".
tools:
  - Read
  - Edit
---

## Layer structure

1. **Domain layer** — `Repository` interface only. No Android imports, no framework types.
2. **Data layer** — `RemoteDataSource` interface + impl, `LocalDataSource` interface + impl, `RepositoryImpl`.
3. Inject both data sources into `RepositoryImpl` via constructor. Never instantiate them inside.

## Remote data source

4. Wrap Retrofit service calls — one method per endpoint.
5. All methods are `suspend`. No RxJava, no callbacks.
6. Map network DTOs → domain models before returning. DTOs never leave the data layer.
7. Let network exceptions propagate to the repository — do not swallow here.

## Local data source

8. Wrap Room DAOs or DataStore.
9. Return `Flow<T>` for observable queries, `suspend` for one-shot reads/writes.
10. Map database entities → domain models before returning. Entities never leave the data layer.

## Repository implementation

11. Local DB is the single source of truth — the repository never returns raw remote data directly.
12. Offline-first pattern:
    ```kotlin
    override fun getItems(): Flow<List<Item>> = localDataSource.observeItems()
        .onStart { refreshFromRemote() }

    private suspend fun refreshFromRemote() = withContext(Dispatchers.IO) {
        runCatching { remoteDataSource.fetchItems() }
            .onSuccess { localDataSource.saveItems(it) }
            .onFailure { /* log or emit error */ }
    }
    ```
13. Expose errors through `Result<T>` (Kotlin stdlib) or a sealed `DataResult`. Never swallow silently.
14. Wrap all data source calls in `withContext(Dispatchers.IO)` unless already on the correct dispatcher.

## Naming conventions

15. Interfaces: `ItemRepository`, `ItemRemoteDataSource`, `ItemLocalDataSource`.
16. Implementations: `ItemRepositoryImpl`, `RetrofitItemRemoteDataSource`, `RoomItemLocalDataSource`.
