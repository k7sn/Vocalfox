package com.vocalfox.app.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.math.PI
import kotlin.math.exp
import kotlin.math.sin

object VocalFoxSfxManager {
    private const val SAMPLE_RATE = 44100
    private const val PREFS_NAME = "vocalfox_prefs"
    private const val KEY_SFX_ENABLED = "sfx_enabled"

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private val isPlaying = AtomicBoolean(false)

    private val tileTapPcm: ShortArray by lazy {
        synthesizeChirp(startFreqHz = 520.0, endFreqHz = 690.0, durationMs = 44, amplitude = 0.22)
    }

    private val chatPopPcm: ShortArray by lazy {
        synthesizeChirp(startFreqHz = 640.0, endFreqHz = 880.0, durationMs = 52, amplitude = 0.20)
    }

    private val successPcm: ShortArray by lazy {
        synthesizeSequence(
            listOf(
                NoteSpec(freqHz = 523.25, durationMs = 85, amplitude = 0.26),
                NoteSpec(freqHz = 783.99, durationMs = 145, amplitude = 0.28)
            )
        )
    }

    private val errorPcm: ShortArray by lazy {
        synthesizeSequence(
            listOf(
                NoteSpec(freqHz = 260.0, durationMs = 90, amplitude = 0.24),
                NoteSpec(freqHz = 196.0, durationMs = 135, amplitude = 0.24)
            )
        )
    }

    private val unitCompletePcm: ShortArray by lazy {
        synthesizeSequence(
            listOf(
                NoteSpec(freqHz = 523.25, durationMs = 80, amplitude = 0.25),
                NoteSpec(freqHz = 659.25, durationMs = 80, amplitude = 0.25),
                NoteSpec(freqHz = 783.99, durationMs = 90, amplitude = 0.26),
                NoteSpec(freqHz = 1046.50, durationMs = 200, amplitude = 0.28)
            )
        )
    }

    fun isSfxEnabled(context: Context): Boolean {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getBoolean(KEY_SFX_ENABLED, true)
    }

    fun setSfxEnabled(context: Context, enabled: Boolean) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putBoolean(KEY_SFX_ENABLED, enabled).apply()
        if (enabled) {
            playSuccess(context)
        }
    }

    fun playTileTap(context: Context) {
        if (!isSfxEnabled(context)) return
        triggerAsync(tileTapPcm, 44, interruptible = true)
    }

    fun playChatPop(context: Context) {
        if (!isSfxEnabled(context)) return
        triggerAsync(chatPopPcm, 52, interruptible = true)
    }

    fun playSuccess(context: Context) {
        if (!isSfxEnabled(context)) return
        triggerAsync(successPcm, 230, interruptible = false)
    }

    fun playError(context: Context) {
        if (!isSfxEnabled(context)) return
        triggerAsync(errorPcm, 225, interruptible = false)
    }

    fun playUnitComplete(context: Context) {
        if (!isSfxEnabled(context)) return
        triggerAsync(unitCompletePcm, 450, interruptible = false)
    }

    private fun triggerAsync(pcm: ShortArray, durationMs: Int, interruptible: Boolean) {
        if (interruptible && isPlaying.get()) return
        scope.launch {
            playPcmSamples(pcm, durationMs)
        }
    }

    private data class NoteSpec(
        val freqHz: Double,
        val durationMs: Int,
        val amplitude: Double
    )

    private fun synthesizeChirp(
        startFreqHz: Double,
        endFreqHz: Double,
        durationMs: Int,
        amplitude: Double
    ): ShortArray {
        val totalSamples = (SAMPLE_RATE * durationMs) / 1000
        val out = ShortArray(totalSamples)
        val fadeSamples = (totalSamples * 0.18).toInt().coerceAtLeast(16)
        var phase = 0.0

        for (i in 0 until totalSamples) {
            val progress = i.toDouble() / totalSamples.toDouble()
            val freq = startFreqHz + (endFreqHz - startFreqHz) * progress
            phase += (2.0 * PI * freq) / SAMPLE_RATE

            val fadeIn = if (i < fadeSamples) i.toDouble() / fadeSamples else 1.0
            val fadeOut = if (i > totalSamples - fadeSamples) {
                (totalSamples - i).toDouble() / fadeSamples
            } else {
                1.0
            }
            val expDecay = exp(-2.8 * progress)
            val env = fadeIn * fadeOut * expDecay

            val wave = sin(phase) + 0.25 * sin(phase * 2.0)
            val sampleVal = (wave * 0.8 * amplitude * env).coerceIn(-1.0, 1.0)
            out[i] = (sampleVal * Short.MAX_VALUE).toInt().toShort()
        }
        return out
    }

    private fun synthesizeSequence(notes: List<NoteSpec>): ShortArray {
        val totalMs = notes.sumOf { it.durationMs }
        val totalSamples = (SAMPLE_RATE * totalMs) / 1000
        val out = ShortArray(totalSamples)
        var offset = 0

        for (note in notes) {
            val count = (SAMPLE_RATE * note.durationMs) / 1000
            val attack = (count * 0.12).toInt().coerceAtLeast(16)
            val release = (count * 0.22).toInt().coerceAtLeast(16)
            var phase = 0.0

            for (i in 0 until count) {
                val idx = offset + i
                if (idx >= totalSamples) break
                val progress = i.toDouble() / count.toDouble()
                phase += (2.0 * PI * note.freqHz) / SAMPLE_RATE

                val fadeIn = if (i < attack) i.toDouble() / attack else 1.0
                val fadeOut = if (i > count - release) (count - i).toDouble() / release else 1.0
                val decay = exp(-2.2 * progress)
                val env = fadeIn * fadeOut * decay

                val wave = sin(phase) + 0.30 * sin(phase * 2.0) + 0.10 * sin(phase * 3.0)
                val sampleVal = (wave * 0.72 * note.amplitude * env).coerceIn(-1.0, 1.0)
                out[idx] = (sampleVal * Short.MAX_VALUE).toInt().toShort()
            }
            offset += count
        }
        return out
    }

    private suspend fun playPcmSamples(pcm16: ShortArray, durationMs: Int) {
        if (pcm16.isEmpty()) return
        isPlaying.set(true)
        var track: AudioTrack? = null
        try {
            val byteSize = (pcm16.size * 2).coerceAtLeast(
                AudioTrack.getMinBufferSize(
                    SAMPLE_RATE,
                    AudioFormat.CHANNEL_OUT_MONO,
                    AudioFormat.ENCODING_PCM_16BIT
                )
            )
            track = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_ASSISTANCE_SONIFICATION)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(SAMPLE_RATE)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build()
                )
                .setBufferSizeInBytes(byteSize)
                .setTransferMode(AudioTrack.MODE_STATIC)
                .build()

            track.write(pcm16, 0, pcm16.size)
            track.play()
            delay(durationMs.toLong() + 35L)
        } catch (_: Throwable) {
        } finally {
            isPlaying.set(false)
            try {
                track?.stop()
                track?.release()
            } catch (_: Throwable) {}
        }
    }
}
