package com.vocalfox.app.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "user_progress")
data class UserProgressEntity(
    @PrimaryKey val itemKey: String, // e.g. "de_B2_syn_1"
    val languageCode: String,
    val cefrLevel: String,
    val pillar: String, // "SYNTAX", "WRITING", "SPEECH"
    val bestScore: Int,
    val attempts: Int,
    val completedAtEpochMs: Long
)

@Entity(tableName = "mistake_srs")
data class MistakeSrsEntity(
    @PrimaryKey val itemKey: String,
    val languageCode: String,
    val cefrLevel: String,
    val promptPreview: String,
    val targetAnswer: String,
    val repetitions: Int,
    val intervalDays: Int,
    val easeFactor: Float,
    val nextReviewEpochMs: Long,
    val lastMistakeNote: String
)

@Entity(tableName = "voice_model_config")
data class VoiceModelConfigEntity(
    @PrimaryKey val languageCode: String,
    val selectedVoiceId: String,
    val preferredSpeed: Float,
    val isOfflinePackVerified: Boolean
)
