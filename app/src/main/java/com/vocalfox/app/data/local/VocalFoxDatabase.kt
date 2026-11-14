package com.vocalfox.app.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [
        UserProgressEntity::class,
        MistakeSrsEntity::class,
        VoiceModelConfigEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class VocalFoxDatabase : RoomDatabase() {
    abstract fun dao(): VocalFoxDao

    companion object {
        @Volatile
        private var INSTANCE: VocalFoxDatabase? = null

        fun getInstance(context: Context): VocalFoxDatabase {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    VocalFoxDatabase::class.java,
                    "vocalfox_offline.db"
                ).fallbackToDestructiveMigration().build().also { INSTANCE = it }
            }
        }
    }
}
