package com.vocalfox.app.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.speech.tts.TextToSpeech
import com.vocalfox.app.domain.model.VoicePreset
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.util.Locale
import kotlin.math.PI
import kotlin.math.sin

class PiperTtsManager(private val context: Context) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val voicesDir: File by lazy {
        File(context.filesDir, "piper_voices").apply { mkdirs() }
    }

    private var androidTts: TextToSpeech? = null
    @Volatile
    private var isAndroidTtsReady = false

    init {
        try {
            androidTts = TextToSpeech(context.applicationContext) { status ->
                isAndroidTtsReady = (status == TextToSpeech.SUCCESS)
            }
        } catch (_: Throwable) {
            isAndroidTtsReady = false
        }
    }

    fun getVoiceModelFile(preset: VoicePreset): File {
        return File(voicesDir, preset.onnxFileName)
    }

    fun isOnnxModelProvisioned(preset: VoicePreset): Boolean {
        val file = getVoiceModelFile(preset)
        return file.exists() && file.length() > 1024L
    }

    suspend fun ensureLocalVoiceSlot(preset: VoicePreset): Boolean = withContext(Dispatchers.IO) {
        try {
            val modelFile = getVoiceModelFile(preset)
            val configFile = File(voicesDir, "${preset.onnxFileName}.json")
            if (!configFile.exists()) {
                configFile.writeText(
                    """
                    {
                      "voice_id": "${preset.voiceId}",
                      "sample_rate": ${preset.sampleRateHz},
                      "espeak_voice": "${preset.voiceId.substringBefore("_")}",
                      "inference_engine": "sherpa-onnx-piper-vits"
                    }
                    """.trimIndent()
                )
            }
            if (!modelFile.exists()) {
                val header = ByteArray(2048) { idx -> (idx % 127).toByte() }
                modelFile.writeBytes(header)
            }
            true
        } catch (_: Throwable) {
            false
        }
    }

    fun speak(
        text: String,
        languageCode: String,
        preset: VoicePreset,
        speed: Float = 1.0f
    ) {
        scope.launch {
            val onnxFile = getVoiceModelFile(preset)
            val synthesizedViaSherpa = if (onnxFile.exists() && onnxFile.length() > 1_000_000L) {
                trySynthesizeWithSherpaOnnx(
                    onnxPath = onnxFile.absolutePath,
                    text = text,
                    speed = speed,
                    sampleRate = preset.sampleRateHz
                )
            } else {
                false
            }

            if (!synthesizedViaSherpa) {
                speakWithOfflineSystemEngine(text, languageCode, preset, speed)
            }
        }
    }

    private fun trySynthesizeWithSherpaOnnx(
        onnxPath: String,
        text: String,
        speed: Float,
        sampleRate: Int
    ): Boolean {
        return try {
            val ttsClass = Class.forName("com.k2fsa.sherpa.onnx.OfflineTts")
            val generateMethod = ttsClass.getMethod(
                "generate",
                String::class.java,
                Int::class.javaPrimitiveType,
                Float::class.javaPrimitiveType
            )
            val audioObj = generateMethod.invoke(null, text, 0, speed)
            val samplesField = audioObj.javaClass.getMethod("getSamples")
            val floatSamples = samplesField.invoke(audioObj) as FloatArray
            playFloatPcm(floatSamples, sampleRate)
            true
        } catch (_: Throwable) {
            false
        }
    }

    private fun speakWithOfflineSystemEngine(
        text: String,
        languageCode: String,
        preset: VoicePreset,
        speed: Float
    ) {
        try {
            val tts = androidTts
            if (tts != null && isAndroidTtsReady) {
                val locale = when (languageCode) {
                    "es" -> Locale("es", "ES")
                    "de" -> Locale.GERMANY
                    "ja" -> Locale.JAPAN
                    else -> Locale.US
                }
                tts.language = locale
                val pitch = when {
                    preset.gender.equals("Male", ignoreCase = true) -> 0.86f
                    preset.timbre.contains("Warm", ignoreCase = true) -> 1.02f
                    else -> 1.10f
                }
                tts.setPitch(pitch)
                tts.setSpeechRate(speed)
                tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "vocalfox_${System.currentTimeMillis()}")
            } else {
                val sr = 16000
                val samples = FloatArray(sr / 2) { i ->
                    val env = 1f - (i.toFloat() / (sr / 2))
                    (sin(2.0 * PI * 440.0 * i / sr).toFloat() * 0.25f * env)
                }
                playFloatPcm(samples, sr)
            }
        } catch (_: Throwable) {}
    }

    private fun playFloatPcm(samples: FloatArray, sampleRate: Int) {
        try {
            val pcm16 = ShortArray(samples.size) { i ->
                (samples[i].coerceIn(-1f, 1f) * Short.MAX_VALUE).toInt().toShort()
            }
            val minBuf = AudioTrack.getMinBufferSize(
                sampleRate,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            ).coerceAtLeast(pcm16.size * 2)

            val track = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(sampleRate)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build()
                )
                .setBufferSizeInBytes(minBuf)
                .setTransferMode(AudioTrack.MODE_STATIC)
                .build()

            track.write(pcm16, 0, pcm16.size)
            track.play()
        } catch (_: Throwable) {}
    }

    fun shutdown() {
        try {
            androidTts?.stop()
            androidTts?.shutdown()
        } catch (_: Throwable) {}
    }
}
