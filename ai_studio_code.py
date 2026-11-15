#!/usr/bin/env python3
"""
patch_vocalfox.py
Applica i 2 aggiornamenti mirati a Vocalfox:
1. Chat Live AI Ultra-Veloce con Fail-Fast (connectTimeout=2500ms, readTimeout=5000ms, 0ms delay),
   Sticky Model in memoria e catena di fallback:
   gemini-3.8-flash -> gemini-2.5-flash -> gemini-2.5-flash-lite -> gemini-4-hydrogen
   (con pre-check silenzioso dei modelli disponibili per risolvere dinamicamente 'hydrogen' e messaggi di errore amichevoli senza JSON grezzo).
2. Sistema di Effetti Sonori (SFX) Procedurali Offline (VocalFoxSfxManager.kt) a 44.1kHz PCM con:
   playTileTap(), playSuccess(), playError(), playUnitComplete(), playChatPop()
   collegato a lezioni, chat Live AI e interruttore in Profilo (SettingsVoiceScreen.kt).
"""

from pathlib import Path

FILES: dict[str, str] = {
    "app/src/main/java/com/vocalfox/app/audio/VocalFoxSfxManager.kt": """\
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
import kotlin.math.PI
import kotlin.math.exp
import kotlin.math.sin

/**
 * Sintetizzatore procedurale offline di effetti sonori (SFX) a 44.100 Hz PCM 16-bit.
 * Zero file audio esterni richiesti, latenza minima e inviluppo anti-click.
 */
object VocalFoxSfxManager {
    private const val SAMPLE_RATE = 44100
    private const val PREFS_NAME = "vocalfox_prefs"
    private const val KEY_SFX_ENABLED = "sfx_enabled"

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

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

    /**
     * Tocco morbido e caldo alla selezione di una tessera parola o opzione.
     */
    fun playTileTap(context: Context) {
        if (!isSfxEnabled(context)) return
        scope.launch {
            val samples = synthesizeChirp(
                startFreqHz = 520.0,
                endFreqHz = 690.0,
                durationMs = 46,
                amplitude = 0.22
            )
            playPcmSamples(samples, 46)
        }
    }

    /**
     * Lieve suono cristallino all'invio/ricezione di un messaggio nella chat Live AI.
     */
    fun playChatPop(context: Context) {
        if (!isSfxEnabled(context)) return
        scope.launch {
            val samples = synthesizeChirp(
                startFreqHz = 640.0,
                endFreqHz = 880.0,
                durationMs = 54,
                amplitude = 0.20
            )
            playPcmSamples(samples, 54)
        }
    }

    /**
     * Accordo ascendente luminoso a 2 note per risposta esatta.
     */
    fun playSuccess(context: Context) {
        if (!isSfxEnabled(context)) return
        scope.launch {
            val samples = synthesizeSequence(
                notes = listOf(
                    NoteSpec(freqHz = 523.25, durationMs = 90, amplitude = 0.26), // C5
                    NoteSpec(freqHz = 783.99, durationMs = 150, amplitude = 0.28) // G5
                )
            )
            playPcmSamples(samples, 240)
        }
    }

    /**
     * Doppio tono morbido grave per risposta errata.
     */
    fun playError(context: Context) {
        if (!isSfxEnabled(context)) return
        scope.launch {
            val samples = synthesizeSequence(
                notes = listOf(
                    NoteSpec(freqHz = 260.0, durationMs = 95, amplitude = 0.24),
                    NoteSpec(freqHz = 196.0, durationMs = 140, amplitude = 0.24)
                )
            )
            playPcmSamples(samples, 235)
        }
    }

    /**
     * Breve arpeggio celebrativo a 4 note per il completamento dell'unità.
     */
    fun playUnitComplete(context: Context) {
        if (!isSfxEnabled(context)) return
        scope.launch {
            val samples = synthesizeSequence(
                notes = listOf(
                    NoteSpec(freqHz = 523.25, durationMs = 85, amplitude = 0.25),  // C5
                    NoteSpec(freqHz = 659.25, durationMs = 85, amplitude = 0.25),  // E5
                    NoteSpec(freqHz = 783.99, durationMs = 95, amplitude = 0.26),  // G5
                    NoteSpec(freqHz = 1046.50, durationMs = 210, amplitude = 0.28) // C6
                )
            )
            playPcmSamples(samples, 475)
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
            delay(durationMs.toLong() + 45L)
        } catch (_: Throwable) {
        } finally {
            try {
                track?.stop()
                track?.release()
            } catch (_: Throwable) {}
        }
    }
}
""",

    "app/src/main/java/com/vocalfox/app/audio/GeminiLiveTutorClient.kt": """\
package com.vocalfox.app.audio

import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.ui.i18n.SystemLang
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

data class TutorChatMessage(
    val isUser: Boolean,
    val text: String,
    val translation: String = "",
    val grammarCorrection: String = ""
)

/**
 * Client Live AI Ultra-Veloce con Fail-Fast (connectTimeout = 2500ms, readTimeout = 5000ms, 0ms delay),
 * Sticky Session Cache in memoria e catena di fallback a 4 livelli:
 * 1. gemini-3.8-flash
 * 2. gemini-2.5-flash
 * 3. gemini-2.5-flash-lite
 * 4. gemini-4-hydrogen (con risoluzione dinamica dell'eventuale modello "hydrogen" disponibile per la chiave).
 */
object GeminiLiveTutorClient {

    private const val CONNECT_TIMEOUT_MS = 2500
    private const val READ_TIMEOUT_MS = 5000

    @Volatile
    private var stickyModel: String? = null

    @Volatile
    private var resolvedHydrogenModel: String = "gemini-4-hydrogen"

    @Volatile
    private var hasCheckedModelsList: Boolean = false

    /**
     * Pre-check asincrono silenzioso chiamato all'apertura di LiveConversationScreen
     * per individuare l'eventuale nome esatto del modello contenente "hydrogen" associato all'API key.
     */
    suspend fun preCheckHydrogenModelAsync(apiKey: String) = withContext(Dispatchers.IO) {
        val cleanKey = apiKey.trim()
        if (cleanKey.isBlank() || hasCheckedModelsList) return@withContext
        hasCheckedModelsList = true

        try {
            val endpoint = "https://generativelanguage.googleapis.com/v1beta/models?key=$cleanKey"
            val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = READ_TIMEOUT_MS
            }
            if (conn.responseCode in 200..299) {
                val raw = BufferedReader(InputStreamReader(conn.inputStream, Charsets.UTF_8)).use { it.readText() }
                val root = JSONObject(raw)
                val modelsArr = root.optJSONArray("models") ?: return@withContext
                for (i in 0 until modelsArr.length()) {
                    val mObj = modelsArr.optJSONObject(i) ?: continue
                    val rawName = mObj.optString("name", "").removePrefix("models/")
                    if (rawName.contains("hydrogen", ignoreCase = true)) {
                        resolvedHydrogenModel = rawName
                        break
                    }
                }
            }
        } catch (_: Throwable) {
            // Silenzioso: mantiene il fallback predefinito "gemini-4-hydrogen"
        }
    }

    private fun buildOrderedModelChain(): List<String> {
        val baseChain = listOf(
            "gemini-3.8-flash",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            resolvedHydrogenModel
        )
        val currentSticky = stickyModel
        return if (!currentSticky.isNullOrBlank()) {
            listOf(currentSticky) + baseChain.filterNot { it.equals(currentSticky, ignoreCase = true) }
        } else {
            baseChain.distinct()
        }
    }

    suspend fun sendMessageToTutor(
        apiKey: String,
        targetLanguageCode: String,
        cefrLevel: CefrLevel,
        systemLang: SystemLang,
        scenarioTitle: String,
        history: List<TutorChatMessage>,
        userMessage: String
    ): Result<TutorChatMessage> = withContext(Dispatchers.IO) {
        val cleanKey = apiKey.trim()
        if (cleanKey.isBlank()) {
            val msg = if (systemLang == SystemLang.IT) {
                "Inserisci la tua chiave API Gemini nella scheda Profilo o usa il pulsante ✨ in alto."
            } else {
                "Enter your Gemini API Key in the Profile tab or tap the ✨ button above."
            }
            return@withContext Result.failure(IllegalArgumentException(msg))
        }

        val targetLangName = if (targetLanguageCode == "de") "German (Deutsch)" else "Spanish (Español)"
        val uiLangName = if (systemLang == SystemLang.IT) "Italian" else "English"

        val systemInstruction = \"\"\"
            You are Vocalfox, a warm, encouraging native $targetLangName language tutor.
            The student is currently at CEFR level ${cefrLevel.name}.
            Current roleplay scenario: "$scenarioTitle".
            Respond ONLY with a valid JSON object with exactly three string fields:
            {
              "reply": "Your natural conversational response in $targetLangName (2-3 sentences max, adapted to ${cefrLevel.name}, ending with an engaging follow-up question in $targetLangName)",
              "translation": "Accurate translation of your reply into $uiLangName",
              "correction": "Brief, friendly feedback in $uiLangName on the student's grammar/vocabulary (if their message was correct, praise it and suggest one idiomatic ${cefrLevel.name} expression)"
            }
        \"\"\".trimIndent()

        val contentsArray = JSONArray()
        history.takeLast(8).forEach { msg ->
            val role = if (msg.isUser) "user" else "model"
            val part = JSONObject().put("text", msg.text)
            val contentObj = JSONObject()
                .put("role", role)
                .put("parts", JSONArray().put(part))
            contentsArray.put(contentObj)
        }

        val userPart = JSONObject().put("text", userMessage)
        contentsArray.put(
            JSONObject()
                .put("role", "user")
                .put("parts", JSONArray().put(userPart))
        )

        val payloadString = JSONObject().apply {
            put(
                "system_instruction",
                JSONObject().put("parts", JSONArray().put(JSONObject().put("text", systemInstruction)))
            )
            put("contents", contentsArray)
            put(
                "generationConfig",
                JSONObject()
                    .put("temperature", 0.7)
                    .put("responseMimeType", "application/json")
            )
        }.toString()

        val modelsChain = buildOrderedModelChain()
        var encounteredAuthKeyError = false

        for (modelName in modelsChain) {
            try {
                val endpoint = "https://generativelanguage.googleapis.com/v1beta/models/$modelName:generateContent?key=$cleanKey"
                val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = CONNECT_TIMEOUT_MS
                    readTimeout = READ_TIMEOUT_MS
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                }

                OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { writer ->
                    writer.write(payloadString)
                }

                val code = conn.responseCode
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val rawResponse = if (stream != null) {
                    BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { it.readText() }
                } else {
                    ""
                }

                if (code in 200..299) {
                    val root = JSONObject(rawResponse)
                    val textOut = root.getJSONArray("candidates")
                        .getJSONObject(0)
                        .getJSONObject("content")
                        .getJSONArray("parts")
                        .getJSONObject(0)
                        .getString("text")
                        .trim()
                        .removePrefix("```json")
                        .removePrefix("```")
                        .removeSuffix("```")
                        .trim()

                    val parsed = JSONObject(textOut)
                    // Memorizza questo modello come Sticky Model per i messaggi successivi
                    stickyModel = modelName

                    return@withContext Result.success(
                        TutorChatMessage(
                            isUser = false,
                            text = parsed.optString("reply", "¡Muy bien! ¿Qué más me cuentas?"),
                            translation = parsed.optString("translation", ""),
                            grammarCorrection = parsed.optString("correction", "")
                        )
                    )
                } else {
                    // Se lo stickyModel ha fallito (503, 429, 404, 500), resettalo e passa con 0ms di attesa al modello successivo
                    if (stickyModel == modelName) {
                        stickyModel = null
                    }
                    if (code == 400 || code == 403) {
                        if (rawResponse.contains("API_KEY_INVALID", ignoreCase = true) ||
                            rawResponse.contains("API key not valid", ignoreCase = true)
                        ) {
                            encounteredAuthKeyError = true
                            break
                        }
                    }
                    // Continua immediatamente al prossimo modello della catena (0ms delay)
                }
            } catch (_: Throwable) {
                // SocketTimeoutException / IOException: resetta lo stickyModel e passa subito al modello successivo
                if (stickyModel == modelName) {
                    stickyModel = null
                }
            }
        }

        val friendlyMessage = if (encounteredAuthKeyError) {
            if (systemLang == SystemLang.IT) {
                "La chiave API Gemini inserita nel Profilo non è valida. Controllala o usa il pulsante ✨ in alto."
            } else {
                "The Gemini API key in Profile is invalid. Please check it or tap the ✨ button above."
            }
        } else {
            if (systemLang == SystemLang.IT) {
                "Tutti i modelli AI sono momentaneamente occupati, riprova tra pochi secondi oppure tocca ✨ in alto per usare l'app Gemini."
            } else {
                "All AI models are currently busy, please try again in a few seconds or tap ✨ above to use the Gemini app."
            }
        }

        Result.failure(RuntimeException(friendlyMessage))
    }
}
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/LiveConversationScreen.kt": """\
package com.vocalfox.app.ui.screens

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.speech.RecognizerIntent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.Send
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.vocalfox.app.audio.GeminiHandoffHelper
import com.vocalfox.app.audio.GeminiLiveTutorClient
import com.vocalfox.app.audio.TutorChatMessage
import com.vocalfox.app.audio.VocalFoxSfxManager
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import kotlinx.coroutines.launch

@Composable
fun LiveConversationScreen(
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    onSpeakText: (String, Float) -> Unit,
    onOpenSettingsForApiKey: () -> Unit
) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("vocalfox_prefs", Context.MODE_PRIVATE) }
    val colors = VocalFoxTheme.colors
    val scope = rememberCoroutineScope()
    val isIt = systemLang == SystemLang.IT

    // Pre-check asincrono silenzioso all'apertura di Live AI per risolvere eventuale modello Hydrogen
    LaunchedEffect(Unit) {
        val currentKey = prefs.getString("gemini_api_key", "").orEmpty()
        GeminiLiveTutorClient.preCheckHydrogenModelAsync(currentKey)
    }

    val scenarios = remember(isIt) {
        if (isIt) {
            listOf(
                "Conversazione libera",
                "Al Bar e Ristorante",
                "Viaggio, Hotel e Stazione",
                "Colloquio di Lavoro",
                "Dibattito d'Attualità"
            )
        } else {
            listOf(
                "Free Conversation",
                "At the Café & Restaurant",
                "Travel, Hotel & Station",
                "Job Interview",
                "Current Events Debate"
            )
        }
    }

    var selectedScenario by remember { mutableStateOf(scenarios.first()) }
    var userInput by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    val messages = remember(currentPack.languageCode, selectedScenario) {
        mutableStateListOf(
            if (currentPack.languageCode == "de") {
                TutorChatMessage(
                    isUser = false,
                    text = "Hallo! Ich bin dein Vocalfox Tutor (${selectedCefr.name}). Wollen wir über '$selectedScenario' auf Deutsch sprechen?",
                    translation = if (isIt) "Ciao! Sono il tuo tutor Vocalfox (${selectedCefr.name}). Parliamo di '$selectedScenario' in tedesco?" else "Hello! I am your Vocalfox tutor. Shall we speak German?",
                    grammarCorrection = ""
                )
            } else {
                TutorChatMessage(
                    isUser = false,
                    text = "¡Hola! Soy tu tutor Vocalfox (${selectedCefr.name}). ¿Hablamos sobre '$selectedScenario' en español?",
                    translation = if (isIt) "Ciao! Sono il tuo tutor Vocalfox (${selectedCefr.name}). Parliamo di '$selectedScenario' in spagnolo?" else "Hello! I am your Vocalfox tutor. Shall we speak Spanish?",
                    grammarCorrection = ""
                )
            }
        )
    }

    fun sendUserTurn(textToSend: String) {
        val trimmed = textToSend.trim()
        if (trimmed.isBlank() || isLoading) return
        val currentApiKey = prefs.getString("gemini_api_key", "").orEmpty().trim()
        if (currentApiKey.isBlank()) {
            VocalFoxSfxManager.playError(context)
            errorMessage = if (isIt) {
                "Per chattare qui inserisci la tua API Key nella scheda Profilo, oppure tocca l'icona ✨ in alto a destra per parlare subito nell'app Gemini."
            } else {
                "Set your API Key in the Profile tab to chat here, or tap the ✨ icon above to speak in the Gemini app."
            }
            return
        }

        errorMessage = null
        VocalFoxSfxManager.playChatPop(context)
        messages.add(TutorChatMessage(isUser = true, text = trimmed))
        userInput = ""
        isLoading = true

        scope.launch {
            val res = GeminiLiveTutorClient.sendMessageToTutor(
                apiKey = currentApiKey,
                targetLanguageCode = currentPack.languageCode,
                cefrLevel = selectedCefr,
                systemLang = systemLang,
                scenarioTitle = selectedScenario,
                history = messages.dropLast(1),
                userMessage = trimmed
            )
            isLoading = false
            res.onSuccess { replyMsg ->
                VocalFoxSfxManager.playChatPop(context)
                messages.add(replyMsg)
                onSpeakText(replyMsg.text, 1.0f)
            }.onFailure { err ->
                VocalFoxSfxManager.playError(context)
                errorMessage = err.message ?: if (isIt) {
                    "Tutti i modelli AI sono momentaneamente occupati, riprova tra pochi secondi."
                } else {
                    "All AI models are currently busy, please try again in a few seconds."
                }
            }
        }
    }

    val speechRecognizerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val spoken = result.data
                ?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                ?.firstOrNull()
            if (!spoken.isNullOrBlank()) {
                sendUserTurn(spoken)
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .imePadding()
            .padding(horizontal = 20.dp)
    ) {
        Spacer(modifier = Modifier.height(10.dp))

        // Header Pulito: Titolo a sinistra + SOLO Pulsante Circolare 44.dp con icona Sparkle di Gemini a destra
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "Live AI · ${currentPack.languageName.get(systemLang)} (${selectedCefr.name})",
                    style = VocalFoxType.PageTitle,
                    color = colors.primaryText
                )
                Text(
                    text = if (isIt) "Chatta qui o apri Gemini Live vocale" else "Chat here or open Gemini Live voice",
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.secondaryText
                )
            }

            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(CircleShape)
                    .background(colors.accent)
                    .clickable {
                        VocalFoxSfxManager.playTileTap(context)
                        GeminiHandoffHelper.launchGeminiAppWithPrompt(
                            context = context,
                            targetLanguageCode = currentPack.languageCode,
                            cefrLevel = selectedCefr,
                            systemLang = systemLang,
                            topic = selectedScenario
                        )
                    },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Outlined.AutoAwesome,
                    contentDescription = "Gemini Live",
                    tint = colors.onAccent,
                    modifier = Modifier.size(22.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            scenarios.forEach { scen ->
                val active = scen == selectedScenario
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (active) colors.accent else colors.card)
                        .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                        .clickable {
                            VocalFoxSfxManager.playTileTap(context)
                            selectedScenario = scen
                        }
                        .padding(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = scen,
                        style = VocalFoxType.SecondaryCaption,
                        color = if (active) colors.onAccent else colors.primaryText
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        if (errorMessage != null) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(colors.card)
                    .border(1.dp, colors.warning, RoundedCornerShape(12.dp))
                    .clickable { errorMessage = null }
                    .padding(12.dp)
            ) {
                Text(
                    text = errorMessage!!,
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.primaryText
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
        }

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(messages) { msg ->
                if (!msg.isUser) {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        if (msg.grammarCorrection.isNotBlank()) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(VocalFoxPalette.TintMintSage)
                                    .padding(12.dp)
                            ) {
                                Text(
                                    text = "Consiglio: ${msg.grammarCorrection}",
                                    style = VocalFoxType.SecondaryCaption,
                                    color = VocalFoxPalette.FoxDeepInkBrown
                                )
                            }
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalAlignment = Alignment.Top
                        ) {
                            VocalFoxMascot(
                                state = MascotState.LOGO_IDLE,
                                size = 48.dp,
                                tintBackground = VocalFoxPalette.TintWarmAmber
                            )
                            Column(
                                modifier = Modifier
                                    .weight(1f)
                                    .clip(RoundedCornerShape(18.dp))
                                    .background(colors.card)
                                    .border(1.dp, colors.hairline, RoundedCornerShape(18.dp))
                                    .padding(14.dp),
                                verticalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Text(
                                    text = msg.text,
                                    style = VocalFoxType.BodyMedium,
                                    color = colors.primaryText
                                )
                                if (msg.translation.isNotBlank()) {
                                    Text(
                                        text = msg.translation,
                                        style = VocalFoxType.SecondaryCaption,
                                        color = colors.secondaryText
                                    )
                                }
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(colors.raised)
                                            .clickable { onSpeakText(msg.text, 1.0f) }
                                            .padding(horizontal = 10.dp, vertical = 6.dp),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        Icon(Icons.Outlined.VolumeUp, null, tint = colors.accent, modifier = Modifier.size(15.dp))
                                        Text("1.0x", style = VocalFoxType.MetaMono, color = colors.primaryText)
                                    }
                                    Row(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(colors.raised)
                                            .clickable { onSpeakText(msg.text, 0.75f) }
                                            .padding(horizontal = 10.dp, vertical = 6.dp),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        Icon(Icons.Outlined.SlowMotionVideo, null, tint = colors.accent, modifier = Modifier.size(15.dp))
                                        Text("0.75x", style = VocalFoxType.MetaMono, color = colors.primaryText)
                                    }
                                }
                            }
                        }
                    }
                } else {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.End
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(18.dp))
                                .background(colors.accent)
                                .padding(horizontal = 16.dp, vertical = 12.dp)
                        ) {
                            Text(
                                text = msg.text,
                                style = VocalFoxType.BodyMedium,
                                color = colors.onAccent
                            )
                        }
                    }
                }
            }

            if (isLoading) {
                item {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        modifier = Modifier.padding(8.dp)
                    ) {
                        CircularProgressIndicator(
                            color = colors.accent,
                            strokeWidth = 2.5.dp,
                            modifier = Modifier.size(22.dp)
                        )
                        Text(
                            text = if (isIt) "Vocalfox sta rispondendo..." else "Vocalfox is replying...",
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(6.dp)) }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp, bottom = 10.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(colors.raised)
                    .border(1.dp, colors.hairline, CircleShape)
                    .clickable {
                        VocalFoxSfxManager.playTileTap(context)
                        try {
                            val localeTag = if (currentPack.languageCode == "de") "de-DE" else "es-ES"
                            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                                putExtra(RecognizerIntent.EXTRA_LANGUAGE, localeTag)
                            }
                            speechRecognizerLauncher.launch(intent)
                        } catch (_: Throwable) {
                            errorMessage = if (isIt) "Riconoscimento vocale non disponibile, usa la tastiera." else "Voice recognition unavailable, please type."
                        }
                    },
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Outlined.Mic, contentDescription = "Speak", tint = colors.accent, modifier = Modifier.size(22.dp))
            }

            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(24.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(24.dp))
                    .padding(horizontal = 16.dp, vertical = 14.dp)
            ) {
                if (userInput.isEmpty()) {
                    Text(
                        text = if (currentPack.languageCode == "de") "Scrivi un messaggio in tedesco..." else "Scrivi un messaggio in spagnolo...",
                        style = VocalFoxType.Body,
                        color = colors.mutedText
                    )
                }
                BasicTextField(
                    value = userInput,
                    onValueChange = { userInput = it },
                    textStyle = VocalFoxType.Body.copy(color = colors.primaryText),
                    cursorBrush = SolidColor(colors.accent),
                    modifier = Modifier.fillMaxWidth()
                )
            }

            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(colors.accent)
                    .clickable { sendUserTurn(userInput) },
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Outlined.Send, contentDescription = "Send", tint = colors.onAccent, modifier = Modifier.size(20.dp))
            }
        }
    }
}
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/OnboardingAndLessonScreens.kt": """\
package com.vocalfox.app.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.Stop
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.vocalfox.app.audio.GeminiHandoffHelper
import com.vocalfox.app.audio.PhonemeAccuracyStatus
import com.vocalfox.app.audio.PronunciationResult
import com.vocalfox.app.audio.VocalFoxSfxManager
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.GrammarSyntaxExercise
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.domain.model.WritingExercise
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.AnimatedWebpSplashPlayer
import com.vocalfox.app.ui.theme.MascotBitmapCache
import com.vocalfox.app.ui.theme.MascotPedagogicalBanner
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.theme.VocalFoxWordmark

data class GuidedUnitBundle(
    val unitIndex: Int,
    val cefr: CefrLevel,
    val chapterBadge: String = "",
    val title: String,
    val subtitle: String,
    val durationMinutes: Int,
    val tintColor: Color,
    val mascotPose: MascotState,
    val grammarExercise: GrammarSyntaxExercise,
    val writingExercise: WritingExercise,
    val pronunciationDrill: PronunciationDrill
)

@Composable
fun SplashScreenOverlay(
    onFinished: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF000000))
            .clickable { onFinished() },
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            AnimatedWebpSplashPlayer(size = 240.dp)
            VocalFoxWordmark(height = 44.dp)
        }
    }
}

@Composable
fun OnboardingScreen(
    allPacks: Map<String, LanguagePack>,
    selectedLangCode: String,
    systemLang: SystemLang,
    strings: UiStrings,
    onSelectSystemLang: (SystemLang) -> Unit,
    onSelectTargetLang: (String) -> Unit,
    onCompleteOnboarding: (CefrLevel) -> Unit
) {
    val context = LocalContext.current
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    var onboardingPhase by remember { mutableIntStateOf(0) }
    var inPlacementMode by remember { mutableStateOf(false) }
    var questionIdx by remember { mutableIntStateOf(0) }
    var correctCount by remember { mutableIntStateOf(0) }

    val welcomeKitBitmap = remember {
        MascotBitmapCache.getTrimmedBitmap(context, "welcome_kit", stripBackground = true)
    }

    val pack = allPacks[selectedLangCode] ?: allPacks.values.first()
    val placementQuestions = remember(pack.languageCode) {
        CefrLevel.entries.mapNotNull { lvl ->
            pack.grammarExercises.firstOrNull { it.cefr == lvl }
        }
    }

    if (onboardingPhase == 0) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(if (colors.isDark) colors.background else Color.White)
                .statusBarsPadding()
                .navigationBarsPadding()
                .padding(horizontal = 24.dp, vertical = 20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Spacer(modifier = Modifier.height(24.dp))

            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(18.dp)
            ) {
                if (welcomeKitBitmap != null) {
                    Image(
                        bitmap = welcomeKitBitmap,
                        contentDescription = "Vocalfox Welcome",
                        contentScale = ContentScale.Fit,
                        modifier = Modifier.size(210.dp)
                    )
                } else {
                    VocalFoxMascot(
                        state = MascotState.CELEBRATE,
                        size = 200.dp
                    )
                }

                VocalFoxWordmark(height = 42.dp)

                Text(
                    text = if (isIt) "Impara una lingua gratuitamente. Per sempre." else "Learn a language for free. Forever.",
                    style = VocalFoxType.Body,
                    color = colors.secondaryText,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 16.dp)
                )
            }

            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.accent)
                        .clickable {
                            VocalFoxSfxManager.playTileTap(context)
                            onboardingPhase = 1
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (isIt) "INIZIA" else "GET STARTED",
                        style = VocalFoxType.SectionTitle,
                        color = colors.onAccent
                    )
                }

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(if (colors.isDark) colors.card else Color.White)
                        .border(1.5.dp, colors.hairline, RoundedCornerShape(16.dp))
                        .clickable {
                            VocalFoxSfxManager.playTileTap(context)
                            onboardingPhase = 2
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (isIt) "HO GIÀ UN LIVELLO / SALTA AL PERCORSO" else "I ALREADY HAVE A LEVEL / SKIP TO PATH",
                        style = VocalFoxType.BodyMedium,
                        color = colors.accent
                    )
                }
            }
        }
        return
    }

    if (onboardingPhase == 2) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(colors.background)
                .statusBarsPadding()
                .navigationBarsPadding()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            VocalFoxWordmark(height = 34.dp)

            Text(
                text = strings.chooseTargetLanguageLabel,
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                allPacks.values.forEach { p ->
                    val isSelected = p.languageCode == selectedLangCode
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (isSelected) colors.card else colors.raised)
                            .border(
                                width = if (isSelected) 2.dp else 1.dp,
                                color = if (isSelected) colors.accent else colors.hairline,
                                shape = RoundedCornerShape(14.dp)
                            )
                            .clickable {
                                VocalFoxSfxManager.playTileTap(context)
                                onSelectTargetLang(p.languageCode)
                            }
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = p.languageName.get(systemLang),
                            style = VocalFoxType.SectionTitle,
                            color = colors.primaryText
                        )
                        if (isSelected) {
                            Icon(Icons.Outlined.Check, null, tint = colors.accent)
                        }
                    }
                }
            }

            Text(
                text = if (isIt) "Scegli il livello da cui partire" else "Choose your starting level",
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )
            CefrLevel.entries.forEach { lvl ->
                val desc = when (lvl) {
                    CefrLevel.A1 -> if (isIt) "A1 · Principiante (Prime parole e basi)" else "A1 · Beginner"
                    CefrLevel.A2 -> if (isIt) "A2 · Elementare (Vita quotidiana e passato)" else "A2 · Elementary"
                    CefrLevel.B1 -> if (isIt) "B1 · Intermedio (Conversazione e opinioni)" else "B1 · Intermediate"
                    CefrLevel.B2 -> if (isIt) "B2 · Avanzato (Padronanza e sfumature)" else "B2 · Upper Intermediate"
                }
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(14.dp))
                        .clickable {
                            VocalFoxSfxManager.playUnitComplete(context)
                            onCompleteOnboarding(lvl)
                        }
                        .padding(18.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(desc, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                    Icon(Icons.Outlined.ArrowForward, null, tint = colors.accent)
                }
            }
        }
        return
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .navigationBarsPadding()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        VocalFoxWordmark(height = 34.dp)

        if (!inPlacementMode) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(VocalFoxPalette.TintWarmAmber)
                    .padding(20.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                VocalFoxMascot(state = MascotState.LOGO_IDLE, size = 84.dp)
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = strings.onboardingWelcomeTitle,
                        style = VocalFoxType.SectionTitle,
                        color = VocalFoxPalette.FoxDeepInkBrown
                    )
                    Text(
                        text = strings.onboardingWelcomeSub,
                        style = VocalFoxType.SecondaryCaption,
                        color = VocalFoxPalette.FoxDeepInkBrown.copy(alpha = 0.8f)
                    )
                }
            }

            Text(
                text = strings.chooseUiLanguageLabel,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                SystemLang.entries.forEach { lang ->
                    val active = lang == systemLang
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (active) colors.accent else colors.card)
                            .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                            .clickable {
                                VocalFoxSfxManager.playTileTap(context)
                                onSelectSystemLang(lang)
                            }
                            .padding(vertical = 14.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = lang.displayName,
                            style = VocalFoxType.BodyMedium,
                            color = if (active) colors.onAccent else colors.primaryText
                        )
                    }
                }
            }

            Text(
                text = strings.chooseTargetLanguageLabel,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                allPacks.values.forEach { p ->
                    val isSelected = p.languageCode == selectedLangCode
                    val flagBadge = when (p.languageCode) {
                        "es" -> "ES · Español (200 Unità A1–B2)"
                        "de" -> "DE · Deutsch (200 Unità A1–B2)"
                        else -> p.languageCode.uppercase()
                    }
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (isSelected) colors.card else colors.raised)
                            .border(
                                width = if (isSelected) 2.dp else 1.dp,
                                color = if (isSelected) colors.accent else colors.hairline,
                                shape = RoundedCornerShape(14.dp)
                            )
                            .clickable {
                                VocalFoxSfxManager.playTileTap(context)
                                onSelectTargetLang(p.languageCode)
                            }
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = p.languageName.get(systemLang),
                                style = VocalFoxType.SectionTitle,
                                color = colors.primaryText
                            )
                            Text(
                                text = flagBadge,
                                style = VocalFoxType.MetaMono,
                                color = colors.secondaryText
                            )
                        }
                        if (isSelected) {
                            Box(
                                modifier = Modifier
                                    .size(28.dp)
                                    .clip(CircleShape)
                                    .background(colors.accent),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.Check,
                                    contentDescription = null,
                                    tint = colors.onAccent,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }
                    }
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.accent)
                    .clickable {
                        VocalFoxSfxManager.playUnitComplete(context)
                        onCompleteOnboarding(CefrLevel.A1)
                    }
                    .padding(18.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = strings.startFromScratchTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.onAccent
                    )
                    Text(
                        text = strings.startFromScratchSub,
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.onAccent.copy(alpha = 0.9f)
                    )
                }
                Icon(
                    imageVector = Icons.Outlined.ArrowForward,
                    contentDescription = null,
                    tint = colors.onAccent
                )
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                    .clickable {
                        VocalFoxSfxManager.playTileTap(context)
                        questionIdx = 0
                        correctCount = 0
                        inPlacementMode = true
                    }
                    .padding(18.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = strings.takePlacementTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Text(
                        text = strings.takePlacementSub,
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }
                Icon(
                    imageVector = Icons.Outlined.ArrowForward,
                    contentDescription = null,
                    tint = colors.accent
                )
            }
        } else {
            val currentQ = placementQuestions.getOrNull(questionIdx)
            if (currentQ != null) {
                val options = remember(currentQ.id) {
                    (listOf(currentQ.blankTarget) + currentQ.distractors).shuffled()
                }
                Text(
                    text = "${strings.placementHeader} (${questionIdx + 1}/${placementQuestions.size})",
                    style = VocalFoxType.MetaMono,
                    color = colors.accent
                )
                LinearProgressIndicator(
                    progress = { (questionIdx + 1).toFloat() / placementQuestions.size.coerceAtLeast(1) },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp)
                        .clip(RoundedCornerShape(4.dp)),
                    color = colors.accent,
                    trackColor = colors.raised
                )

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                        .padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Text(
                        text = currentQ.title.get(systemLang),
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                    Text(
                        text = currentQ.promptSentence,
                        style = VocalFoxType.SentenceDisplay,
                        color = colors.primaryText
                    )

                    options.forEach { opt ->
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(colors.raised)
                                .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                                .clickable {
                                    if (opt == currentQ.blankTarget) {
                                        VocalFoxSfxManager.playSuccess(context)
                                        correctCount++
                                    } else {
                                        VocalFoxSfxManager.playError(context)
                                    }
                                    if (questionIdx + 1 < placementQuestions.size) {
                                        questionIdx++
                                    } else {
                                        val assigned = when (correctCount) {
                                            0, 1 -> CefrLevel.A1
                                            2 -> CefrLevel.A2
                                            3 -> CefrLevel.B1
                                            else -> CefrLevel.B2
                                        }
                                        VocalFoxSfxManager.playUnitComplete(context)
                                        onCompleteOnboarding(assigned)
                                    }
                                }
                                .padding(16.dp)
                        ) {
                            Text(
                                text = opt,
                                style = VocalFoxType.BodyMedium,
                                color = colors.primaryText
                            )
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun GuidedLessonScreen(
    bundle: GuidedUnitBundle,
    systemLang: SystemLang,
    strings: UiStrings,
    isRecording: Boolean,
    pronunciationResult: PronunciationResult?,
    onSpeakText: (String, Float) -> Unit,
    onStartRecording: (PronunciationDrill) -> Unit,
    onStopAndEvaluate: (PronunciationDrill) -> Unit,
    onCompleteUnit: (GuidedUnitBundle, Int) -> Unit,
    onClose: () -> Unit
) {
    val context = LocalContext.current
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT
    var currentStep by remember(bundle.unitIndex) { mutableIntStateOf(0) } // 0..5

    val animatedProgress by animateFloatAsState(
        targetValue = (currentStep + 1) / 6f,
        animationSpec = tween(300),
        label = "lesson_progress"
    )

    val micPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) onStartRecording(bundle.pronunciationDrill)
        else onStopAndEvaluate(bundle.pronunciationDrill)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .navigationBarsPadding()
            .padding(horizontal = 20.dp, vertical = 14.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(colors.raised)
                    .clickable(onClick = onClose),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Outlined.Close,
                    contentDescription = null,
                    tint = colors.primaryText,
                    modifier = Modifier.size(20.dp)
                )
            }

            LinearProgressIndicator(
                progress = { animatedProgress },
                modifier = Modifier
                    .weight(1f)
                    .height(10.dp)
                    .clip(RoundedCornerShape(5.dp)),
                color = colors.accent,
                trackColor = colors.raised
            )

            Text(
                text = "${(currentStep + 1).coerceAtMost(5)}/5",
                style = VocalFoxType.MetaMono,
                color = colors.secondaryText
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        AnimatedContent(
            targetState = currentStep,
            transitionSpec = {
                fadeIn(animationSpec = tween(220)) togetherWith fadeOut(animationSpec = tween(180))
            },
            modifier = Modifier.weight(1f),
            label = "step_transition"
        ) { step ->
            when (step) {
                0 -> {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = "${bundle.cefr.name} · Unità ${bundle.unitIndex + 1} · ${strings.stepLearnWords}",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Text(
                            text = bundle.title,
                            style = VocalFoxType.PageTitle,
                            color = colors.primaryText
                        )
                        Text(
                            text = strings.tapWordToListenHint,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )

                        bundle.grammarExercise.syntaxTokens.forEach { token ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(16.dp))
                                    .background(colors.card)
                                    .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                    .clickable {
                                        VocalFoxSfxManager.playTileTap(context)
                                        onSpeakText(token.surface, 1.0f)
                                    }
                                    .padding(18.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(
                                    modifier = Modifier.weight(1f),
                                    verticalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    Text(
                                        text = token.surface,
                                        style = VocalFoxType.SentenceDisplay,
                                        color = colors.primaryText
                                    )
                                    Text(
                                        text = token.gloss.get(systemLang),
                                        style = VocalFoxType.Body,
                                        color = colors.secondaryText
                                    )
                                }
                                Box(
                                    modifier = Modifier
                                        .size(44.dp)
                                        .clip(CircleShape)
                                        .background(VocalFoxPalette.TintWarmAmber),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = null,
                                        tint = VocalFoxPalette.FoxFurOrangeDark
                                    )
                                }
                            }
                        }

                        MascotPedagogicalBanner(
                            state = MascotState.THINKING,
                            title = if (isIt) "Regola chiave" else "Key rule",
                            subtitle = bundle.grammarExercise.explanation.get(systemLang)
                        )

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = strings.continueButton,
                            onClick = {
                                VocalFoxSfxManager.playTileTap(context)
                                currentStep = 1
                            }
                        )
                    }
                }

                1 -> {
                    val ex = bundle.grammarExercise
                    val options = remember(ex.id) {
                        (listOf(ex.blankTarget) + ex.distractors).shuffled()
                    }
                    var picked by remember(ex.id) { mutableStateOf<String?>(null) }
                    var verified by remember(ex.id) { mutableStateOf(false) }
                    val isRight = picked == ex.blankTarget

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = strings.stepQuizChoice,
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Text(
                            text = strings.tapOptionToHearHint,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Text(
                                text = ex.promptSentence.replace("___", picked ?: " _____ "),
                                style = VocalFoxType.SentenceDisplay,
                                color = colors.primaryText
                            )

                            options.forEach { option ->
                                val selected = picked == option
                                val borderCol = when {
                                    verified && option == ex.blankTarget -> colors.positive
                                    verified && selected && !isRight -> colors.negative
                                    selected -> colors.accent
                                    else -> colors.hairline
                                }
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(if (selected) colors.raised else colors.background)
                                        .border(2.dp, borderCol, RoundedCornerShape(12.dp))
                                        .clickable {
                                            picked = option
                                            verified = false
                                            VocalFoxSfxManager.playTileTap(context)
                                            onSpeakText(option, 1.0f)
                                        }
                                        .padding(16.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = option,
                                        style = VocalFoxType.BodyMedium,
                                        color = colors.primaryText
                                    )
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = null,
                                        tint = colors.mutedText,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                            }
                        }

                        if (verified) {
                            MascotPedagogicalBanner(
                                state = if (isRight) MascotState.CELEBRATE else MascotState.STRICT_COACH,
                                title = if (isRight) "Corretto" else ex.blankTarget,
                                subtitle = ex.explanation.get(systemLang)
                            )
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!verified) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!verified && picked != null) {
                                    verified = true
                                    if (isRight) VocalFoxSfxManager.playSuccess(context)
                                    else VocalFoxSfxManager.playError(context)
                                    onSpeakText(ex.promptSentence.replace("___", ex.blankTarget), 1.0f)
                                } else if (verified) {
                                    VocalFoxSfxManager.playTileTap(context)
                                    currentStep = 2
                                }
                            }
                        )
                    }
                }

                2 -> {
                    val tokens = bundle.grammarExercise.syntaxTokens
                    val targetToken = tokens.firstOrNull()
                    val correctMeaning = targetToken?.gloss?.get(systemLang).orEmpty()
                    val distractorMeanings = remember(bundle.unitIndex) {
                        val otherGlosses = tokens.drop(1).map { it.gloss.get(systemLang) }
                        val defaults = if (isIt) listOf("Ieri sera tardi", "Domani pomeriggio") else listOf("Late last night", "Tomorrow afternoon")
                        (listOf(correctMeaning) + otherGlosses + defaults).distinct().take(4).shuffled()
                    }
                    var pickedMeaning by remember(bundle.unitIndex) { mutableStateOf<String?>(null) }
                    var verifiedMeaning by remember(bundle.unitIndex) { mutableStateOf(false) }

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = if (isIt) "Passo 3 · Riconosci il significato" else "Step 3 · Meaning check",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .clickable {
                                    VocalFoxSfxManager.playTileTap(context)
                                    onSpeakText(targetToken?.surface.orEmpty(), 1.0f)
                                }
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Text(
                                text = if (isIt) "Cosa significa questa espressione?" else "What does this expression mean?",
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.secondaryText
                            )
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Icon(Icons.Outlined.VolumeUp, null, tint = colors.accent)
                                Text(
                                    text = targetToken?.surface.orEmpty(),
                                    style = VocalFoxType.PageTitle,
                                    color = colors.primaryText
                                )
                            }
                        }

                        distractorMeanings.forEach { mOpt ->
                            val selected = pickedMeaning == mOpt
                            val borderCol = when {
                                verifiedMeaning && mOpt == correctMeaning -> colors.positive
                                verifiedMeaning && selected && mOpt != correctMeaning -> colors.negative
                                selected -> colors.accent
                                else -> colors.hairline
                            }
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(if (selected) colors.raised else colors.card)
                                    .border(2.dp, borderCol, RoundedCornerShape(12.dp))
                                    .clickable {
                                        VocalFoxSfxManager.playTileTap(context)
                                        pickedMeaning = mOpt
                                        verifiedMeaning = false
                                    }
                                    .padding(16.dp)
                            ) {
                                Text(mOpt, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                            }
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!verifiedMeaning) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!verifiedMeaning && pickedMeaning != null) {
                                    verifiedMeaning = true
                                    if (pickedMeaning == correctMeaning) VocalFoxSfxManager.playSuccess(context)
                                    else VocalFoxSfxManager.playError(context)
                                } else if (verifiedMeaning) {
                                    VocalFoxSfxManager.playTileTap(context)
                                    currentStep = 3
                                }
                            }
                        )
                    }
                }

                3 -> {
                    val wrt = bundle.writingExercise
                    val targetSentence = wrt.referenceTargets.firstOrNull().orEmpty()
                    val allWords = remember(wrt.id) {
                        targetSentence
                            .replace(".", "")
                            .replace(",", "")
                            .replace("¿", "")
                            .replace("?", "")
                            .split(" ")
                            .filter { it.isNotBlank() }
                            .ifEmpty { bundle.grammarExercise.scrambleTokens }
                    }
                    val shuffledBank = remember(wrt.id) { allWords.shuffled() }
                    val selectedWords = remember(wrt.id) { mutableStateListOf<String>() }
                    var checked by remember(wrt.id) { mutableStateOf(false) }

                    val builtRight = selectedWords.size == allWords.size &&
                        selectedWords.indices.all { idx ->
                            selectedWords[idx].equals(allWords[idx], ignoreCase = true)
                        }

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = if (isIt) "Passo 4 · Componi la frase" else "Step 4 · Build the sentence",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Text(
                            text = strings.buildSentenceInstruction,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(18.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = wrt.sourcePrompt.get(systemLang),
                                style = VocalFoxType.SentenceDisplay,
                                color = colors.primaryText
                            )
                        }

                        FlowRow(
                            modifier = Modifier
                                .fillMaxWidth()
                                .heightIn(min = 104.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.raised)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            selectedWords.forEachIndexed { index, w ->
                                val isWordAtPosCorrect = checked &&
                                    allWords.getOrNull(index)?.equals(w, ignoreCase = true) == true

                                val tileBorderColor = when {
                                    !checked -> colors.accent
                                    isWordAtPosCorrect -> colors.positive
                                    else -> colors.negative
                                }
                                val tileBgColor = when {
                                    !checked -> colors.card
                                    isWordAtPosCorrect -> colors.positive.copy(alpha = 0.12f)
                                    else -> colors.negative.copy(alpha = 0.12f)
                                }
                                val tileTextColor = when {
                                    !checked -> colors.primaryText
                                    isWordAtPosCorrect -> colors.positive
                                    else -> colors.negative
                                }

                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(tileBgColor)
                                        .border(2.dp, tileBorderColor, RoundedCornerShape(10.dp))
                                        .clickable {
                                            VocalFoxSfxManager.playTileTap(context)
                                            selectedWords.removeAt(index)
                                            checked = false
                                        }
                                        .padding(horizontal = 12.dp, vertical = 8.dp)
                                ) {
                                    Text(
                                        text = w,
                                        style = VocalFoxType.BodyMedium,
                                        color = tileTextColor
                                    )
                                }
                            }
                        }

                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            shuffledBank.forEach { word ->
                                val alreadyUsed = selectedWords.count { it == word } >= allWords.count { it == word }
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(if (alreadyUsed) colors.raised else colors.card)
                                        .border(1.dp, colors.hairline, RoundedCornerShape(10.dp))
                                        .clickable(enabled = !alreadyUsed) {
                                            VocalFoxSfxManager.playTileTap(context)
                                            selectedWords.add(word)
                                            checked = false
                                            onSpeakText(word, 1.0f)
                                        }
                                        .padding(horizontal = 14.dp, vertical = 10.dp)
                                ) {
                                    Text(
                                        text = word,
                                        style = VocalFoxType.BodyMedium,
                                        color = if (alreadyUsed) colors.mutedText else colors.primaryText
                                    )
                                }
                            }
                        }

                        if (checked) {
                            MascotPedagogicalBanner(
                                state = if (builtRight) MascotState.CELEBRATE else MascotState.STRICT_COACH,
                                title = if (builtRight) {
                                    if (isIt) "Frase perfetta!" else "Perfect sentence!"
                                } else {
                                    targetSentence
                                },
                                subtitle = if (builtRight) {
                                    wrt.jitFeedback.get(systemLang)
                                } else {
                                    if (isIt) {
                                        "Le parole in verde sono al posto giusto, quelle in rosso vanno spostate. Tocca una parola per correggerla o premi Continua."
                                    } else {
                                        "Green words are in the right spot, red ones need adjustment. Tap a word to fix it or press Continue."
                                    }
                                }
                            )
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!checked) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!checked && selectedWords.isNotEmpty()) {
                                    checked = true
                                    if (builtRight) VocalFoxSfxManager.playSuccess(context)
                                    else VocalFoxSfxManager.playError(context)
                                    onSpeakText(targetSentence, 1.0f)
                                } else if (checked) {
                                    VocalFoxSfxManager.playTileTap(context)
                                    currentStep = 4
                                }
                            }
                        )
                    }
                }

                4 -> {
                    val drill = bundle.pronunciationDrill
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = if (isIt) "Passo 5 · Ascolta e pronuncia" else "Step 5 · Listen & speak aloud",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Text(
                                text = drill.targetSentence,
                                style = VocalFoxType.SentenceDisplay,
                                color = colors.primaryText
                            )
                            Text(
                                text = drill.translation.get(systemLang),
                                style = VocalFoxType.Body,
                                color = colors.secondaryText
                            )

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Row(
                                    modifier = Modifier
                                        .weight(1f)
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(colors.raised)
                                        .clickable { onSpeakText(drill.targetSentence, 1.0f) }
                                        .padding(vertical = 12.dp),
                                    horizontalArrangement = Arrangement.Center,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Outlined.VolumeUp, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(strings.listenNormal, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                                }
                                Row(
                                    modifier = Modifier
                                        .weight(1f)
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(colors.raised)
                                        .clickable { onSpeakText(drill.targetSentence, 0.75f) }
                                        .padding(vertical = 12.dp),
                                    horizontalArrangement = Arrangement.Center,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Outlined.SlowMotionVideo, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(strings.listenSlow, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                                }
                            }

                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(14.dp))
                                    .background(if (isRecording) colors.negative else colors.accent)
                                    .clickable {
                                        VocalFoxSfxManager.playTileTap(context)
                                        if (isRecording) {
                                            onStopAndEvaluate(drill)
                                        } else {
                                            val granted = ContextCompat.checkSelfPermission(
                                                context,
                                                Manifest.permission.RECORD_AUDIO
                                            ) == PackageManager.PERMISSION_GRANTED
                                            if (granted) onStartRecording(drill)
                                            else micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                                        }
                                    }
                                    .padding(vertical = 16.dp),
                                horizontalArrangement = Arrangement.Center,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = if (isRecording) Icons.Outlined.Stop else Icons.Outlined.Mic,
                                    contentDescription = null,
                                    tint = colors.onAccent
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = if (isRecording) strings.stopListening else strings.tapToSpeak,
                                    style = VocalFoxType.BodyMedium,
                                    color = colors.onAccent
                                )
                            }
                        }

                        if (pronunciationResult != null) {
                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                pronunciationResult.wordFeedbacks.forEach { wf ->
                                    val col = when (wf.status) {
                                        PhonemeAccuracyStatus.ACCURATE -> colors.positive
                                        PhonemeAccuracyStatus.STRESS_OR_PITCH -> colors.warning
                                        PhonemeAccuracyStatus.MISPRONOUNCED -> colors.negative
                                    }
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(10.dp))
                                            .background(colors.card)
                                            .border(2.dp, col, RoundedCornerShape(10.dp))
                                            .clickable { onSpeakText(wf.word, 0.85f) }
                                            .padding(horizontal = 12.dp, vertical = 8.dp)
                                    ) {
                                        Text(
                                            text = "${wf.word} · ${wf.score}%",
                                            style = VocalFoxType.BodyMedium,
                                            color = colors.primaryText
                                        )
                                    }
                                }
                            }
                        }

                        MascotPedagogicalBanner(
                            state = if ((pronunciationResult?.overallScore ?: 0) >= 80) MascotState.CELEBRATE else MascotState.LOGO_IDLE,
                            title = if (pronunciationResult != null) "${pronunciationResult.overallScore}%" else bundle.cefr.name,
                            subtitle = drill.articulatoryTip.get(systemLang)
                        )

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = strings.finishUnitButton,
                            onClick = {
                                VocalFoxSfxManager.playUnitComplete(context)
                                onCompleteUnit(bundle, pronunciationResult?.overallScore ?: 95)
                                currentStep = 5
                            }
                        )
                    }
                }

                else -> {
                    val langCode = if (bundle.grammarExercise.id.startsWith("de")) "de" else "es"
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        VocalFoxMascot(
                            state = MascotState.CELEBRATE,
                            size = 150.dp,
                            tintBackground = VocalFoxPalette.TintSoftGold
                        )
                        Spacer(modifier = Modifier.height(20.dp))
                        Text(
                            text = strings.unitCompletedTitle,
                            style = VocalFoxType.PageTitle,
                            color = colors.primaryText
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = strings.unitCompletedSubtitle,
                            style = VocalFoxType.Body,
                            color = colors.secondaryText
                        )
                        Spacer(modifier = Modifier.height(24.dp))

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(14.dp))
                                .background(colors.card)
                                .border(1.5.dp, colors.accent, RoundedCornerShape(14.dp))
                                .clickable {
                                    VocalFoxSfxManager.playTileTap(context)
                                    GeminiHandoffHelper.launchGeminiAppWithPrompt(
                                        context = context,
                                        targetLanguageCode = langCode,
                                        cefrLevel = bundle.cefr,
                                        systemLang = systemLang,
                                        topic = bundle.title
                                    )
                                }
                                .padding(vertical = 14.dp, horizontal = 16.dp),
                            horizontalArrangement = Arrangement.Center,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.AutoAwesome,
                                contentDescription = null,
                                tint = colors.accent,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = if (isIt) "Pratica '${bundle.title}' su Gemini Live" else "Practice '${bundle.title}' on Gemini Live",
                                style = VocalFoxType.BodyMedium,
                                color = colors.accent
                            )
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        PrimaryBottomButton(
                            text = strings.continueButton,
                            onClick = {
                                VocalFoxSfxManager.playTileTap(context)
                                onClose()
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun PrimaryBottomButton(
    text: String,
    onClick: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(colors.accent)
            .clickable(onClick = onClick)
            .padding(vertical = 16.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = VocalFoxType.SectionTitle,
            color = colors.onAccent
        )
    }
}
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/SettingsVoiceScreen.kt": """\
package com.vocalfox.app.ui.screens

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.vocalfox.app.audio.VocalFoxSfxManager
import com.vocalfox.app.data.local.VoiceModelConfigEntity
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.VoicePreset
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxTokens
import com.vocalfox.app.ui.theme.VocalFoxType

@Composable
fun SettingsVoiceScreen(
    allPacks: Map<String, LanguagePack>,
    voiceConfigs: List<VoiceModelConfigEntity>,
    systemLang: SystemLang,
    isDarkMode: Boolean,
    strings: UiStrings,
    onSelectSystemLang: (SystemLang) -> Unit,
    onToggleDarkMode: (Boolean) -> Unit,
    onSelectVoicePreset: (String, VoicePreset) -> Unit,
    onPreviewVoice: (String, VoicePreset) -> Unit,
    selectedTargetLangCode: String = "es",
    onSelectTargetLang: (String) -> Unit = {}
) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("vocalfox_prefs", Context.MODE_PRIVATE) }
    var geminiApiKey by remember { mutableStateOf(prefs.getString("gemini_api_key", "").orEmpty()) }
    var keySavedToast by remember { mutableStateOf(false) }
    var sfxEnabled by remember { mutableStateOf(VocalFoxSfxManager.isSfxEnabled(context)) }

    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Active Language Course Switcher (Spanish / German)
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = if (isIt) "Corso di lingua attivo" else "Active language course",
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                allPacks.values.forEach { pack ->
                    val active = pack.languageCode == selectedTargetLangCode
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (active) colors.accent else colors.raised)
                            .clickable {
                                VocalFoxSfxManager.playTileTap(context)
                                onSelectTargetLang(pack.languageCode)
                            }
                            .padding(vertical = 14.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "${pack.languageCode.uppercase()} · ${pack.languageName.get(systemLang)}",
                            style = VocalFoxType.BodyMedium,
                            color = if (active) colors.onAccent else colors.primaryText
                        )
                    }
                }
            }
        }

        // Google Gemini Live AI API Key Configuration
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(
                text = "Google Gemini Live AI (API Key)",
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )
            Text(
                text = if (isIt) "Inserisci la tua API Key di Google AI Studio per la chat integrata (catena Fail-Fast 3.8-flash -> 2.5-flash -> hydrogen)." else "Enter your Google AI Studio API Key for in-app chat (Fail-Fast chain 3.8-flash -> 2.5-flash -> hydrogen).",
                style = VocalFoxType.SecondaryCaption,
                color = colors.secondaryText
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(10.dp))
                        .background(colors.raised)
                        .padding(horizontal = 12.dp, vertical = 12.dp)
                ) {
                    if (geminiApiKey.isEmpty()) {
                        Text("AIzaSy...", style = VocalFoxType.MetaMono, color = colors.mutedText)
                    }
                    BasicTextField(
                        value = geminiApiKey,
                        onValueChange = {
                            geminiApiKey = it
                            keySavedToast = false
                        },
                        textStyle = VocalFoxType.MetaMono.copy(color = colors.primaryText),
                        cursorBrush = SolidColor(colors.accent),
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(10.dp))
                        .background(colors.accent)
                        .clickable {
                            prefs.edit().putString("gemini_api_key", geminiApiKey.trim()).apply()
                            keySavedToast = true
                            VocalFoxSfxManager.playSuccess(context)
                        }
                        .padding(horizontal = 16.dp, vertical = 12.dp)
                ) {
                    Text(
                        text = if (keySavedToast) "Salvata ✓" else (if (isIt) "Salva" else "Save"),
                        style = VocalFoxType.BodyMedium,
                        color = colors.onAccent
                    )
                }
            }
        }

        // System UI Language Switcher
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = strings.systemLanguageSection,
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                SystemLang.entries.forEach { lang ->
                    val isSelected = lang == systemLang
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isSelected) colors.accent else colors.raised)
                            .clickable {
                                VocalFoxSfxManager.playTileTap(context)
                                onSelectSystemLang(lang)
                            }
                            .padding(vertical = 12.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = lang.displayName,
                            style = VocalFoxType.BodyMedium,
                            color = if (isSelected) colors.onAccent else colors.primaryText
                        )
                    }
                }
            }
        }

        // Dark Mode Toggle
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(horizontal = 18.dp, vertical = 14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = strings.appearanceSection,
                    style = VocalFoxType.SectionTitle,
                    color = colors.primaryText
                )
                Text(
                    text = strings.darkModeLabel,
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.secondaryText
                )
            }
            Switch(
                checked = isDarkMode,
                onCheckedChange = {
                    VocalFoxSfxManager.playTileTap(context)
                    onToggleDarkMode(it)
                },
                colors = SwitchDefaults.colors(
                    checkedThumbColor = colors.onAccent,
                    checkedTrackColor = colors.accent
                )
            )
        }

        // Procedural Sound Effects (SFX) Toggle
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(horizontal = 18.dp, vertical = 14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = if (isIt) "Effetti sonori (SFX)" else "Sound effects (SFX)",
                    style = VocalFoxType.SectionTitle,
                    color = colors.primaryText
                )
                Text(
                    text = if (isIt) "Suoni di feedback per risposte, bottoni e chat" else "Feedback sounds for answers, tiles, and chat",
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.secondaryText
                )
            }
            Switch(
                checked = sfxEnabled,
                onCheckedChange = { enabled ->
                    sfxEnabled = enabled
                    VocalFoxSfxManager.setSfxEnabled(context, enabled)
                },
                colors = SwitchDefaults.colors(
                    checkedThumbColor = colors.onAccent,
                    checkedTrackColor = colors.accent
                )
            )
        }

        // Clean Teacher Voice Picker
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Text(
                text = strings.voiceModelsSection,
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )

            allPacks.values.forEach { pack ->
                val activeVoiceId = voiceConfigs
                    .firstOrNull { it.languageCode == pack.languageCode }
                    ?.selectedVoiceId
                    ?: pack.availableVoices.first().voiceId

                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = pack.languageName.get(systemLang),
                        style = VocalFoxType.BodyMedium,
                        color = colors.accent
                    )

                    pack.availableVoices.forEach { preset ->
                        val isSelected = preset.voiceId == activeVoiceId
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(if (isSelected) colors.raised else colors.background)
                                .border(
                                    width = if (isSelected) 1.5.dp else 1.dp,
                                    color = if (isSelected) colors.accent else colors.hairline,
                                    shape = RoundedCornerShape(12.dp)
                                )
                                .clickable {
                                    VocalFoxSfxManager.playTileTap(context)
                                    onSelectVoicePreset(pack.languageCode, preset)
                                }
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Text(
                                    text = preset.displayName,
                                    style = VocalFoxType.BodyMedium,
                                    color = colors.primaryText
                                )
                                Text(
                                    text = "${preset.gender} · ${preset.timbre}",
                                    style = VocalFoxType.SecondaryCaption,
                                    color = colors.secondaryText
                                )
                            }

                            Row(
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(colors.card)
                                        .border(1.dp, colors.hairline, RoundedCornerShape(8.dp))
                                        .clickable { onPreviewVoice(pack.languageCode, preset) }
                                        .padding(8.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = strings.previewVoiceAction,
                                        tint = colors.primaryText,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                                if (isSelected) {
                                    Icon(
                                        imageVector = Icons.Outlined.Check,
                                        contentDescription = null,
                                        tint = colors.accent,
                                        modifier = Modifier.size(20.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(110.dp))
    }
}
"""
}


def find_project_root() -> Path | None:
    candidates = [
        Path(__file__).resolve().parent,
        Path.cwd(),
    ]
    for base in list(candidates):
        if base.exists():
            for child in base.iterdir():
                if child.is_dir():
                    candidates.append(child)

    for folder in candidates:
        if (folder / "settings.gradle.kts").exists():
            return folder
    return None


def main() -> None:
    root = find_project_root()
    if root is None:
        print("[ERRORE] Non riesco a trovare settings.gradle.kts!")
        return

    print(f"[Vocalfox Patch] Applicazione aggiornamenti su:\n  {root}\n")

    for rel_path, content in FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  + Aggiornato: {rel_path}")

    print("\n========================================================")
    print("PATCH APPLICATA CON SUCCESSO!")
    print("Esegui ora:")
    print("========================================================\n")
    print(f'cd "{root}"')
    print("git add -A")
    print('git commit -m "Feat: Add Fail-Fast Gemini Sticky fallback chain & procedural offline SFX engine"')
    print("git push origin main")


if __name__ == "__main__":
    main()
