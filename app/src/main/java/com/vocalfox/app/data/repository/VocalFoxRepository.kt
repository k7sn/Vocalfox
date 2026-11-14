package com.vocalfox.app.data.repository

import com.vocalfox.app.data.local.MistakeSrsEntity
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.data.local.VocalFoxDao
import com.vocalfox.app.data.local.VoiceModelConfigEntity
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import kotlinx.coroutines.flow.Flow
import kotlin.math.max

class VocalFoxRepository(
    private val dao: VocalFoxDao,
    private val packLoader: PackLoader
) {
    private val cachedPacks: Map<String, LanguagePack> by lazy {
        try {
            packLoader.loadAllLanguagePacks()
        } catch (_: Throwable) {
            mapOf("es" to PackLoader.createEmergencyPack())
        }
    }

    fun getAllPacks(): Map<String, LanguagePack> = cachedPacks

    fun getPack(languageCode: String): LanguagePack {
        return cachedPacks[languageCode]
            ?: cachedPacks.values.firstOrNull()
            ?: PackLoader.createEmergencyPack()
    }

    fun observeProgress(languageCode: String): Flow<List<UserProgressEntity>> =
        dao.observeProgressByLanguage(languageCode)

    fun observeSrsItems(languageCode: String): Flow<List<MistakeSrsEntity>> =
        dao.observeSrsByLanguage(languageCode)

    fun observeVoiceConfigs(): Flow<List<VoiceModelConfigEntity>> =
        dao.observeVoiceConfigs()

    suspend fun recordExerciseOutcome(
        itemKey: String,
        languageCode: String,
        cefrLevel: CefrLevel,
        pillar: String,
        score: Int,
        promptPreview: String,
        targetAnswer: String,
        mistakeNote: String
    ) {
        dao.upsertProgress(
            UserProgressEntity(
                itemKey = itemKey,
                languageCode = languageCode,
                cefrLevel = cefrLevel.name,
                pillar = pillar,
                bestScore = score,
                attempts = 1,
                completedAtEpochMs = System.currentTimeMillis()
            )
        )

        val quality = when {
            score >= 90 -> 5
            score >= 80 -> 4
            score >= 65 -> 3
            score >= 45 -> 2
            else -> 1
        }

        val existingSrs = dao.getSrsItem(itemKey)
        val updatedSrs = Sm2Scheduler.scheduleNext(
            existing = existingSrs,
            itemKey = itemKey,
            languageCode = languageCode,
            cefrLevel = cefrLevel.name,
            promptPreview = promptPreview,
            targetAnswer = targetAnswer,
            quality = max(1, quality),
            mistakeNote = mistakeNote
        )
        dao.upsertSrsItem(updatedSrs)
    }

    suspend fun saveVoiceConfig(
        languageCode: String,
        voiceId: String,
        speed: Float,
        verified: Boolean
    ) {
        dao.upsertVoiceConfig(
            VoiceModelConfigEntity(
                languageCode = languageCode,
                selectedVoiceId = voiceId,
                preferredSpeed = speed,
                isOfflinePackVerified = verified
            )
        )
    }
}
