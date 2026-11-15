#!/usr/bin/env python3
"""
patch_vocalfox.py
Applica i 5 aggiornamenti mirati a Vocalfox:
1. Fix HTTP 404 in GeminiLiveTutorClient.kt: aggiorna a models/gemini-3.8-flash con fallback a models/gemini-2.5-flash.
2. Persistenza immediata in SharedPreferences di lingua, livello CEFR e lingua UI in VocalFoxViewModel.kt + calcolo streak con java.time.LocalDate.
3. Splash Screen con sfondo Nero Puro (#000000) in modo che l'animazione WebP della volpe si fonda perfettamente + logotipo grafico Vocalfox sotto.
4. Header pulito in LiveConversationScreen.kt: solo pulsante circolare 44.dp con icona sparkle per Gemini Live; rimossa l'icona chiave dall'header (gestita solo in Profilo).
5. Nuova Schermata di Benvenuto al primo avvio (stile Duolingo reference) con welcome_kit.png, logotipo grafico Vocalfox, sottotitolo e i due pulsanti a tutta larghezza.
"""

import shutil
from pathlib import Path

FILES: dict[str, str] = {
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
 * Direct REST client for Google Gemini Live AI Conversation Tutor.
 * Uses `models/gemini-3.8-flash` primarily, with automatic fallback to `models/gemini-2.5-flash` on 404.
 */
object GeminiLiveTutorClient {

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
            return@withContext Result.failure(IllegalArgumentException("API Key mancante"))
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

        val payload = JSONObject().apply {
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
        }

        val modelsToTry = listOf("gemini-3.8-flash", "gemini-2.5-flash")
        var lastError: Throwable? = null

        for (modelName in modelsToTry) {
            try {
                val endpoint = "https://generativelanguage.googleapis.com/v1beta/models/$modelName:generateContent?key=$cleanKey"
                val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = 15000
                    readTimeout = 20000
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                }

                OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { writer ->
                    writer.write(payload.toString())
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
                    return@withContext Result.success(
                        TutorChatMessage(
                            isUser = false,
                            text = parsed.optString("reply", "¡Muy bien! ¿Qué más me cuentas?"),
                            translation = parsed.optString("translation", ""),
                            grammarCorrection = parsed.optString("correction", "")
                        )
                    )
                } else {
                    lastError = RuntimeException("HTTP $code: $rawResponse")
                    // If 404 Not Found on primary model, loop continues to fallback model
                    if (code != 404) break
                }
            } catch (e: Throwable) {
                lastError = e
            }
        }

        Result.failure(lastError ?: RuntimeException("Errore di connessione a Gemini API"))
    }
}
""",

    "app/src/main/java/com/vocalfox/app/ui/viewmodel/VocalFoxViewModel.kt": """\
package com.vocalfox.app.ui.viewmodel

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.vocalfox.app.audio.PiperTtsManager
import com.vocalfox.app.audio.PronunciationEvaluator
import com.vocalfox.app.audio.PronunciationResult
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
import com.vocalfox.app.domain.model.WritingExercise
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.theme.MascotState
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

data class WritingEvaluationFeedback(
    val score: Int,
    val matchedMorphemes: List<String>,
    val missingMorphemes: List<String>,
    val mascotState: MascotState,
    val explanation: String
)

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

    private val _showFurigana = MutableStateFlow(true)
    val showFurigana: StateFlow<Boolean> = _showFurigana.asStateFlow()

    private val _showRomaji = MutableStateFlow(true)
    val showRomaji: StateFlow<Boolean> = _showRomaji.asStateFlow()

    private val _isRecordingAudio = MutableStateFlow(false)
    val isRecordingAudio: StateFlow<Boolean> = _isRecordingAudio.asStateFlow()

    private val _latestPronunciationResult = MutableStateFlow<PronunciationResult?>(null)
    val latestPronunciationResult: StateFlow<PronunciationResult?> = _latestPronunciationResult.asStateFlow()

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

    fun toggleFurigana(enabled: Boolean) {
        _showFurigana.value = enabled
    }

    fun toggleRomaji(enabled: Boolean) {
        _showRomaji.value = enabled
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

    fun evaluateWritingSubmission(
        exercise: WritingExercise,
        userInput: String
    ): WritingEvaluationFeedback {
        val normalizedUser = userInput.trim().lowercase()
        val matched = exercise.requiredMorphemes.filter { morpheme ->
            normalizedUser.contains(morpheme.lowercase())
        }
        val missing = exercise.requiredMorphemes.filter { morpheme ->
            !normalizedUser.contains(morpheme.lowercase())
        }

        val exactMatch = exercise.referenceTargets.any {
            it.trim().lowercase().trimEnd('.', '。') == normalizedUser.trimEnd('.', '。')
        }

        val ratio = if (exercise.requiredMorphemes.isEmpty()) 1f
        else matched.size.toFloat() / exercise.requiredMorphemes.size

        val score = when {
            exactMatch -> 98
            ratio >= 1.0f && normalizedUser.length >= 8 -> 90
            ratio >= 0.5f -> (60 + ratio * 25).toInt()
            normalizedUser.isNotBlank() -> 35
            else -> 0
        }

        val mascot = when {
            score >= 85 -> MascotState.CELEBRATE
            score >= 60 -> MascotState.THINKING
            score > 0 -> MascotState.STRICT_COACH
            else -> MascotState.ENCOURAGE_SAD
        }

        viewModelScope.launch {
            repository.recordExerciseOutcome(
                itemKey = exercise.id,
                languageCode = _selectedLanguageCode.value,
                cefrLevel = exercise.cefr,
                pillar = "WRITING",
                score = score,
                promptPreview = exercise.sourcePrompt.get(_systemLang.value),
                targetAnswer = exercise.referenceTargets.firstOrNull().orEmpty(),
                mistakeNote = exercise.jitFeedback.get(_systemLang.value)
            )
        }

        return WritingEvaluationFeedback(
            score = score,
            matchedMorphemes = matched,
            missingMorphemes = missing,
            mascotState = mascot,
            explanation = exercise.jitFeedback.get(_systemLang.value)
        )
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
""",

    "app/src/main/java/com/vocalfox/app/MainActivity.kt": """\
package com.vocalfox.app

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
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
        delay(2200L)
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

    Scaffold(
        containerColor = colors.background,
        bottomBar = {
            CleanBottomNavigationBar(
                activeTab = activeTab,
                systemLang = systemLang,
                onSelectTab = { activeTab = it }
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
                    onStartGuidedUnit = { unit -> activeGuidedUnit = unit },
                    onOpenProfileSettings = { activeTab = MainTab.PROFILE }
                )

                MainTab.EXPLORE -> ExploreStudyHubScreen(
                    currentPack = currentPack,
                    systemLang = systemLang,
                    strings = strings,
                    onPlayAudio = { text, speed -> viewModel.speakSentence(text, speed) }
                )

                MainTab.LIVE_AI -> LiveConversationScreen(
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
                        onSelectTargetLang = viewModel::selectLanguage
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
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/HomeScreen.kt": """\
package com.vocalfox.app.ui.screens

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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
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
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    val all50Units = remember(currentPack.languageCode, selectedCefr, systemLang) {
        CurriculumGenerator.generate50UnitsForLevel(currentPack, selectedCefr, systemLang)
    }

    var selectedChapterFilter by remember(selectedCefr) { mutableIntStateOf(0) }
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
                            .clickable { onSelectCefr(level) }
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
                            .clickable { selectedChapterFilter = chapIdx }
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
                        tintBackground = unit.tintColor
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
            errorMessage = if (isIt) {
                "Per chattare qui inserisci la tua API Key nella scheda Profilo, oppure tocca l'icona ✨ in alto a destra per parlare subito nell'app Gemini."
            } else {
                "Set your API Key in the Profile tab to chat here, or tap the ✨ icon above to speak in the Gemini app."
            }
            return
        }

        errorMessage = null
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
                messages.add(replyMsg)
                onSpeakText(replyMsg.text, 1.0f)
            }.onFailure { err ->
                errorMessage = err.localizedMessage ?: "Errore chiamata Gemini"
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
                        .clickable { selectedScenario = scen }
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
                    .border(1.dp, colors.negative, RoundedCornerShape(12.dp))
                    .clickable { onOpenSettingsForApiKey() }
                    .padding(12.dp)
            ) {
                Text(
                    text = errorMessage!!,
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.negative
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

/**
 * Splash Screen con sfondo Nero Puro (#000000) così il riquadro nero dell'animazione WebP
 * si fonde alla perfezione ("blend in") senza alcun bordo visibile, seguito dal logotipo Vocalfox.
 */
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

/**
 * Primo Avvio:
 * - Step 0: Schermata di Benvenuto in stile Duolingo (`6230cce907f5a532aa4b175e_5d38993213523202613a6180_Duo-1.png`)
 *   con `welcome_kit.png`, `VocalFoxWordmark`, sottotitolo e i due pulsanti "INIZIA" e "HO GIÀ UN LIVELLO / SALTA AL PERCORSO".
 * - Step 1: Configurazione lingua + partenza da zero o test di piazzamento.
 * - Step 2: Scelta diretta lingua + livello per chi ha premuto "HO GIÀ UN LIVELLO / SALTA AL PERCORSO".
 */
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

    var onboardingPhase by remember { mutableIntStateOf(0) } // 0 = Welcome Landing, 1 = Setup/Test, 2 = Direct Level Picker
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
        // SCHERMATA DI BENVENUTO ISPIRATA A DUO-1.PNG
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

            // Blocco Centrale: welcome_kit.png + VocalFoxWordmark + Sottotitolo
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

            // Blocco Inferiore: 2 Pulsanti a tutta larghezza (height = 54.dp, RoundedCornerShape(16.dp))
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
                        .clickable { onboardingPhase = 1 },
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
                        .clickable { onboardingPhase = 2 },
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
        // Scelta diretta di lingua e livello senza test
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
                            .clickable { onSelectTargetLang(p.languageCode) }
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
                        .clickable { onCompleteOnboarding(lvl) }
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
                            .clickable { onSelectSystemLang(lang) }
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
                            .clickable { onSelectTargetLang(p.languageCode) }
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
                    .clickable { onCompleteOnboarding(CefrLevel.A1) }
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
                                        correctCount++
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
                                    .clickable { onSpeakText(token.surface, 1.0f) }
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
                            onClick = { currentStep = 1 }
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
                                    onSpeakText(ex.promptSentence.replace("___", ex.blankTarget), 1.0f)
                                } else if (verified) {
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
                                .clickable { onSpeakText(targetToken?.surface.orEmpty(), 1.0f) }
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
                                } else if (verifiedMeaning) {
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
                                    onSpeakText(targetSentence, 1.0f)
                                } else if (checked) {
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
                            onClick = onClose
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

    print(f"[Vocalfox Patch] Applicazione 5 aggiornamenti su:\n  {root}\n")

    for rel_path, content in FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  + Aggiornato: {rel_path}")

    drawable_dir = root / "app/src/main/res/drawable-nodpi"
    drawable_dir.mkdir(parents=True, exist_ok=True)

    for asset_name in [
        "welcome_kit.png",
        "vocalfox_text.png",
        "vocalfox.png",
        "splash_screen.webp",
    ]:
        src_candidate = root / asset_name
        dst_candidate = drawable_dir / asset_name
        if src_candidate.exists() and src_candidate.resolve() != dst_candidate.resolve():
            shutil.copy2(src_candidate, dst_candidate)
            print(f"  + Copiato asset: {asset_name} -> app/src/main/res/drawable-nodpi/{asset_name}")

    print("\n========================================================")
    print("PATCH VOCALFOX COMPLETATA CON SUCCESSO!")
    print("Assicurati che welcome_kit.png sia dentro:")
    print("  app/src/main/res/drawable-nodpi/welcome_kit.png")
    print("Poi esegui:")
    print("========================================================\n")
    print(f'cd "{root}"')
    print("git add -A")
    print('git commit -m "Feat: Update to gemini-3.8-flash, persist language prefs, black splash & welcome screen"')
    print("git push origin main")


if __name__ == "__main__":
    main()
