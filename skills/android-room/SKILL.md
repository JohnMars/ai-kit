---
name: android-room
description: >
  Use when defining Room entities, DAOs, or a RoomDatabase, running database queries,
  or writing migrations in Android. Triggered by: Room, @Entity, @Dao, @Database,
  SQLite, migration, TypeConverter, database query.
tools:
  - Read
  - Edit
---

## Entity

1. Annotate data classes with `@Entity(tableName = "items")`.
2. Mark the primary key with `@PrimaryKey(autoGenerate = true) val id: Int = 0`.
3. Use `@ColumnInfo(name = "column_name")` only when the DB column name differs from the field name.
4. Keep entities flat — no nested objects without a registered `TypeConverter`.

## DAO

5. Annotate the interface with `@Dao`.
6. Return `Flow<T>` from `@Query` for observable data; `suspend` for one-shot reads and all writes.
7. Prefer `@Upsert` (Room 2.5+) over `@Insert(onConflict = OnConflictStrategy.REPLACE)`.
8. No business logic inside a DAO — queries only.

```kotlin
@Dao
interface ItemDao {
    @Query("SELECT * FROM items ORDER BY created_at DESC")
    fun observeAll(): Flow<List<ItemEntity>>

    @Query("SELECT * FROM items WHERE id = :id")
    suspend fun getById(id: Int): ItemEntity?

    @Upsert
    suspend fun upsert(item: ItemEntity)

    @Delete
    suspend fun delete(item: ItemEntity)
}
```

## Database class

9. Annotate with `@Database(entities = [ItemEntity::class], version = 1, exportSchema = true)`.
10. Extend `RoomDatabase()`. Declare each DAO as an abstract function.
11. Set `exportSchema = true` and commit the generated `schemas/` directory — required for migration testing.

```kotlin
@Database(entities = [ItemEntity::class], version = 1, exportSchema = true)
abstract class AppDatabase : RoomDatabase() {
    abstract fun itemDao(): ItemDao
}
```

## Initialization

12. Build exactly one instance per process — use `@Singleton` in Hilt or a `companion object`.
13. Use `.fallbackToDestructiveMigration(false)` during development; replace with explicit migrations before release.

```kotlin
@Provides
@Singleton
fun provideDatabase(@ApplicationContext ctx: Context): AppDatabase =
    Room.databaseBuilder(ctx, AppDatabase::class.java, "app.db")
        .fallbackToDestructiveMigration(false)
        .build()
```

## Type converters

14. Register with `@TypeConverters(MyConverters::class)` on the `@Database` class.
15. Each converter must be stateless with matching `@TypeConverter` functions for both directions (to DB type and from DB type).

## Migrations

16. Increment `version` by exactly 1 per schema change.
17. Write an explicit `Migration(from, to)` object with raw SQL; register it with `.addMigrations(MIGRATION_1_2)`.
18. Test migrations with `MigrationTestHelper` from `androidx.room:room-testing` — run against the exported schema JSON.
