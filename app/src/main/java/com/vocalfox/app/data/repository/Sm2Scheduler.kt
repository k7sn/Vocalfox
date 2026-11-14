package com.vocalfox.app.data.repository

import com.vocalfox.app.data.local.MistakeSrsEntity
import kotlin.math.max
import kotlin.math.roundToInt

/**
 * SuperMemo-2 (SM-2) Spaced Repetition Scheduler for weak words, grammar rules, and phonemes.
 * Quality rating `q` ranges from 0 (total failure) to 5 (flawless recall / >=90% pronunciation).
 */
object Sm2Scheduler {
    private const val DAY_MS = 86_400_000L

    fun scheduleNext(
        existing: MistakeSrsEntity?,
        itemKey: String,
        languageCode: String,
        cefrLevel: String,
        promptPreview: String,
        targetAnswer: String,
        quality: Int,
        mistakeNote: String,
        nowMs: Long = System.currentTimeMillis()
    ): MistakeSrsEntity {
        val q = quality.coerceIn(0, 5)
        val prevReps = existing?.repetitions ?: 0
        val prevInterval = existing?.intervalDays ?: 0
        val prevEf = existing?.easeFactor ?: 2.5f

        val newReps: Int
        val newInterval: Int

        if (q < 3) {
            newReps = 0
            newInterval = 1
        } else {
            newReps = prevReps + 1
            newInterval = when (newReps) {
                1 -> 1
                2 -> 6
                else -> (prevInterval * prevEf).roundToInt().coerceAtLeast(1)
            }
        }

        val efDelta = 0.1f - (5 - q) * (0.08f + (5 - q) * 0.02f)
        val newEf = max(1.3f, prevEf + efDelta)

        return MistakeSrsEntity(
            itemKey = itemKey,
            languageCode = languageCode,
            cefrLevel = cefrLevel,
            promptPreview = promptPreview,
            targetAnswer = targetAnswer,
            repetitions = newReps,
            intervalDays = newInterval,
            easeFactor = newEf,
            nextReviewEpochMs = nowMs + newInterval * DAY_MS,
            lastMistakeNote = mistakeNote
        )
    }
}
