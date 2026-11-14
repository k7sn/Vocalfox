package com.vocalfox.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface VocalFoxDao {
    @Query("SELECT * FROM user_progress WHERE languageCode = :languageCode")
    fun observeProgressByLanguage(languageCode: String): Flow<List<UserProgressEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertProgress(entity: UserProgressEntity)

    @Query("SELECT * FROM mistake_srs WHERE languageCode = :languageCode ORDER BY nextReviewEpochMs ASC")
    fun observeSrsByLanguage(languageCode: String): Flow<List<MistakeSrsEntity>>

    @Query("SELECT * FROM mistake_srs WHERE itemKey = :itemKey LIMIT 1")
    suspend fun getSrsItem(itemKey: String): MistakeSrsEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertSrsItem(entity: MistakeSrsEntity)

    @Query("SELECT * FROM voice_model_config")
    fun observeVoiceConfigs(): Flow<List<VoiceModelConfigEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertVoiceConfig(entity: VoiceModelConfigEntity)
}
