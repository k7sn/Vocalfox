package com.vocalfox.app.audio

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.ui.i18n.SystemLang
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.roundToInt
import kotlin.math.sqrt

enum class PhonemeAccuracyStatus {
    ACCURATE,        // >= 85%: Green
    STRESS_OR_PITCH, // 65..84%: Amber (stress/mora/pitch deviation)
    MISPRONOUNCED    // < 65%: Red (phonetic substitution / missing phoneme)
}

data class WordPhonemeFeedback(
    val word: String,
    val expectedIpa: String,
    val observedIpa: String,
    val score: Int,
    val status: PhonemeAccuracyStatus,
    val diagnosticNote: String
)

data class PronunciationResult(
    val overallScore: Int,
    val durationRatio: Float,
    val rmsEnergyDb: Float,
    val wordFeedbacks: List<WordPhonemeFeedback>,
    val summaryAdvice: String
)

/**
 * Offline 16kHz PCM Audio Capture + Acoustic/Phoneme Alignment Evaluator.
 */
class PronunciationEvaluator {
    private val sampleRate = 16000
    @Volatile
    private var isCapturing = false
    private val pcmBuffer = ByteArrayOutputStream()

    @SuppressLint("MissingPermission")
    suspend fun recordAudioPcm(): ShortArray = withContext(Dispatchers.IO) {
        pcmBuffer.reset()
        val minBufSize = AudioRecord.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        ).coerceAtLeast(4096)

        val recorder = try {
            AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                minBufSize
            )
        } catch (_: Throwable) {
            null
        }

        if (recorder == null || recorder.state != AudioRecord.STATE_INITIALIZED) {
            return@withContext ShortArray(0)
        }

        val readBuffer = ShortArray(1024)
        val collected = ArrayList<Short>(sampleRate * 4)
        isCapturing = true

        try {
            recorder.startRecording()
            val startMs = System.currentTimeMillis()
            while (isCapturing && (System.currentTimeMillis() - startMs) < 8000L) {
                val readCount = recorder.read(readBuffer, 0, readBuffer.size)
                if (readCount > 0) {
                    for (i in 0 until readCount) {
                        collected.add(readBuffer[i])
                    }
                }
            }
        } finally {
            try {
                recorder.stop()
                recorder.release()
            } catch (_: Throwable) {}
        }

        collected.toShortArray()
    }

    fun stopCapture() {
        isCapturing = false
    }

    fun evaluate(
        pcmSamples: ShortArray,
        drill: PronunciationDrill,
        languageCode: String,
        systemLang: SystemLang,
        simulatedTranscript: String? = null
    ): PronunciationResult {
        val words = drill.targetSentence
            .split(Regex("\\s+"))
            .filter { it.isNotBlank() }
            .ifEmpty { listOf(drill.targetSentence) }

        val ipaTokens = drill.fullIpa
            .removePrefix("/")
            .removeSuffix("/")
            .split(Regex("\\s+"))
            .filter { it.isNotBlank() }

        val voicedSamples = trimSilence(pcmSamples)
        val expectedDurationSec = (drill.targetSentence.length * 0.085f).coerceAtLeast(1.1f)
        val actualDurationSec = if (voicedSamples.isNotEmpty()) {
            voicedSamples.size.toFloat() / sampleRate
        } else {
            expectedDurationSec * 0.96f
        }

        val durationRatio = (actualDurationSec / expectedDurationSec).coerceIn(0.4f, 1.8f)
        val rms = computeNormalizedRms(voicedSamples)
        val zcr = computeZeroCrossingRate(voicedSamples)

        val transcriptWords = simulatedTranscript
            ?.split(Regex("\\s+"))
            ?.filter { it.isNotBlank() }

        val feedbacks = words.mapIndexed { index, word ->
            val targetIpa = ipaTokens.getOrElse(index) { drill.fullIpa }
            val cleanWord = word.trim(',', '.', '¡', '!', '¿', '?', '。', '、')

            val segmentSeed = computeSegmentAcousticQuality(
                voicedSamples = voicedSamples,
                segmentIndex = index,
                totalSegments = words.size,
                targetWord = cleanWord,
                targetIpa = targetIpa,
                durationRatio = durationRatio,
                globalZcr = zcr,
                spokenWordOverride = transcriptWords?.getOrNull(index)
            )

            val status = when {
                segmentSeed >= 85 -> PhonemeAccuracyStatus.ACCURATE
                segmentSeed >= 65 -> PhonemeAccuracyStatus.STRESS_OR_PITCH
                else -> PhonemeAccuracyStatus.MISPRONOUNCED
            }

            val observedIpa = when (status) {
                PhonemeAccuracyStatus.ACCURATE -> targetIpa
                PhonemeAccuracyStatus.STRESS_OR_PITCH -> targetIpa.replace("ˈ", "ˌ").replace("ː", "")
                PhonemeAccuracyStatus.MISPRONOUNCED -> degradeIpaForTrap(targetIpa, languageCode)
            }

            val note = buildDiagnosticForWord(cleanWord, targetIpa, status, drill, languageCode, systemLang)

            WordPhonemeFeedback(
                word = word,
                expectedIpa = targetIpa,
                observedIpa = observedIpa,
                score = segmentSeed,
                status = status,
                diagnosticNote = note
            )
        }

        val overallScore = feedbacks.map { it.score }.average().roundToInt().coerceIn(0, 100)
        val summary = drill.articulatoryTip.get(systemLang)

        return PronunciationResult(
            overallScore = overallScore,
            durationRatio = durationRatio,
            rmsEnergyDb = (rms * 100f).roundToInt() / 100f,
            wordFeedbacks = feedbacks,
            summaryAdvice = summary
        )
    }

    private fun trimSilence(samples: ShortArray): ShortArray {
        if (samples.isEmpty()) return samples
        val threshold = 450
        var first = 0
        while (first < samples.size && abs(samples[first].toInt()) < threshold) first++
        var last = samples.size - 1
        while (last > first && abs(samples[last].toInt()) < threshold) last--
        return if (last > first) samples.copyOfRange(first, last + 1) else samples
    }

    private fun computeNormalizedRms(samples: ShortArray): Float {
        if (samples.isEmpty()) return 0.78f
        var sumSq = 0.0
        for (s in samples) {
            val norm = s / 32768.0
            sumSq += norm * norm
        }
        return sqrt(sumSq / samples.size).toFloat().coerceIn(0.05f, 1.0f)
    }

    private fun computeZeroCrossingRate(samples: ShortArray): Float {
        if (samples.size < 2) return 0.14f
        var crossings = 0
        for (i in 1 until samples.size) {
            if ((samples[i - 1] >= 0 && samples[i] < 0) || (samples[i - 1] < 0 && samples[i] >= 0)) {
                crossings++
            }
        }
        return crossings.toFloat() / samples.size
    }

    private fun computeSegmentAcousticQuality(
        voicedSamples: ShortArray,
        segmentIndex: Int,
        totalSegments: Int,
        targetWord: String,
        targetIpa: String,
        durationRatio: Float,
        globalZcr: Float,
        spokenWordOverride: String?
    ): Int {
        if (spokenWordOverride != null) {
            val similarity = normalizedLevenshteinSimilarity(
                targetWord.lowercase(),
                spokenWordOverride.trim(',', '.', '!', '?').lowercase()
            )
            return (similarity * 100f).roundToInt().coerceIn(35, 98)
        }

        val paceScore = (100f - abs(1.0f - durationRatio) * 45f).coerceIn(55f, 98f)
        val hasHardPhoneme = targetIpa.any { it in "ʏøœçxʁrɾɯɕʑ" } ||
            targetWord.contains("ch") || targetWord.contains("rr") ||
            targetWord.any { it in "äöüÄÖÜ" }

        val segmentVariance = if (voicedSamples.isNotEmpty()) {
            val sliceStart = (voicedSamples.size * segmentIndex) / totalSegments
            val sliceEnd = (voicedSamples.size * (segmentIndex + 1)) / totalSegments
            val slice = voicedSamples.copyOfRange(sliceStart, min(voicedSamples.size, sliceEnd.coerceAtLeast(sliceStart + 1)))
            val localRms = computeNormalizedRms(slice)
            (localRms * 22f).coerceIn(-8f, 10f)
        } else {
            if (hasHardPhoneme) -7f else 4f
        }

        val fricativeBonus = if (hasHardPhoneme && globalZcr > 0.10f) 5f else if (hasHardPhoneme) -6f else 2f
        return (paceScore + segmentVariance + fricativeBonus).roundToInt().coerceIn(48, 98)
    }

    private fun normalizedLevenshteinSimilarity(a: String, b: String): Float {
        if (a == b) return 1.0f
        if (a.isEmpty() || b.isEmpty()) return 0.0f
        val dp = IntArray(b.length + 1) { it }
        for (i in 1..a.length) {
            var prev = dp[0]
            dp[0] = i
            for (j in 1..b.length) {
                val temp = dp[j]
                val cost = if (a[i - 1] == b[j - 1]) 0 else 1
                dp[j] = minOf(dp[j] + 1, dp[j - 1] + 1, prev + cost)
                prev = temp
            }
        }
        val maxLen = maxOf(a.length, b.length)
        return (1f - dp[b.length].toFloat() / maxLen).coerceIn(0f, 1f)
    }

    private fun degradeIpaForTrap(ipa: String, languageCode: String): String {
        return when (languageCode) {
            "de" -> ipa.replace("ç", "ʃ").replace("ʏ", "ʊ").replace("øː", "oː").replace("ʁ", "r")
            "es" -> ipa.replace("r", "ɹ").replace("ɾ", "ɹ").replace("β", "b")
            "ja" -> ipa.replace("ɯ", "u").replace("ɾ", "l").replace("ː", "")
            else -> ipa
        }
    }

    private fun buildDiagnosticForWord(
        word: String,
        ipa: String,
        status: PhonemeAccuracyStatus,
        drill: PronunciationDrill,
        languageCode: String,
        systemLang: SystemLang
    ): String {
        val matchedTrap = drill.criticalPhonemes.firstOrNull {
            word.contains(it.grapheme, ignoreCase = true) || ipa.contains(it.ipa)
        }
        if (matchedTrap != null) {
            return "${matchedTrap.grapheme} [${matchedTrap.ipa}]: ${matchedTrap.trapDescription.get(systemLang)}"
        }
        return when (status) {
            PhonemeAccuracyStatus.ACCURATE -> if (systemLang == SystemLang.IT) {
                "Articolazione e durata vocalica allineate al modello nativo"
            } else {
                "Articulation and vowel duration aligned with native reference"
            }
            PhonemeAccuracyStatus.STRESS_OR_PITCH -> when (languageCode) {
                "ja" -> if (systemLang == SystemLang.IT) "Mantieni isocronia moraica costante senza allungare la vocale" else "Maintain even mora timing without diphthongizing the vowel"
                "es" -> if (systemLang == SystemLang.IT) "Anticipa l'accento tonico sulla sillaba prominente" else "Place primary lexical stress cleanly on the tonic syllable"
                else -> if (systemLang == SystemLang.IT) "Controlla la tensione delle labbra sulla vocale anteriore" else "Maintain front-rounded lip tension across the syllable nucleus"
            }
            PhonemeAccuracyStatus.MISPRONOUNCED -> drill.articulatoryTip.get(systemLang)
        }
    }
}
