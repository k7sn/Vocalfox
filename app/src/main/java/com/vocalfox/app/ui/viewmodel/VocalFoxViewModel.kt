package com.vocalfox.app.ui.viewmodel

import android.app.Application
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
    private val database = VocalFoxDatabase.getInstance(application)
    private val repository = VocalFoxRepository(database.dao(), PackLoader(application))
    val ttsManager = PiperTtsManager(application)
    private val pronunciationEvaluator = PronunciationEvaluator()

    private val _systemLang = MutableStateFlow(SystemLang.EN)
    val systemLang: StateFlow<SystemLang> = _systemLang.asStateFlow()

    private val _isDarkMode = MutableStateFlow(false)
    val isDarkMode: StateFlow<Boolean> = _isDarkMode.asStateFlow()

    private val _selectedLanguageCode = MutableStateFlow("es")
    val selectedLanguageCode: StateFlow<String> = _selectedLanguageCode.asStateFlow()

    private val _selectedCefr = MutableStateFlow(CefrLevel.A1)
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
        .stateIn(viewModelScope, SharingStarted.Eagerly, repository.getPack("es"))

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
    }

    fun toggleDarkMode(enabled: Boolean) {
        _isDarkMode.value = enabled
    }

    fun selectLanguage(code: String) {
        _selectedLanguageCode.value = code
        _latestPronunciationResult.value = null
    }

    fun selectCefr(level: CefrLevel) {
        _selectedCefr.value = level
        _latestPronunciationResult.value = null
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
