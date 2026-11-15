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
