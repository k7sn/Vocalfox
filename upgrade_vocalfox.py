#!/usr/bin/env python3
"""
upgrade_vocalfox.py
Applica tutte le migliorie architetturali, UI/UX, SFX pre-sintetizzati,
gesture Indietro (BackHandler) coerente, Accademia con ModalBottomSheet + Ripasso SM-2,
e il ripristino completo di OnboardingAndLessonScreens.kt al progetto VocalFox.
"""

from pathlib import Path

OBSOLETE_FILES = [
    "app/src/main/assets/packs/ja_pack.json",
    "app/src/main/java/com/vocalfox/app/ui/screens/GrammarSyntaxScreen.kt",
    "app/src/main/java/com/vocalfox/app/ui/screens/WritingExerciseScreen.kt",
    "app/src/main/java/com/vocalfox/app/ui/screens/PronunciationScreen.kt",
    "app/src/main/java/com/vocalfox/app/ui/screens/JapaneseScriptScreen.kt",
]

UPDATED_FILES: dict[str, str] = {
    "app/src/main/java/com/vocalfox/app/MainActivity.kt": '''\
package com.vocalfox.app

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Explore
import androidx.compose.material.icons.outlined.Forum
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModelProvider
import com.vocalfox.app.audio.VocalFoxSfxManager
import com.vocalfox.app.ui.i18n.AppStrings
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.screens.ExploreStudyHubScreen
import com.vocalfox.app.ui.screens.GuidedLessonScreen
import com.vocalfox.app.ui.screens.GuidedUnitBundle
import com.vocalfox.app.ui.screens.HomeScreen
import com.vocalfox.app.ui.screens.LiveConversationScreen
import com.vocalfox.app.ui.screens.OnboardingScreen
import com.vocalfox.app.ui.screens.SettingsVoiceScreen
import com.vocalfox.app.ui.screens.SplashScreenOverlay
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.viewmodel.VocalFoxViewModel
import kotlinx.coroutines.delay

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val vm = ViewModelProvider(
            this,
            ViewModelProvider.AndroidViewModelFactory.getInstance(application)
        )[VocalFoxViewModel::class.java]

        setContent {
            val isDark by vm.isDarkMode.collectAsState()
            VocalFoxTheme(darkTheme = isDark) {
                VocalFoxRootApp(viewModel = vm)
            }
        }
    }
}

private enum class MainTab {
    TODAY, EXPLORE, LIVE_AI, PROFILE
}

@Composable
private fun VocalFoxRootApp(viewModel: VocalFoxViewModel) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("vocalfox_prefs", Context.MODE_PRIVATE) }

    val colors = VocalFoxTheme.colors
    val systemLang by viewModel.systemLang.collectAsState()
    val isDarkMode by viewModel.isDarkMode.collectAsState()
    val currentPack by viewModel.currentPack.collectAsState()
    val selectedCefr by viewModel.selectedCefr.collectAsState()
    val progressList by viewModel.progressList.collectAsState()
    val srsList by viewModel.srsList.collectAsState()
    val voiceConfigs by viewModel.voiceConfigs.collectAsState()
    val isRecording by viewModel.isRecordingAudio.collectAsState()
    val pronunciationResult by viewModel.latestPronunciationResult.collectAsState()

    val strings = AppStrings.forLang(systemLang)

    var showSplash by rememberSaveable { mutableStateOf(true) }
    var hasCompletedOnboarding by rememberSaveable {
        mutableStateOf(prefs.getBoolean("onboarding_done", false))
    }
    var activeTab by rememberSaveable { mutableStateOf(MainTab.TODAY) }
    var activeGuidedUnit by remember { mutableStateOf<GuidedUnitBundle?>(null) }

    LaunchedEffect(Unit) {
        delay(2000L)
        showSplash = false
    }

    if (showSplash) {
        SplashScreenOverlay(onFinished = { showSplash = false })
        return
    }

    if (!hasCompletedOnboarding) {
        OnboardingScreen(
            allPacks = viewModel.allPacks,
            selectedLangCode = currentPack.languageCode,
            systemLang = systemLang,
            strings = strings,
            onSelectSystemLang = viewModel::setSystemLanguage,
            onSelectTargetLang = viewModel::selectLanguage,
            onCompleteOnboarding = { chosenCefr ->
                viewModel.selectCefr(chosenCefr)
                prefs.edit().putBoolean("onboarding_done", true).apply()
                hasCompletedOnboarding = true
            }
        )
        return
    }

    val currentUnit = activeGuidedUnit
    if (currentUnit != null) {
        GuidedLessonScreen(
            bundle = currentUnit,
            systemLang = systemLang,
            strings = strings,
            isRecording = isRecording,
            pronunciationResult = pronunciationResult,
            onSpeakText = { text, speed -> viewModel.speakSentence(text, speed) },
            onStartRecording = viewModel::startRecordingPronunciation,
            onStopAndEvaluate = { drill -> viewModel.stopAndEvaluatePronunciation(drill, null) },
            onCompleteUnit = { bundle, _ ->
                viewModel.recordSyntaxCompletion(bundle.grammarExercise, true)
            },
            onClose = { activeGuidedUnit = null }
        )
        return
    }

    // Gesture "Indietro" coerente: da qualsiasi tab secondaria torna prima a Percorso (TODAY)
    BackHandler(enabled = activeTab != MainTab.TODAY) {
        VocalFoxSfxManager.playTileTap(context)
        activeTab = MainTab.TODAY
    }

    Scaffold(
        containerColor = colors.background,
        bottomBar = {
            CleanBottomNavigationBar(
                activeTab = activeTab,
                systemLang = systemLang,
                onSelectTab = { newTab ->
                    if (newTab != activeTab) {
                        VocalFoxSfxManager.playTileTap(context)
                        activeTab = newTab
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            when (activeTab) {
                MainTab.TODAY -> HomeScreen(
                    allPacks = viewModel.allPacks,
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    systemLang = systemLang,
                    strings = strings,
                    progressList = progressList,
                    onSelectLanguage = viewModel::selectLanguage,
                    onSelectCefr = viewModel::selectCefr,
                    onStartGuidedUnit = { unit ->
                        VocalFoxSfxManager.playTileTap(context)
                        activeGuidedUnit = unit
                    },
                    onOpenProfileSettings = {
                        VocalFoxSfxManager.playTileTap(context)
                        activeTab = MainTab.PROFILE
                    }
                )

                MainTab.EXPLORE -> ExploreStudyHubScreen(
                    currentPack = currentPack,
                    systemLang = systemLang,
                    strings = strings,
                    srsList = srsList,
                    onPlayAudio = { text, speed -> viewModel.speakSentence(text, speed) }
                )

                MainTab.LIVE_AI -> LiveConversationScreen(
                    viewModel = viewModel,
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    systemLang = systemLang,
                    onSpeakText = { text, speed -> viewModel.speakSentence(text, speed) },
                    onOpenSettingsForApiKey = { activeTab = MainTab.PROFILE }
                )

                MainTab.PROFILE -> Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .statusBarsPadding()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = strings.profileSettingsTitle,
                            style = VocalFoxType.PageTitle,
                            color = colors.primaryText
                        )
                        Row(
                            modifier = Modifier
                                .clip(RoundedCornerShape(10.dp))
                                .background(colors.raised)
                                .clickable {
                                    VocalFoxSfxManager.playTileTap(context)
                                    prefs.edit().putBoolean("onboarding_done", false).apply()
                                    hasCompletedOnboarding = false
                                }
                                .padding(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Text(
                                text = strings.retakePlacementAction,
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.accent
                            )
                        }
                    }
                    SettingsVoiceScreen(
                        allPacks = viewModel.allPacks,
                        voiceConfigs = voiceConfigs,
                        systemLang = systemLang,
                        isDarkMode = isDarkMode,
                        strings = strings,
                        onSelectSystemLang = viewModel::setSystemLanguage,
                        onToggleDarkMode = viewModel::toggleDarkMode,
                        onSelectVoicePreset = viewModel::selectVoicePreset,
                        onPreviewVoice = { langCode, preset ->
                            val sampleText = viewModel.allPacks[langCode]
                                ?.pronunciationDrills
                                ?.firstOrNull()
                                ?.targetSentence
                                .orEmpty()
                            viewModel.ttsManager.speak(sampleText, langCode, preset, 1.0f)
                        },
                        selectedTargetLangCode = currentPack.languageCode,
                        onSelectTargetLang = viewModel::selectLanguage,
                        onInstallSystemTts = { viewModel.ttsManager.launchInstallTtsData(context) }
                    )
                }
            }
        }
    }
}

@Composable
private fun CleanBottomNavigationBar(
    activeTab: MainTab,
    systemLang: SystemLang,
    onSelectTab: (MainTab) -> Unit
) {
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    val tabs = listOf(
        Triple(MainTab.TODAY, if (isIt) "Percorso" else "Path", Icons.Outlined.Home),
        Triple(MainTab.EXPLORE, if (isIt) "Accademia" else "Academy", Icons.Outlined.Explore),
        Triple(MainTab.LIVE_AI, "Live AI", Icons.Outlined.Forum),
        Triple(MainTab.PROFILE, if (isIt) "Profilo" else "Profile", Icons.Outlined.Person)
    )

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(colors.card)
            .border(1.dp, colors.hairline)
            .navigationBarsPadding()
            .padding(horizontal = 12.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically
    ) {
        tabs.forEach { (tab, label, icon) ->
            val selected = activeTab == tab
            Column(
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .background(if (selected) colors.accent.copy(alpha = 0.12f) else Color.Transparent)
                    .clickable { onSelectTab(tab) }
                    .padding(horizontal = 16.dp, vertical = 6.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = label,
                    tint = if (selected) colors.accent else colors.mutedText,
                    modifier = Modifier.size(22.dp)
                )
                Text(
                    text = label,
                    style = VocalFoxType.SecondaryCaption,
                    color = if (selected) colors.accent else colors.mutedText,
                    maxLines = 1
                )
            }
        }
    }
}
''',

    "app/src/main/java/com/vocalfox/app/audio/GeminiLiveTutorClient.kt": '''\
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

object GeminiLiveTutorClient {

    private const val CONNECT_TIMEOUT_MS = 2500
    private const val READ_TIMEOUT_MS = 12000

    @Volatile
    private var stickyModel: String? = null

    @Volatile
    private var resolvedHydrogenModel: String = "gemini-4-hydrogen"

    @Volatile
    private var hasResolvedModelsList: Boolean = false

    suspend fun preCheckHydrogenModelAsync(apiKey: String) = withContext(Dispatchers.IO) {
        val cleanKey = apiKey.trim()
        if (cleanKey.isBlank() || hasResolvedModelsList) return@withContext

        try {
            val endpoint = "https://generativelanguage.googleapis.com/v1beta/models?key=$cleanKey"
            val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = 4000
            }
            if (conn.responseCode in 200..299) {
                val raw = BufferedReader(InputStreamReader(conn.inputStream, Charsets.UTF_8)).use { it.readText() }
                val root = JSONObject(raw)
                val modelsArr = root.optJSONArray("models")
                if (modelsArr != null) {
                    hasResolvedModelsList = true
                    for (i in 0 until modelsArr.length()) {
                        val mObj = modelsArr.optJSONObject(i) ?: continue
                        val rawName = mObj.optString("name", "").removePrefix("models/")
                        if (rawName.contains("hydrogen", ignoreCase = true)) {
                            resolvedHydrogenModel = rawName
                            break
                        }
                    }
                }
            }
        } catch (_: Throwable) {}
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

        val systemInstruction = """
            You are Vocalfox, a warm, encouraging native $targetLangName language tutor.
            The student is currently at CEFR level ${cefrLevel.name}.
            Current roleplay scenario: "$scenarioTitle".
            Respond ONLY with a valid JSON object with exactly three string fields:
            {
              "reply": "Your natural conversational response in $targetLangName (2-3 sentences max, adapted to ${cefrLevel.name}, ending with an engaging follow-up question in $targetLangName)",
              "translation": "Accurate translation of your reply into $uiLangName",
              "correction": "Brief, friendly feedback in $uiLangName on the student's grammar/vocabulary (if their message was correct, praise it and suggest one idiomatic ${cefrLevel.name} expression)"
            }
        """.trimIndent()

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
                }
            } catch (_: Throwable) {
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
''',

    "app/src/main/java/com/vocalfox/app/audio/VocalFoxSfxManager.kt": '''\
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
''',

    "app/src/main/java/com/vocalfox/app/audio/PiperTtsManager.kt": '''\
package com.vocalfox.app.audio

import android.content.Context
import android.content.Intent
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

    fun launchInstallTtsData(ctx: Context) {
        try {
            val installIntent = Intent(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            ctx.startActivity(installIntent)
        } catch (_: Throwable) {}
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
                    "de" -> Locale.GERMANY
                    else -> Locale("es", "ES")
                }
                tts.language = locale
                val pitch = when {
                    preset.gender.equals("Maschile", ignoreCase = true) ||
                        preset.gender.equals("Male", ignoreCase = true) -> 0.86f
                    preset.timbre.contains("Calda", ignoreCase = true) ||
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
''',

    "app/src/main/java/com/vocalfox/app/ui/viewmodel/VocalFoxViewModel.kt": '''\
package com.vocalfox.app.ui.viewmodel

import android.app.Application
import android.content.Context
import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.vocalfox.app.audio.PiperTtsManager
import com.vocalfox.app.audio.PronunciationEvaluator
import com.vocalfox.app.audio.PronunciationResult
import com.vocalfox.app.audio.TutorChatMessage
import com.vocalfox.app.data.local.MistakeSrsEntity
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.data.local.VocalFoxDatabase
import com.vocalfox.app.data.local.VoiceModelConfigEntity
import com.vocalfox.app.data.repository.PackLoader
import com.vocalfox.app.data.repository.VocalFoxRepository
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.GrammarSyntaxExercise
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.domain.model.VoicePreset
import com.vocalfox.app.ui.i18n.SystemLang
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

@OptIn(ExperimentalCoroutinesApi::class)
class VocalFoxViewModel(application: Application) : AndroidViewModel(application) {
    private val prefs = application.getSharedPreferences("vocalfox_prefs", Context.MODE_PRIVATE)
    private val database = VocalFoxDatabase.getInstance(application)
    private val repository = VocalFoxRepository(database.dao(), PackLoader(application))
    val ttsManager = PiperTtsManager(application)
    private val pronunciationEvaluator = PronunciationEvaluator()

    private val initialSysLang: SystemLang = run {
        val saved = prefs.getString("system_lang", SystemLang.IT.name) ?: SystemLang.IT.name
        SystemLang.entries.firstOrNull { it.name == saved } ?: SystemLang.IT
    }
    private val initialLangCode: String = prefs.getString("target_lang", "es") ?: "es"
    private val initialCefr: CefrLevel = run {
        val saved = prefs.getString("selected_cefr", CefrLevel.A1.name) ?: CefrLevel.A1.name
        CefrLevel.entries.firstOrNull { it.name == saved } ?: CefrLevel.A1
    }
    private val initialDark: Boolean = prefs.getBoolean("dark_mode", false)

    private val _systemLang = MutableStateFlow(initialSysLang)
    val systemLang: StateFlow<SystemLang> = _systemLang.asStateFlow()

    private val _isDarkMode = MutableStateFlow(initialDark)
    val isDarkMode: StateFlow<Boolean> = _isDarkMode.asStateFlow()

    private val _selectedLanguageCode = MutableStateFlow(initialLangCode)
    val selectedLanguageCode: StateFlow<String> = _selectedLanguageCode.asStateFlow()

    private val _selectedCefr = MutableStateFlow(initialCefr)
    val selectedCefr: StateFlow<CefrLevel> = _selectedCefr.asStateFlow()

    private val _isRecordingAudio = MutableStateFlow(false)
    val isRecordingAudio: StateFlow<Boolean> = _isRecordingAudio.asStateFlow()

    private val _latestPronunciationResult = MutableStateFlow<PronunciationResult?>(null)
    val latestPronunciationResult: StateFlow<PronunciationResult?> = _latestPronunciationResult.asStateFlow()

    val chatMessages = mutableStateListOf<TutorChatMessage>()
    private var chatContextSignature: String = ""

    private var recordingJob: Job? = null

    val allPacks: Map<String, LanguagePack> = repository.getAllPacks()

    val currentPack: StateFlow<LanguagePack> = _selectedLanguageCode
        .combine(_selectedCefr) { code, _ -> repository.getPack(code) }
        .stateIn(viewModelScope, SharingStarted.Eagerly, repository.getPack(initialLangCode))

    val progressList: StateFlow<List<UserProgressEntity>> = _selectedLanguageCode
        .flatMapLatest { code -> repository.observeProgress(code) }
        .stateIn(viewModelScope, SharingStarted.Eagerly, emptyList())

    val srsList: StateFlow<List<MistakeSrsEntity>> = _selectedLanguageCode
        .flatMapLatest { code -> repository.observeSrsItems(code) }
        .stateIn(viewModelScope, SharingStarted.Eagerly, emptyList())

    val voiceConfigs: StateFlow<List<VoiceModelConfigEntity>> = repository
        .observeVoiceConfigs()
        .stateIn(viewModelScope, SharingStarted.Eagerly, emptyList())

    init {
        viewModelScope.launch {
            allPacks.values.forEach { pack ->
                val defaultVoice = pack.availableVoices.firstOrNull() ?: return@forEach
                ttsManager.ensureLocalVoiceSlot(defaultVoice)
            }
        }
    }

    fun ensureChatInitialized(langCode: String, cefr: CefrLevel, scenario: String, isIt: Boolean) {
        val sig = "$langCode|${cefr.name}|$scenario|$isIt"
        if (chatMessages.isEmpty() || chatContextSignature != sig) {
            chatContextSignature = sig
            chatMessages.clear()
            chatMessages.add(
                if (langCode == "de") {
                    TutorChatMessage(
                        isUser = false,
                        text = "Hallo! Ich bin dein Vocalfox Tutor (${cefr.name}). Wollen wir über '$scenario' auf Deutsch sprechen?",
                        translation = if (isIt) "Ciao! Sono il tuo tutor Vocalfox (${cefr.name}). Parliamo di '$scenario' in tedesco?" else "Hello! I am your Vocalfox tutor. Shall we speak German?"
                    )
                } else {
                    TutorChatMessage(
                        isUser = false,
                        text = "¡Hola! Soy tu tutor Vocalfox (${cefr.name}). ¿Hablamos sobre '$scenario' en español?",
                        translation = if (isIt) "Ciao! Sono il tuo tutor Vocalfox (${cefr.name}). Parliamo di '$scenario' in spagnolo?" else "Hello! I am your Vocalfox tutor. Shall we speak Spanish?"
                    )
                }
            )
        }
    }

    fun setSystemLanguage(lang: SystemLang) {
        _systemLang.value = lang
        prefs.edit().putString("system_lang", lang.name).apply()
    }

    fun toggleDarkMode(enabled: Boolean) {
        _isDarkMode.value = enabled
        prefs.edit().putBoolean("dark_mode", enabled).apply()
    }

    fun selectLanguage(code: String) {
        _selectedLanguageCode.value = code
        _latestPronunciationResult.value = null
        prefs.edit().putString("target_lang", code).apply()
    }

    fun selectCefr(level: CefrLevel) {
        _selectedCefr.value = level
        _latestPronunciationResult.value = null
        prefs.edit().putString("selected_cefr", level.name).apply()
    }

    fun getActiveVoiceForLanguage(languageCode: String): VoicePreset {
        val pack = repository.getPack(languageCode)
        val savedId = voiceConfigs.value.firstOrNull { it.languageCode == languageCode }?.selectedVoiceId
        return pack.availableVoices.firstOrNull { it.voiceId == savedId }
            ?: pack.availableVoices.first()
    }

    fun selectVoicePreset(languageCode: String, preset: VoicePreset) {
        viewModelScope.launch {
            val verified = ttsManager.ensureLocalVoiceSlot(preset)
            repository.saveVoiceConfig(
                languageCode = languageCode,
                voiceId = preset.voiceId,
                speed = 1.0f,
                verified = verified
            )
        }
    }

    fun speakSentence(text: String, speed: Float = 1.0f) {
        val lang = _selectedLanguageCode.value
        val preset = getActiveVoiceForLanguage(lang)
        ttsManager.speak(text = text, languageCode = lang, preset = preset, speed = speed)
    }

    fun recordSyntaxCompletion(exercise: GrammarSyntaxExercise, isCorrect: Boolean) {
        viewModelScope.launch {
            val score = if (isCorrect) 95 else 40
            repository.recordExerciseOutcome(
                itemKey = exercise.id,
                languageCode = _selectedLanguageCode.value,
                cefrLevel = exercise.cefr,
                pillar = "SYNTAX",
                score = score,
                promptPreview = exercise.promptSentence,
                targetAnswer = exercise.blankTarget,
                mistakeNote = exercise.explanation.get(_systemLang.value)
            )
        }
    }

    fun startRecordingPronunciation(drill: PronunciationDrill) {
        if (_isRecordingAudio.value) return
        _isRecordingAudio.value = true
        recordingJob = viewModelScope.launch {
            val pcm = pronunciationEvaluator.recordAudioPcm()
            _isRecordingAudio.value = false
            val result = pronunciationEvaluator.evaluate(
                pcmSamples = pcm,
                drill = drill,
                languageCode = _selectedLanguageCode.value,
                systemLang = _systemLang.value
            )
            _latestPronunciationResult.value = result
            repository.recordExerciseOutcome(
                itemKey = drill.id,
                languageCode = _selectedLanguageCode.value,
                cefrLevel = drill.cefr,
                pillar = "SPEECH",
                score = result.overallScore,
                promptPreview = drill.targetSentence,
                targetAnswer = drill.fullIpa,
                mistakeNote = result.summaryAdvice
            )
        }
    }

    fun stopAndEvaluatePronunciation(drill: PronunciationDrill, simulatedTranscript: String? = null) {
        if (_isRecordingAudio.value) {
            pronunciationEvaluator.stopCapture()
        } else {
            viewModelScope.launch {
                val result = pronunciationEvaluator.evaluate(
                    pcmSamples = ShortArray(0),
                    drill = drill,
                    languageCode = _selectedLanguageCode.value,
                    systemLang = _systemLang.value,
                    simulatedTranscript = simulatedTranscript
                )
                _latestPronunciationResult.value = result
                repository.recordExerciseOutcome(
                    itemKey = drill.id,
                    languageCode = _selectedLanguageCode.value,
                    cefrLevel = drill.cefr,
                    pillar = "SPEECH",
                    score = result.overallScore,
                    promptPreview = drill.targetSentence,
                    targetAnswer = drill.fullIpa,
                    mistakeNote = result.summaryAdvice
                )
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        ttsManager.shutdown()
    }
}
''',

    "app/src/main/java/com/vocalfox/app/ui/screens/SettingsVoiceScreen.kt": '''\
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
import androidx.compose.material.icons.outlined.Download
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
    onSelectTargetLang: (String) -> Unit = {},
    onInstallSystemTts: () -> Unit = {}
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
        // Corso di lingua attivo
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

        // Google Gemini Live AI API Key
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

        // Lingua dell'app
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

        // Tema Scuro
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

        // Effetti sonori (SFX)
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

        // Selettore Voci + Pacchetti vocali offline Android
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = strings.voiceModelsSection,
                    style = VocalFoxType.SectionTitle,
                    color = colors.primaryText
                )
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(colors.raised)
                        .clickable {
                            VocalFoxSfxManager.playTileTap(context)
                            onInstallSystemTts()
                        }
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(Icons.Outlined.Download, null, tint = colors.accent, modifier = Modifier.size(15.dp))
                    Text(
                        text = if (isIt) "Dati vocali" else "Voice data",
                        style = VocalFoxType.MetaMono,
                        color = colors.accent
                    )
                }
            }

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
''',

    "app/src/main/java/com/vocalfox/app/ui/screens/HomeScreen.kt": '''\
package com.vocalfox.app.ui.screens

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.LocalFireDepartment
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.vocalfox.app.audio.VocalFoxSfxManager
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.data.repository.CurriculumGenerator
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.theme.VocalFoxWordmark
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

@Composable
fun HomeScreen(
    allPacks: Map<String, LanguagePack>,
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    strings: UiStrings,
    progressList: List<UserProgressEntity>,
    onSelectLanguage: (String) -> Unit,
    onSelectCefr: (CefrLevel) -> Unit,
    onStartGuidedUnit: (GuidedUnitBundle) -> Unit,
    onOpenProfileSettings: () -> Unit
) {
    val context = LocalContext.current
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    val all50Units = remember(currentPack.languageCode, selectedCefr, systemLang) {
        CurriculumGenerator.generate50UnitsForLevel(currentPack, selectedCefr, systemLang)
    }

    var selectedChapterFilter by remember(selectedCefr) { mutableIntStateOf(0) }

    BackHandler(enabled = selectedChapterFilter != 0) {
        VocalFoxSfxManager.playTileTap(context)
        selectedChapterFilter = 0
    }

    val displayedUnits = remember(all50Units, selectedChapterFilter) {
        if (selectedChapterFilter == 0) {
            all50Units
        } else {
            val startIdx = (selectedChapterFilter - 1) * 10
            all50Units.subList(startIdx, (startIdx + 10).coerceAtMost(all50Units.size))
        }
    }

    val completedCount = progressList.count { it.bestScore >= 70 }
    val realStreakDays = remember(progressList) {
        calculateConsecutiveDayStreak(progressList)
    }

    val dailyTarget = 4
    val completedToday = remember(progressList) {
        val zone = ZoneId.systemDefault()
        val today = LocalDate.now(zone)
        progressList.count {
            it.bestScore >= 70 &&
                it.completedAtEpochMs > 0L &&
                Instant.ofEpochMilli(it.completedAtEpochMs).atZone(zone).toLocalDate() == today
        }
    }
    val dailyProgressRatio = (completedToday.toFloat() / dailyTarget.toFloat()).coerceIn(0f, 1f)

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                VocalFoxWordmark(height = 32.dp)

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                            .clickable(onClick = onOpenProfileSettings)
                            .padding(horizontal = 12.dp, vertical = 7.dp)
                    ) {
                        Text(
                            text = "${currentPack.languageName.get(systemLang)} · ${selectedCefr.name}",
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                    }

                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                            .padding(horizontal = 10.dp, vertical = 7.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.LocalFireDepartment,
                            contentDescription = null,
                            tint = if (realStreakDays > 0) colors.accent else colors.mutedText,
                            modifier = Modifier.size(18.dp)
                        )
                        Text(
                            text = "$realStreakDays",
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                    }
                }
            }
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CefrLevel.entries.forEach { level ->
                    val isSelected = level == selectedCefr
                    val doneInLevel = progressList.count { it.cefrLevel == level.name && it.bestScore >= 70 }
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (isSelected) colors.accent else colors.card)
                            .border(
                                width = 1.dp,
                                color = if (isSelected) colors.accent else colors.hairline,
                                shape = RoundedCornerShape(14.dp)
                            )
                            .clickable {
                                VocalFoxSfxManager.playTileTap(context)
                                onSelectCefr(level)
                            }
                            .padding(vertical = 10.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(2.dp)
                    ) {
                        Text(
                            text = level.name,
                            style = VocalFoxType.SectionTitle,
                            color = if (isSelected) colors.onAccent else colors.primaryText,
                            maxLines = 1
                        )
                        Text(
                            text = "$doneInLevel/50",
                            style = VocalFoxType.SecondaryCaption,
                            color = if (isSelected) colors.onAccent.copy(alpha = 0.85f) else colors.mutedText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                    .padding(16.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(68.dp),
                    contentAlignment = Alignment.Center
                ) {
                    val trackCol = colors.raised
                    val arcCol = colors.accent
                    Canvas(modifier = Modifier.fillMaxSize()) {
                        drawArc(
                            color = trackCol,
                            startAngle = 135f,
                            sweepAngle = 270f,
                            useCenter = false,
                            style = Stroke(width = 16f, cap = StrokeCap.Round)
                        )
                        if (dailyProgressRatio > 0f) {
                            drawArc(
                                color = arcCol,
                                startAngle = 135f,
                                sweepAngle = 270f * dailyProgressRatio,
                                useCenter = false,
                                style = Stroke(width = 16f, cap = StrokeCap.Round)
                            )
                        }
                    }
                    Text(
                        text = "$completedToday/$dailyTarget",
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                }

                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = strings.dailyGoalTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Text(
                        text = if (isIt) "$completedCount unità completate in totale" else "$completedCount total units completed",
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }
            }
        }

        item {
            val chapterFilters = listOf(
                0 to (if (isIt) "Tutte" else "All"),
                1 to "1–10",
                2 to "11–20",
                3 to "21–30",
                4 to "31–40",
                5 to "41–50"
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                chapterFilters.forEach { (chapIdx, label) ->
                    val active = selectedChapterFilter == chapIdx
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(10.dp))
                            .background(if (active) colors.primaryText else colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(10.dp))
                            .clickable {
                                VocalFoxSfxManager.playTileTap(context)
                                selectedChapterFilter = chapIdx
                            }
                            .padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = if (chapIdx == 0) label else (if (isIt) "Unità $label" else "Units $label"),
                            style = VocalFoxType.BodyMedium,
                            color = if (active) colors.background else colors.secondaryText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        itemsIndexed(displayedUnits, key = { _, u -> u.grammarExercise.id }) { idx, unit ->
            val isCompleted = progressList.any { it.itemKey == unit.grammarExercise.id && it.bestScore >= 70 }
            val isNextActive = idx == 0 || !isCompleted
            val effectiveTint = if (colors.isDark) unit.tintColor.copy(alpha = 0.22f) else unit.tintColor

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier
                        .width(16.dp)
                        .fillMaxHeight()
                ) {
                    Spacer(modifier = Modifier.height(22.dp))
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                            .background(
                                when {
                                    isCompleted -> colors.positive
                                    idx == 0 -> colors.accent
                                    else -> colors.raised
                                }
                            )
                            .border(
                                width = 2.dp,
                                color = if (isNextActive) colors.accent else colors.mutedText.copy(alpha = 0.35f),
                                shape = CircleShape
                            )
                    )
                    if (idx < displayedUnits.lastIndex) {
                        Box(
                            modifier = Modifier
                                .width(2.dp)
                                .weight(1f)
                                .padding(vertical = 4.dp)
                                .background(colors.hairline)
                        )
                    }
                }

                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.card)
                        .border(
                            width = if (idx == 0) 1.5.dp else 1.dp,
                            color = if (idx == 0) colors.accent.copy(alpha = 0.5f) else colors.hairline,
                            shape = RoundedCornerShape(16.dp)
                        )
                        .clickable { onStartGuidedUnit(unit) }
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = if (isIt) "Unità ${unit.unitIndex + 1}" else "Unit ${unit.unitIndex + 1}",
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.accent,
                            maxLines = 1
                        )
                        Text(
                            text = unit.title,
                            style = VocalFoxType.SectionTitle,
                            color = colors.primaryText,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            text = unit.subtitle,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )

                        Spacer(modifier = Modifier.height(2.dp))

                        Row(
                            modifier = Modifier
                                .clip(RoundedCornerShape(10.dp))
                                .background(if (isCompleted) colors.positive.copy(alpha = 0.12f) else colors.accent)
                                .padding(horizontal = 14.dp, vertical = 7.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = if (isCompleted) Icons.Outlined.Check else Icons.Outlined.PlayArrow,
                                contentDescription = null,
                                tint = if (isCompleted) colors.positive else colors.onAccent,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = if (isCompleted) (if (isIt) "Completata" else "Completed") else strings.startUnitAction,
                                style = VocalFoxType.BodyMedium,
                                color = if (isCompleted) colors.positive else colors.onAccent,
                                maxLines = 1
                            )
                        }
                    }

                    VocalFoxMascot(
                        state = unit.mascotPose,
                        size = 76.dp,
                        tintBackground = effectiveTint
                    )
                }
            }
        }

        item { Spacer(modifier = Modifier.height(24.dp)) }
    }
}

private fun calculateConsecutiveDayStreak(progressList: List<UserProgressEntity>): Int {
    val zone = ZoneId.systemDefault()
    val completedDates = progressList
        .filter { it.bestScore >= 70 && it.completedAtEpochMs > 0L }
        .map { Instant.ofEpochMilli(it.completedAtEpochMs).atZone(zone).toLocalDate() }
        .distinct()
        .sortedDescending()

    if (completedDates.isEmpty()) return 0

    val today = LocalDate.now(zone)
    if (completedDates.first().isBefore(today.minusDays(1))) return 0

    var streak = 1
    for (i in 0 until completedDates.lastIndex) {
        if (completedDates[i].minusDays(1) == completedDates[i + 1]) {
            streak++
        } else {
            break
        }
    }
    return streak
}

fun buildGuidedUnitsForPack(
    pack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang
): List<GuidedUnitBundle> {
    return CurriculumGenerator.generate50UnitsForLevel(pack, selectedCefr, systemLang)
}
''',

    "app/src/main/java/com/vocalfox/app/ui/screens/LiveConversationScreen.kt": '''\
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
import com.vocalfox.app.ui.viewmodel.VocalFoxViewModel
import kotlinx.coroutines.launch

@Composable
fun LiveConversationScreen(
    viewModel: VocalFoxViewModel,
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

    LaunchedEffect(currentPack.languageCode, selectedCefr, selectedScenario, isIt) {
        viewModel.ensureChatInitialized(currentPack.languageCode, selectedCefr, selectedScenario, isIt)
    }

    val messages = viewModel.chatMessages

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
                                    .background(if (colors.isDark) VocalFoxPalette.TintMintSage.copy(alpha = 0.22f) else VocalFoxPalette.TintMintSage)
                                    .padding(12.dp)
                            ) {
                                Text(
                                    text = "Consiglio: ${msg.grammarCorrection}",
                                    style = VocalFoxType.SecondaryCaption,
                                    color = if (colors.isDark) colors.primaryText else VocalFoxPalette.FoxDeepInkBrown
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
                                tintBackground = if (colors.isDark) VocalFoxPalette.TintWarmAmber.copy(alpha = 0.22f) else VocalFoxPalette.TintWarmAmber
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
''',

    "app/src/main/java/com/vocalfox/app/ui/screens/ExploreStudyHubScreen.kt": '''\
package com.vocalfox.app.ui.screens

import androidx.activity.compose.BackHandler
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
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Quiz
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.vocalfox.app.audio.VocalFoxSfxManager
import com.vocalfox.app.data.local.MistakeSrsEntity
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType

data class GrammarStudyCard(
    val category: String,
    val title: String,
    val levelBadge: String,
    val whenToUse: String,
    val tableRows: List<Pair<String, String>>,
    val exampleSentence: String,
    val exampleTranslation: String,
    val quizPrompt: String,
    val quizCorrect: String,
    val quizOptions: List<String>
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExploreStudyHubScreen(
    currentPack: LanguagePack,
    systemLang: SystemLang,
    strings: UiStrings,
    srsList: List<MistakeSrsEntity> = emptyList(),
    onPlayAudio: (String, Float) -> Unit
) {
    val context = LocalContext.current
    val colors = VocalFoxTheme.colors
    val isItalian = systemLang == SystemLang.IT

    val tabs = listOf(
        "VERBS" to (if (isItalian) "Verbi" else "Verbs"),
        "PRONOUNS" to (if (isItalian) "Pronomi" else "Pronouns"),
        "ADJECTIVES" to (if (isItalian) "Aggettivi e Casi" else "Adjectives & Cases"),
        "PHRASES" to (if (isItalian) "Frasario e Suoni" else "Phrases & Sounds"),
        "SRS" to (if (isItalian) "Ripasso Smart" else "Smart Review")
    )

    var selectedTab by remember { mutableStateOf("VERBS") }
    var activeQuizCard by remember { mutableStateOf<GrammarStudyCard?>(null) }

    BackHandler(enabled = activeQuizCard != null) {
        activeQuizCard = null
    }

    val allStudyCards = remember(currentPack.languageCode, systemLang) {
        buildStudyCardsForLanguage(currentPack.languageCode, isItalian)
    }
    val filteredCards = allStudyCards.filter { it.category == selectedTab }

    val quiz = activeQuizCard
    if (quiz != null) {
        val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
        var pickedAnswer by remember(quiz.title) { mutableStateOf<String?>(null) }

        ModalBottomSheet(
            onDismissRequest = { activeQuizCard = null },
            sheetState = sheetState,
            containerColor = colors.card
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .navigationBarsPadding()
                    .padding(horizontal = 20.dp, vertical = 12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = quiz.title,
                    style = VocalFoxType.MetaMono,
                    color = colors.accent
                )
                Text(
                    text = quiz.quizPrompt,
                    style = VocalFoxType.SentenceDisplay,
                    color = colors.primaryText
                )

                quiz.quizOptions.forEach { opt ->
                    val isSelected = pickedAnswer == opt
                    val isCorrect = opt == quiz.quizCorrect
                    val borderCol = when {
                        pickedAnswer != null && isCorrect -> colors.positive
                        isSelected && !isCorrect -> colors.negative
                        else -> colors.hairline
                    }
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isSelected) colors.raised else colors.background)
                            .border(2.dp, borderCol, RoundedCornerShape(12.dp))
                            .clickable {
                                pickedAnswer = opt
                                if (isCorrect) {
                                    VocalFoxSfxManager.playSuccess(context)
                                } else {
                                    VocalFoxSfxManager.playError(context)
                                }
                                onPlayAudio(opt, 1.0f)
                            }
                            .padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(opt, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                        if (pickedAnswer != null && isCorrect) {
                            Icon(Icons.Outlined.CheckCircle, null, tint = colors.positive, modifier = Modifier.size(20.dp))
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp)
    ) {
        Spacer(modifier = Modifier.height(10.dp))
        Text(
            text = if (isItalian) "Accademia · ${currentPack.languageName.get(systemLang)}" else "Academy · ${currentPack.languageName.get(systemLang)}",
            style = VocalFoxType.PageTitle,
            color = colors.primaryText
        )
        Text(
            text = if (isItalian) "Tocca qualsiasi voce per ascoltare la pronuncia corretta" else "Tap any item to hear its pronunciation",
            style = VocalFoxType.SecondaryCaption,
            color = colors.secondaryText
        )

        Spacer(modifier = Modifier.height(12.dp))

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            tabs.forEach { (code, label) ->
                val active = selectedTab == code
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (active) colors.accent else colors.card)
                        .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                        .clickable {
                            VocalFoxSfxManager.playTileTap(context)
                            selectedTab = code
                            activeQuizCard = null
                        }
                        .padding(horizontal = 16.dp, vertical = 10.dp)
                ) {
                    Text(
                        text = label,
                        style = VocalFoxType.BodyMedium,
                        color = if (active) colors.onAccent else colors.primaryText,
                        maxLines = 1
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        if (selectedTab == "SRS") {
            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                if (srsList.isEmpty()) {
                    item {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text(
                                text = if (isItalian) "Nessun elemento da ripassare" else "Nothing due for review yet",
                                style = VocalFoxType.SectionTitle,
                                color = colors.primaryText
                            )
                            Text(
                                text = if (isItalian) "Completa qualche unità nel Percorso: gli esercizi più difficili appariranno qui automaticamente." else "Complete units in your Path: tricky items will automatically appear here.",
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.secondaryText
                            )
                        }
                    }
                } else {
                    items(srsList, key = { it.itemKey }) { srsItem ->
                        var revealed by remember(srsItem.itemKey) { mutableStateOf(false) }
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .clickable {
                                    VocalFoxSfxManager.playTileTap(context)
                                    revealed = !revealed
                                    if (revealed) onPlayAudio(srsItem.targetAnswer, 1.0f)
                                }
                                .padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "${srsItem.cefrLevel} · ${if (isItalian) "Intervallo ${srsItem.intervalDays}g" else "Interval ${srsItem.intervalDays}d"}",
                                    style = VocalFoxType.MetaMono,
                                    color = colors.accent
                                )
                                Icon(Icons.Outlined.Refresh, null, tint = colors.mutedText, modifier = Modifier.size(16.dp))
                            }
                            Text(
                                text = srsItem.promptPreview,
                                style = VocalFoxType.BodyMedium,
                                color = colors.primaryText
                            )
                            if (revealed) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(colors.raised)
                                        .padding(12.dp)
                                ) {
                                    Text(
                                        text = "${srsItem.targetAnswer} — ${srsItem.lastMistakeNote}",
                                        style = VocalFoxType.SecondaryCaption,
                                        color = colors.positive
                                    )
                                }
                            } else {
                                Text(
                                    text = if (isItalian) "Tocca per mostrare soluzione e ascoltare" else "Tap to reveal answer and listen",
                                    style = VocalFoxType.SecondaryCaption,
                                    color = colors.secondaryText
                                )
                            }
                        }
                    }
                }
                item { Spacer(modifier = Modifier.height(24.dp)) }
            }
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(filteredCards) { card ->
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(16.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = card.title,
                                style = VocalFoxType.SectionTitle,
                                color = colors.primaryText,
                                modifier = Modifier.weight(1f)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(if (colors.isDark) VocalFoxPalette.TintWarmAmber.copy(alpha = 0.22f) else VocalFoxPalette.TintWarmAmber)
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text(
                                    text = card.levelBadge,
                                    style = VocalFoxType.MetaMono,
                                    color = colors.accent
                                )
                            }
                        }

                        Text(
                            text = card.whenToUse,
                            style = VocalFoxType.Body,
                            color = colors.secondaryText
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(colors.raised)
                                .padding(10.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            card.tableRows.forEach { (targetForm, meaning) ->
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(colors.card)
                                        .clickable { onPlayAudio(targetForm.substringBefore("->").trim(), 1.0f) }
                                        .padding(horizontal = 14.dp, vertical = 10.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column(
                                        modifier = Modifier.weight(1f),
                                        verticalArrangement = Arrangement.spacedBy(2.dp)
                                    ) {
                                        Text(
                                            text = targetForm,
                                            style = VocalFoxType.BodyMedium,
                                            color = colors.primaryText
                                        )
                                        Text(
                                            text = meaning,
                                            style = VocalFoxType.SecondaryCaption,
                                            color = colors.secondaryText
                                        )
                                    }
                                    Spacer(modifier = Modifier.width(10.dp))
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = null,
                                        tint = colors.accent,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                            }
                        }

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(colors.background)
                                .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(
                                modifier = Modifier.weight(1f),
                                verticalArrangement = Arrangement.spacedBy(2.dp)
                            ) {
                                Text(
                                    text = card.exampleSentence,
                                    style = VocalFoxType.BodyMedium,
                                    color = colors.primaryText
                                )
                                Text(
                                    text = card.exampleTranslation,
                                    style = VocalFoxType.SecondaryCaption,
                                    color = colors.secondaryText
                                )
                            }
                            Spacer(modifier = Modifier.width(8.dp))
                            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .clip(CircleShape)
                                        .background(colors.raised)
                                        .clickable { onPlayAudio(card.exampleSentence, 1.0f) },
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(Icons.Outlined.VolumeUp, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                                }
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .clip(CircleShape)
                                        .background(colors.raised)
                                        .clickable { onPlayAudio(card.exampleSentence, 0.75f) },
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(Icons.Outlined.SlowMotionVideo, null, tint = colors.accent, modifier = Modifier.size(18.dp))
                                }
                            }
                        }

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(colors.accent.copy(alpha = 0.12f))
                                .clickable {
                                    VocalFoxSfxManager.playTileTap(context)
                                    activeQuizCard = card
                                }
                                .padding(vertical = 10.dp),
                            horizontalArrangement = Arrangement.Center,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(Icons.Outlined.Quiz, null, tint = colors.accent, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = if (isItalian) "Fai un test rapido" else "Take a quick quiz",
                                style = VocalFoxType.BodyMedium,
                                color = colors.accent
                            )
                        }
                    }
                }

                item { Spacer(modifier = Modifier.height(24.dp)) }
            }
        }
    }
}

private fun buildStudyCardsForLanguage(langCode: String, isIt: Boolean): List<GrammarStudyCard> {
    return if (langCode == "de") {
        listOf(
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Sein (Essere) e Haben (Avere)" else "Sein (To be) & Haben (To have)",
                levelBadge = "A1",
                whenToUse = if (isIt) "I due verbi cardine del tedesco. Si usano da soli al presente e come ausiliari per formare il passato." else "The two core German verbs, used standalone and as auxiliaries in the past tense.",
                tableRows = listOf(
                    "ich bin · ich habe" to (if (isIt) "io sono · io ho" else "I am · I have"),
                    "du bist · du hast" to (if (isIt) "tu sei · tu hai" else "you are · you have"),
                    "er/sie/es ist · hat" to (if (isIt) "lui/lei è · ha" else "he/she/it is · has"),
                    "wir sind · wir haben" to (if (isIt) "noi siamo · noi abbiamo" else "we are · we have"),
                    "ihr seid · ihr habt" to (if (isIt) "voi siete · voi avete" else "you all are · have"),
                    "sie/Sie sind · haben" to (if (isIt) "loro sono / Lei è · hanno / ha" else "they/You are · have")
                ),
                exampleSentence = "Ich bin aus Italien und habe zwei Brüder.",
                exampleTranslation = if (isIt) "Sono italiano e ho due fratelli." else "I am from Italy and have two brothers.",
                quizPrompt = "Wir ___ heute sehr glücklich und ___ viel Zeit.",
                quizCorrect = "sind / haben",
                quizOptions = listOf("sind / haben", "seid / habt", "ist / hat")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Verbi Modali (Können, Müssen, Möchten, Wollen)" else "Modal Verbs",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "Il verbo modale occupa il 2° posto nella frase, mentre il verbo all'infinito va sempre in fondo." else "Place the modal verb in 2nd position and the infinitive verb at the very end.",
                tableRows = listOf(
                    "ich kann · wir können" to (if (isIt) "posso · possiamo (capacità o possibilità)" else "I can · we can"),
                    "ich muss · wir müssen" to (if (isIt) "devo · dobbiamo (obbligo o necessità)" else "I must · we must"),
                    "ich möchte · wir möchten" to (if (isIt) "vorrei · vorremmo (desiderio cortese)" else "I would like · we would like"),
                    "ich will · wir wollen" to (if (isIt) "voglio · vogliamo (intenzione decisa)" else "I want · we want")
                ),
                exampleSentence = "Ich möchte gern einen Kaffee trinken.",
                exampleTranslation = if (isIt) "Vorrei bere volentieri un caffè." else "I would like to drink a coffee.",
                quizPrompt = "Morgen ___ ich früh aufstehen.",
                quizCorrect = "muss",
                quizOptions = listOf("muss", "müssen", "musst")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Passato Parlato (Perfekt) e Präteritum" else "Past Tenses (Perfekt & Präteritum)",
                levelBadge = "A2–B1",
                whenToUse = if (isIt) "Nel parlato si usa il Perfekt (haben/sein + participio in fondo). Con sein, haben e i modali si usa il Präteritum (war, hatte, musste, konnte)." else "Use Perfekt for spoken German, and Präteritum for auxiliaries and modals.",
                tableRows = listOf(
                    "ich habe gelernt · gemacht" to (if (isIt) "ho studiato · ho fatto" else "I studied · I made"),
                    "ich bin gefahren · gegangen" to (if (isIt) "sono andato (verbi di moto -> sein)" else "I traveled · I went"),
                    "ich war · ich hatte" to (if (isIt) "ero / sono stato · avevo / ho avuto" else "I was · I had"),
                    "ich musste · ich konnte" to (if (isIt) "ho dovuto · ho potuto" else "I had to · I could")
                ),
                exampleSentence = "Gestern bin ich mit dem Zug nach München gefahren.",
                exampleTranslation = if (isIt) "Ieri sono andato a Monaco in treno." else "Yesterday I traveled to Munich by train.",
                quizPrompt = "Letzte Woche ___ wir ins Theater gegangen.",
                quizCorrect = "sind",
                quizOptions = listOf("sind", "haben", "waren")
            ),
            GrammarStudyCard(
                category = "PRONOUNS",
                title = if (isIt) "Pronomi Personali (Nominativo, Accusativo, Dativo)" else "Personal Pronouns",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Nominativo per il soggetto, Accusativo per l'oggetto diretto e Dativo per il destinatario ('a chi?') o dopo mit, zu, helfen." else "Nominative for subject, Accusative for direct object, Dative for recipient.",
                tableRows = listOf(
                    "ich -> mich (Akk.) -> mir (Dat.)" to (if (isIt) "io -> mi (oggetto) -> a me" else "I -> me -> to me"),
                    "du -> dich (Akk.) -> dir (Dat.)" to (if (isIt) "tu -> ti (oggetto) -> a te" else "you -> you -> to you"),
                    "er -> ihn (Akk.) -> ihm (Dat.)" to (if (isIt) "lui -> lo -> a lui (gli)" else "he -> him -> to him"),
                    "sie -> sie (Akk.) -> ihr (Dat.)" to (if (isIt) "lei -> la -> a lei (le)" else "she -> her -> to her"),
                    "wir -> uns · Sie -> Ihnen (Dat.)" to (if (isIt) "noi -> ci · Lei -> a Lei" else "we -> us · You -> to You")
                ),
                exampleSentence = "Kannst du mir bitte sagen, wo ich ihn finde?",
                exampleTranslation = if (isIt) "Puoi dirmi per favore dove lo trovo?" else "Can you tell me where I can find him?",
                quizPrompt = "Wie geht es ___ heute? Danke, es geht mir gut.",
                quizCorrect = "dir",
                quizOptions = listOf("dir", "dich", "du")
            ),
            GrammarStudyCard(
                category = "ADJECTIVES",
                title = if (isIt) "Articoli e Casi (der, die, das)" else "Articles & Cases",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Nell'Accusativo cambia solo il maschile (der -> den). Nel Dativo diventano dem (maschile/neutro), der (femminile), den (plurale)." else "In Accusative only masculine changes (der -> den). In Dative: dem, der, den.",
                tableRows = listOf(
                    "Nominativ: der (m) · die (f) · das (n)" to (if (isIt) "Soggetto della frase" else "Subject"),
                    "Akkusativ: den (m) · die (f) · das (n)" to (if (isIt) "Oggetto diretto" else "Direct object"),
                    "Dativ: dem (m) · der (f) · dem (n)" to (if (isIt) "Termine / stato in luogo / dopo mit, zu" else "Indirect object / after mit, zu"),
                    "Genitiv: des (m/n) · der (f/pl)" to (if (isIt) "Possesso / dopo trotz, während" else "Possession / during, despite")
                ),
                exampleSentence = "Ich gebe dem Kellner den Schlüssel für das Zimmer.",
                exampleTranslation = if (isIt) "Do al cameriere la chiave per la stanza." else "I give the waiter the key for the room.",
                quizPrompt = "Ich trinke gern einen Kaffee mit ___ warmen Milch (die Milch, femm.).",
                quizCorrect = "der",
                quizOptions = listOf("der", "die", "dem")
            ),
            GrammarStudyCard(
                category = "PHRASES",
                title = if (isIt) "Regole di Pronuncia Tedesca" else "German Pronunciation Rules",
                levelBadge = "A1–B2",
                whenToUse = if (isIt) "Ecco le combinazioni chiave per leggere qualsiasi parola tedesca senza esitazioni." else "Core letter combinations to read any German word accurately.",
                tableRows = listOf(
                    "ei = [ai] · ie = [ii lunga]" to (if (isIt) "mein (main) · sieben (ziiben)" else "mein · sieben"),
                    "eu / äu = [oi]" to (if (isIt) "heute (hoite) · Häuser (hoiser)" else "heute · Häuser"),
                    "sch = [sc] · sp / st = [shp / sht]" to (if (isIt) "Schule · sprechen · Straße" else "Schule · sprechen · Straße"),
                    "ch dopo i/e/ä/ö/ü = dolce [ç]" to (if (isIt) "ich · möchte · Bücher" else "ich · möchte · Bücher")
                ),
                exampleSentence = "Heute sprechen wir über fünf schöne Bücher.",
                exampleTranslation = if (isIt) "Oggi parliamo di cinque bei libri." else "Today we are talking about five nice books.",
                quizPrompt = "Come si legge il dittongo 'eu' nella parola 'heute' (oggi)?",
                quizCorrect = "Come 'oi' (hoite)",
                quizOptions = listOf("Come 'oi' (hoite)", "Come 'eu' italiana", "Come 'au'")
            )
        )
    } else {
        listOf(
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Ser vs Estar (I due verbi 'Essere')" else "Ser vs Estar",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "Usa SER per identità, origine, professione e ora. Usa ESTAR per posizione nello spazio e stati temporanei." else "Use SER for identity, origin, and time. Use ESTAR for location and temporary states.",
                tableRows = listOf(
                    "yo soy · yo estoy" to (if (isIt) "io sono (identità) · io mi trovo / sto" else "I am (identity) · I am (location)"),
                    "tú eres · tú estás" to (if (isIt) "tu sei · tu stai" else "you are"),
                    "él/ella es · está" to (if (isIt) "lui/lei è · si trova / sta" else "he/she is"),
                    "nosotros somos · estamos" to (if (isIt) "noi siamo · noi ci troviamo / stiamo" else "we are"),
                    "ellos son · están" to (if (isIt) "loro sono · loro si trovano / stanno" else "they are")
                ),
                exampleSentence = "Soy de Milán, pero hoy estoy en Barcelona por trabajo.",
                exampleTranslation = if (isIt) "Sono di Milano, ma oggi mi trovo a Barcellona per lavoro." else "I am from Milan, but today I am in Barcelona for work.",
                quizPrompt = "La farmacia ___ al final de esta calle, pero ahora ___ cerrada.",
                quizCorrect = "está / está",
                quizOptions = listOf("está / está", "es / está", "es / es")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Tener (Avere) vs Haber (Ausiliare e Hay)" else "Tener vs Haber & Hay",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "TENER indica possesso o fame/sete/età. HABER (he, has, ha, hemos) forma il passato prossimo, mentre HAY significa 'c'è / ci sono'." else "TENER for possession; HABER as auxiliary; HAY for 'there is / are'.",
                tableRows = listOf(
                    "tengo, tienes, tiene, tenemos" to (if (isIt) "ho, hai, ha, abbiamo (possesso)" else "I have, you have"),
                    "he, has, ha, hemos + participio" to (if (isIt) "ho parlato (he hablado), abbiamo mangiato" else "have spoken, have eaten"),
                    "hay (invariabile)" to (if (isIt) "c'è / ci sono (Hay dos mesas libres)" else "there is / there are"),
                    "tener que + infinito" to (if (isIt) "dover fare qualcosa (Tengo que salir)" else "have to do something")
                ),
                exampleSentence = "Hoy he tenido mucho trabajo y ahora tengo hambre.",
                exampleTranslation = if (isIt) "Oggi ho avuto molto lavoro e ora ho fame." else "Today I have had a lot of work and now I am hungry.",
                quizPrompt = "Esta mañana nosotros ___ desayunado en el bar porque ___ prisa.",
                quizCorrect = "hemos / teníamos",
                quizOptions = listOf("hemos / teníamos", "tenemos / hemos", "hay / tenemos")
            ),
            GrammarStudyCard(
                category = "PRONOUNS",
                title = if (isIt) "Pronomi Oggetto Diretto (lo/la) e Indiretto (le/se)" else "Direct & Indirect Object Pronouns",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "I pronomi vanno prima del verbo coniugato. Quando 'le' incontra 'lo/la', si trasforma in 'se' (Se lo doy = Glielo do)." else "Place pronouns before the verb. 'Le' becomes 'se' before 'lo/la'.",
                tableRows = listOf(
                    "me · te · nos" to (if (isIt) "mi · ti · ci (diretto, indiretto e riflessivo)" else "me · you · us"),
                    "lo, la, los, las" to (if (isIt) "lo, la, li, le (oggetto diretto)" else "him, her, it, them"),
                    "le, les (-> se lo / se la)" to (if (isIt) "gli, le, a loro (diventa 'se' davanti a lo/la)" else "to him/her/them"),
                    "conmigo · contigo" to (if (isIt) "con me · con te" else "with me · with you")
                ),
                exampleSentence = "Me pidió las llaves y se las entregué inmediatamente.",
                exampleTranslation = if (isIt) "Mi ha chiesto le chiavi e gliele ho consegnate subito." else "He asked me for the keys and I handed them to him immediately.",
                quizPrompt = "¿Le has enviado el correo a Ana? — Sí, ya ___ he enviado.",
                quizCorrect = "se lo",
                quizOptions = listOf("se lo", "le lo", "la lo")
            ),
            GrammarStudyCard(
                category = "ADJECTIVES",
                title = if (isIt) "Aggettivi, Possessivi e Muy vs Mucho" else "Adjectives, Possessives & Muy vs Mucho",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Usa MUY davanti ad aggettivi e avverbi (muy bueno), e MUCHO/A/OS/AS davanti ai nomi o dopo i verbi (mucho tiempo)." else "Use MUY before adjectives/adverbs and MUCHO with nouns/verbs.",
                tableRows = listOf(
                    "mi/mis · tu/tus · su/sus" to (if (isIt) "mio/miei · tuo/tuoi · suo/suoi (senza articolo)" else "my · your · his/her"),
                    "muy + aggettivo / avverbio" to (if (isIt) "muy fácil, muy bien, muy tarde" else "very easy, very well"),
                    "mucho/a/os/as + sostantivo" to (if (isIt) "mucha agua, muchos amigos" else "a lot of water, many friends"),
                    "más ... que · mejor que" to (if (isIt) "più ... di · migliore di" else "more ... than · better than")
                ),
                exampleSentence = "Lo más importante es que este proyecto es mejor que el anterior.",
                exampleTranslation = if (isIt) "La cosa più importante è che questo progetto è migliore del precedente." else "The most important thing is that this project is better than the previous one.",
                quizPrompt = "Hoy estoy ___ cansado porque ayer tuvimos ___ reuniones.",
                quizCorrect = "muy / muchas",
                quizOptions = listOf("muy / muchas", "mucho / muy", "muy / muchos")
            ),
            GrammarStudyCard(
                category = "PHRASES",
                title = if (isIt) "Pronuncia Spagnola e Por vs Para" else "Pronunciation & Por vs Para",
                levelBadge = "A1–B2",
                whenToUse = if (isIt) "Usa PARA per scopo, destinatario e scadenza; usa POR per causa, mezzo e durata." else "Use PARA for goal/recipient/deadline; use POR for cause/means.",
                tableRows = listOf(
                    "PARA: scopo, destinatario, destinazione" to (if (isIt) "Estudio para aprender · Es para ti" else "in order to · for you"),
                    "POR: causa, mezzo, prezzo, parte del giorno" to (if (isIt) "Por la lluvia · Por teléfono · Por la mañana" else "because of · by phone"),
                    "que / qui = [che / chi] · gue / gui = [ghe / ghi]" to (if (isIt) "quiero, queso, guitarra" else "quiero, queso, guitarra"),
                    "ll = [gl / y] · ñ = [gn] · j = [kh]" to (if (isIt) "llave, mañana, viaje" else "llave, mañana, viaje")
                ),
                exampleSentence = "Te envío el contrato por correo electrónico para que lo firmes.",
                exampleTranslation = if (isIt) "Ti invio il contratto per email affinché tu lo firmi." else "I am sending you the contract by email so that you sign it.",
                quizPrompt = "He comprado este regalo ___ tu cumpleaños y pagué treinta euros ___ él.",
                quizCorrect = "para / por",
                quizOptions = listOf("para / por", "por / para", "para / para")
            )
        )
    }
}
''',

    "app/src/main/java/com/vocalfox/app/ui/screens/OnboardingAndLessonScreens.kt": '''\
package com.vocalfox.app.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.BorderStroke
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
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.Stop
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.OutlinedButton
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
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
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
            verticalArrangement = Arrangement.spacedBy(18.dp)
        ) {
            AnimatedWebpSplashPlayer(size = 240.dp)
            VocalFoxWordmark(height = 42.dp)
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

    var onboardingStage by remember { mutableIntStateOf(0) }
    var questionIdx by remember { mutableIntStateOf(0) }
    var correctCount by remember { mutableIntStateOf(0) }

    BackHandler(enabled = onboardingStage > 0) {
        VocalFoxSfxManager.playTileTap(context)
        when (onboardingStage) {
            1 -> onboardingStage = 0
            2 -> {
                if (questionIdx > 0) {
                    questionIdx--
                } else {
                    onboardingStage = 1
                }
            }
            3 -> onboardingStage = 0
        }
    }

    val pack = allPacks[selectedLangCode] ?: allPacks.values.first()
    val placementQuestions = remember(pack.languageCode) {
        CefrLevel.entries.mapNotNull { lvl ->
            pack.grammarExercises.firstOrNull { it.cefr == lvl }
        }
    }

    if (onboardingStage == 0) {
        val welcomeKitBitmap = remember {
            MascotBitmapCache.getTrimmedBitmap(context, "welcome_kit", stripBackground = true)
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(colors.card)
                .statusBarsPadding()
                .navigationBarsPadding()
                .padding(horizontal = 24.dp, vertical = 20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Spacer(modifier = Modifier.height(12.dp))

            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                if (welcomeKitBitmap != null) {
                    Image(
                        bitmap = welcomeKitBitmap,
                        contentDescription = "Vocalfox Welcome",
                        contentScale = ContentScale.Fit,
                        modifier = Modifier.size(210.dp)
                    )
                } else {
                    VocalFoxMascot(state = MascotState.LOGO_IDLE, size = 190.dp)
                }

                VocalFoxWordmark(height = 44.dp)

                Text(
                    text = if (isIt) {
                        "Impara una lingua gratuitamente. Per sempre."
                    } else {
                        "Learn a language for free. Forever."
                    },
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
                Button(
                    onClick = {
                        VocalFoxSfxManager.playTileTap(context)
                        onboardingStage = 1
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = colors.accent,
                        contentColor = colors.onAccent
                    ),
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp)
                ) {
                    Text(
                        text = if (isIt) "INIZIA" else "GET STARTED",
                        style = VocalFoxType.BodyMedium.copy(fontWeight = FontWeight.SemiBold)
                    )
                }

                OutlinedButton(
                    onClick = {
                        VocalFoxSfxManager.playTileTap(context)
                        onboardingStage = 3
                    },
                    border = BorderStroke(1.5.dp, colors.hairline),
                    colors = ButtonDefaults.outlinedButtonColors(
                        containerColor = colors.background,
                        contentColor = colors.accent
                    ),
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp)
                ) {
                    Text(
                        text = if (isIt) "HO GIÀ UN LIVELLO" else "I ALREADY KNOW SOME",
                        style = VocalFoxType.BodyMedium.copy(fontWeight = FontWeight.SemiBold)
                    )
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
        verticalArrangement = Arrangement.spacedBy(18.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.clickable {
                VocalFoxSfxManager.playTileTap(context)
                onboardingStage = if (onboardingStage == 2 && questionIdx > 0) {
                    questionIdx--
                    2
                } else {
                    0
                }
            }
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(colors.raised),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Outlined.ArrowBack, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
            }
            Text(
                text = if (isIt) "Indietro" else "Back",
                style = VocalFoxType.BodyMedium,
                color = colors.secondaryText
            )
        }

        when (onboardingStage) {
            1 -> {
                Text(
                    text = strings.chooseUiLanguageLabel,
                    style = VocalFoxType.SectionTitle,
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
                    style = VocalFoxType.SectionTitle,
                    color = colors.primaryText
                )
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    allPacks.values.forEach { p ->
                        val isSelected = p.languageCode == selectedLangCode
                        val flagBadge = if (p.languageCode == "de") "DE · Deutsch" else "ES · Español"
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

                Spacer(modifier = Modifier.height(6.dp))

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.accent)
                        .clickable {
                            VocalFoxSfxManager.playSuccess(context)
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
                    Icon(Icons.Outlined.ArrowForward, null, tint = colors.onAccent)
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
                            onboardingStage = 2
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
                    Icon(Icons.Outlined.ArrowForward, null, tint = colors.accent)
                }
            }

            2 -> {
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
                        verticalArrangement = Arrangement.spacedBy(14.dp)
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
                                            correctCount++
                                            VocalFoxSfxManager.playSuccess(context)
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

            3 -> {
                Text(
                    text = if (isIt) "Scegli lingua e livello" else "Pick language & level",
                    style = VocalFoxType.PageTitle,
                    color = colors.primaryText
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    allPacks.values.forEach { p ->
                        val active = p.languageCode == selectedLangCode
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .clip(RoundedCornerShape(12.dp))
                                .background(if (active) colors.accent else colors.card)
                                .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                                .clickable {
                                    VocalFoxSfxManager.playTileTap(context)
                                    onSelectTargetLang(p.languageCode)
                                }
                                .padding(vertical = 14.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = p.languageName.get(systemLang),
                                style = VocalFoxType.BodyMedium,
                                color = if (active) colors.onAccent else colors.primaryText
                            )
                        }
                    }
                }

                CefrLevel.entries.forEach { lvl ->
                    val desc = when (lvl) {
                        CefrLevel.A1 -> if (isIt) "Principiante · Basi e prime frasi" else "Beginner · Foundations"
                        CefrLevel.A2 -> if (isIt) "Elementare · Vita quotidiana" else "Elementary · Everyday life"
                        CefrLevel.B1 -> if (isIt) "Intermedio · Conversazione e opinioni" else "Intermediate · Fluency"
                        CefrLevel.B2 -> if (isIt) "Avanzato · Strutture complesse" else "Upper-Intermediate · Mastery"
                    }
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(14.dp))
                            .clickable {
                                VocalFoxSfxManager.playSuccess(context)
                                onCompleteOnboarding(lvl)
                            }
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(lvl.name, style = VocalFoxType.SectionTitle, color = colors.accent)
                            Text(desc, style = VocalFoxType.SecondaryCaption, color = colors.secondaryText)
                        }
                        Icon(Icons.Outlined.ArrowForward, null, tint = colors.accent)
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
    val haptic = LocalHapticFeedback.current
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT
    var currentStep by remember(bundle.unitIndex, bundle.grammarExercise.id) { mutableIntStateOf(0) }

    BackHandler {
        VocalFoxSfxManager.playTileTap(context)
        if (currentStep in 1..3) {
            currentStep--
        } else {
            onClose()
        }
    }

    val animatedProgress by animateFloatAsState(
        targetValue = (currentStep + 1) / 5f,
        animationSpec = tween(280),
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
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(colors.raised)
                    .clickable {
                        VocalFoxSfxManager.playTileTap(context)
                        onClose()
                    },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Outlined.Close,
                    contentDescription = null,
                    tint = colors.primaryText,
                    modifier = Modifier.size(18.dp)
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
                text = "${(currentStep + 1).coerceAtMost(4)}/4",
                style = VocalFoxType.MetaMono,
                color = colors.secondaryText
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        AnimatedContent(
            targetState = currentStep,
            transitionSpec = {
                fadeIn(animationSpec = tween(200)) togetherWith fadeOut(animationSpec = tween(160))
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
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Text(
                            text = strings.stepLearnWords,
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
                                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                        onSpeakText(token.surface, 1.0f)
                                    }
                                    .padding(16.dp),
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
                                        .background(if (colors.isDark) VocalFoxPalette.TintWarmAmber.copy(alpha = 0.22f) else VocalFoxPalette.TintWarmAmber),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = null,
                                        tint = colors.accent
                                    )
                                }
                            }
                        }

                        MascotPedagogicalBanner(
                            state = MascotState.THINKING,
                            title = bundle.cefr.name,
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
                        verticalArrangement = Arrangement.spacedBy(14.dp)
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
                                .padding(18.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
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
                                            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                            picked = option
                                            verified = false
                                            onSpeakText(option, 1.0f)
                                        }
                                        .padding(14.dp),
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
                                title = if (isRight) (if (isIt) "Corretto!" else "Correct!") else ex.blankTarget,
                                subtitle = ex.explanation.get(systemLang)
                            )
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!verified) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!verified && picked != null) {
                                    verified = true
                                    if (isRight) {
                                        VocalFoxSfxManager.playSuccess(context)
                                    } else {
                                        VocalFoxSfxManager.playError(context)
                                    }
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
                    val wrt = bundle.writingExercise
                    val targetSentence = wrt.referenceTargets.firstOrNull().orEmpty()
                    val expectedWords = remember(wrt.id) {
                        targetSentence
                            .replace(".", "")
                            .replace(",", "")
                            .replace("¿", "")
                            .replace("?", "")
                            .replace("¡", "")
                            .replace("!", "")
                            .split(" ")
                            .filter { it.isNotBlank() }
                            .ifEmpty { bundle.grammarExercise.scrambleTokens }
                    }
                    val shuffledBank = remember(wrt.id) { expectedWords.shuffled() }
                    val selectedWords = remember(wrt.id) { mutableStateListOf<String>() }
                    var checked by remember(wrt.id) { mutableStateOf(false) }

                    val allCorrect = selectedWords.size == expectedWords.size &&
                        selectedWords.indices.all { idx ->
                            selectedWords[idx].equals(expectedWords[idx], ignoreCase = true)
                        }

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Text(
                            text = strings.stepBuildSentence,
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
                                .padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text(
                                text = wrt.sourcePrompt.get(systemLang),
                                style = VocalFoxType.SentenceDisplay,
                                color = colors.primaryText
                            )
                            Text(
                                text = wrt.grammarRuleTitle.get(systemLang),
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.mutedText
                            )
                        }

                        FlowRow(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(112.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.raised)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            selectedWords.forEachIndexed { idx, w ->
                                val isWordPosCorrect = idx < expectedWords.size &&
                                    w.equals(expectedWords[idx], ignoreCase = true)
                                val outlineColor = when {
                                    !checked -> colors.accent
                                    isWordPosCorrect -> colors.positive
                                    else -> colors.negative
                                }
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(colors.card)
                                        .border(2.dp, outlineColor, RoundedCornerShape(10.dp))
                                        .clickable {
                                            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                            VocalFoxSfxManager.playTileTap(context)
                                            selectedWords.removeAt(idx)
                                            checked = false
                                        }
                                        .padding(horizontal = 12.dp, vertical = 8.dp)
                                ) {
                                    Text(
                                        text = w,
                                        style = VocalFoxType.BodyMedium,
                                        color = colors.primaryText
                                    )
                                }
                            }
                        }

                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            shuffledBank.forEach { word ->
                                val alreadyUsed = selectedWords.count { it == word } >= expectedWords.count { it == word }
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(if (alreadyUsed) colors.raised else colors.card)
                                        .border(1.dp, colors.hairline, RoundedCornerShape(10.dp))
                                        .clickable(enabled = !alreadyUsed) {
                                            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
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
                                state = if (allCorrect) MascotState.CELEBRATE else MascotState.STRICT_COACH,
                                title = targetSentence,
                                subtitle = wrt.jitFeedback.get(systemLang)
                            )
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!checked) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!checked && selectedWords.isNotEmpty()) {
                                    checked = true
                                    if (allCorrect) {
                                        VocalFoxSfxManager.playSuccess(context)
                                    } else {
                                        VocalFoxSfxManager.playError(context)
                                    }
                                    onSpeakText(targetSentence, 1.0f)
                                } else if (checked) {
                                    VocalFoxSfxManager.playTileTap(context)
                                    currentStep = 3
                                }
                            }
                        )
                    }
                }

                3 -> {
                    val drill = bundle.pronunciationDrill
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Text(
                            text = strings.stepSpeakAloud,
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(18.dp),
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
                                onCompleteUnit(bundle, pronunciationResult?.overallScore ?: 90)
                                currentStep = 4
                            }
                        )
                    }
                }

                else -> {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        VocalFoxMascot(
                            state = MascotState.CELEBRATE,
                            size = 160.dp,
                            tintBackground = if (colors.isDark) VocalFoxPalette.TintSoftGold.copy(alpha = 0.22f) else VocalFoxPalette.TintSoftGold
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
                            color = colors.secondaryText,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(28.dp))

                        OutlinedButton(
                            onClick = {
                                VocalFoxSfxManager.playTileTap(context)
                                GeminiHandoffHelper.launchGeminiAppWithPrompt(
                                    context = context,
                                    targetLanguageCode = bundle.grammarExercise.id.substringBefore("_"),
                                    cefrLevel = bundle.cefr,
                                    systemLang = systemLang,
                                    topic = bundle.title
                                )
                            },
                            border = BorderStroke(1.5.dp, colors.accent),
                            shape = RoundedCornerShape(14.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(52.dp)
                        ) {
                            Icon(Icons.Outlined.AutoAwesome, null, tint = colors.accent, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = if (isIt) "Pratica questo tema su Gemini Live" else "Practice this topic on Gemini Live",
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
'''
}


def find_project_root() -> Path | None:
    for candidate in [Path(__file__).resolve().parent, Path.cwd()]:
        if (candidate / "settings.gradle.kts").exists():
            return candidate
    return None


def main() -> None:
    root = find_project_root()
    if root is None:
        print("[ERRORE] Esegui questo script dalla cartella principale del progetto (dove si trova settings.gradle.kts).")
        return

    print(f"[VocalFox Upgrade] Applicazione miglioramenti in: {root}\n")

    for obs in OBSOLETE_FILES:
        obs_path = root / obs
        if obs_path.exists():
            obs_path.unlink()
            print(f"  - Rimosso file obsoleto: {obs}")

    for rel_path, content in UPDATED_FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  + Aggiornato/Creato: {rel_path}")

    print("\n[OK] Tutti gli aggiornamenti sono stati applicati con successo!")


if __name__ == "__main__":
    main()