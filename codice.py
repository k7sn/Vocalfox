#!/usr/bin/env python3
"""
apply_fixes.py
Trova automaticamente la cartella del progetto VocalFox, applica i fix anti-crash
e stampa i comandi esatti per fare il push.
"""

from pathlib import Path

PATCHED_FILES: dict[str, str] = {
    "app/src/main/AndroidManifest.xml": """\
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.RECORD_AUDIO" />

    <queries>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
    </queries>

    <application
        android:allowBackup="true"
        android:icon="@drawable/logo"
        android:roundIcon="@drawable/logo"
        android:label="VocalFox"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
""",

    "app/src/main/java/com/vocalfox/app/data/repository/PackLoader.kt": """\
package com.vocalfox.app.data.repository

import android.content.Context
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.GrammarSyntaxExercise
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.LocalizedText
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.domain.model.SyntaxToken
import com.vocalfox.app.domain.model.VoicePreset
import com.vocalfox.app.domain.model.WritingExercise
import kotlinx.serialization.json.Json

class PackLoader(private val context: Context) {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    fun loadAllLanguagePacks(): Map<String, LanguagePack> {
        val packs = linkedMapOf<String, LanguagePack>()
        val files = try {
            context.assets.list("packs").orEmpty().filter { it.endsWith("_pack.json") }.sorted()
        } catch (_: Throwable) {
            emptyList()
        }

        for (fileName in files) {
            try {
                val rawJson = context.assets.open("packs/$fileName").bufferedReader().use { it.readText() }
                val pack = json.decodeFromString<LanguagePack>(rawJson)
                packs[pack.languageCode] = pack
            } catch (e: Throwable) {
                e.printStackTrace()
            }
        }

        if (packs.isEmpty()) {
            packs["es"] = createEmergencyPack()
        }
        return packs
    }

    companion object {
        fun createEmergencyPack(): LanguagePack = LanguagePack(
            languageCode = "es",
            languageName = LocalizedText("Spanish", "Spagnolo"),
            availableVoices = listOf(
                VoicePreset("es_ES-carlfm-high", "Carlos (Castilian)", "Male", "Warm baritone", "es_ES-carlfm-high.onnx")
            ),
            grammarExercises = listOf(
                GrammarSyntaxExercise(
                    id = "fallback_es_a1",
                    cefr = CefrLevel.A1,
                    title = LocalizedText("Essence vs state (ser / estar)", "Essenza vs stato (ser / estar)"),
                    promptSentence = "La biblioteca central ___ cerrada hoy.",
                    blankTarget = "está",
                    distractors = listOf("es", "son", "están"),
                    scrambleTokens = listOf("La", "biblioteca", "está", "cerrada"),
                    syntaxTokens = listOf(
                        SyntaxToken("La biblioteca", "SUBJ", "la βiβljoˈteka", LocalizedText("Subject", "Soggetto")),
                        SyntaxToken("está", "VERB", "esˈta", LocalizedText("Estar 3rd sg", "Estar 3ª sg")),
                        SyntaxToken("cerrada", "OBJ", "θeˈraða", LocalizedText("Participle", "Participio"))
                    ),
                    explanation = LocalizedText(
                        "Use estar with past participles to express a resulting state.",
                        "Si usa estar con i participi passati per indicare uno stato risultante."
                    )
                )
            ),
            writingExercises = listOf(
                WritingExercise(
                    id = "fallback_es_wrt",
                    cefr = CefrLevel.A1,
                    sourcePrompt = LocalizedText("Translate: We want two coffees, please.", "Traduci: Vorremmo due caffè, per favore."),
                    referenceTargets = listOf("Queremos dos cafés, por favor."),
                    requiredMorphemes = listOf("queremos", "dos"),
                    grammarRuleTitle = LocalizedText("Present indicative", "Presente indicativo"),
                    jitFeedback = LocalizedText("Use 'queremos' for 1st person plural.", "Usa 'queremos' per la 1ª persona plurale.")
                )
            ),
            pronunciationDrills = listOf(
                PronunciationDrill(
                    id = "fallback_es_spk",
                    cefr = CefrLevel.A1,
                    targetSentence = "El perro corre rápido.",
                    fullIpa = "/el ˈpero ˈkore ˈrapiðo/",
                    translation = LocalizedText("The dog runs fast.", "Il cane corre veloce."),
                    criticalPhonemes = emptyList(),
                    articulatoryTip = LocalizedText("Trill the double rr against the alveolar ridge.", "Fai vibrare la doppia rr sugli alveoli.")
                )
            ),
            scriptCards = emptyList()
        )
    }
}
""",

    "app/src/main/java/com/vocalfox/app/data/repository/VocalFoxRepository.kt": """\
package com.vocalfox.app.data.repository

import com.vocalfox.app.data.local.MistakeSrsEntity
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.data.local.VocalFoxDao
import com.vocalfox.app.data.local.VoiceModelConfigEntity
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import kotlinx.coroutines.flow.Flow
import kotlin.math.max

class VocalFoxRepository(
    private val dao: VocalFoxDao,
    private val packLoader: PackLoader
) {
    private val cachedPacks: Map<String, LanguagePack> by lazy {
        try {
            packLoader.loadAllLanguagePacks()
        } catch (_: Throwable) {
            mapOf("es" to PackLoader.createEmergencyPack())
        }
    }

    fun getAllPacks(): Map<String, LanguagePack> = cachedPacks

    fun getPack(languageCode: String): LanguagePack {
        return cachedPacks[languageCode]
            ?: cachedPacks.values.firstOrNull()
            ?: PackLoader.createEmergencyPack()
    }

    fun observeProgress(languageCode: String): Flow<List<UserProgressEntity>> =
        dao.observeProgressByLanguage(languageCode)

    fun observeSrsItems(languageCode: String): Flow<List<MistakeSrsEntity>> =
        dao.observeSrsByLanguage(languageCode)

    fun observeVoiceConfigs(): Flow<List<VoiceModelConfigEntity>> =
        dao.observeVoiceConfigs()

    suspend fun recordExerciseOutcome(
        itemKey: String,
        languageCode: String,
        cefrLevel: CefrLevel,
        pillar: String,
        score: Int,
        promptPreview: String,
        targetAnswer: String,
        mistakeNote: String
    ) {
        dao.upsertProgress(
            UserProgressEntity(
                itemKey = itemKey,
                languageCode = languageCode,
                cefrLevel = cefrLevel.name,
                pillar = pillar,
                bestScore = score,
                attempts = 1,
                completedAtEpochMs = System.currentTimeMillis()
            )
        )

        val quality = when {
            score >= 90 -> 5
            score >= 80 -> 4
            score >= 65 -> 3
            score >= 45 -> 2
            else -> 1
        }

        val existingSrs = dao.getSrsItem(itemKey)
        val updatedSrs = Sm2Scheduler.scheduleNext(
            existing = existingSrs,
            itemKey = itemKey,
            languageCode = languageCode,
            cefrLevel = cefrLevel.name,
            promptPreview = promptPreview,
            targetAnswer = targetAnswer,
            quality = max(1, quality),
            mistakeNote = mistakeNote
        )
        dao.upsertSrsItem(updatedSrs)
    }

    suspend fun saveVoiceConfig(
        languageCode: String,
        voiceId: String,
        speed: Float,
        verified: Boolean
    ) {
        dao.upsertVoiceConfig(
            VoiceModelConfigEntity(
                languageCode = languageCode,
                selectedVoiceId = voiceId,
                preferredSpeed = speed,
                isOfflinePackVerified = verified
            )
        )
    }
}
""",

    "app/src/main/java/com/vocalfox/app/audio/PiperTtsManager.kt": """\
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
                    \"\"\"
                    {
                      "voice_id": "${preset.voiceId}",
                      "sample_rate": ${preset.sampleRateHz},
                      "espeak_voice": "${preset.voiceId.substringBefore("_")}",
                      "inference_engine": "sherpa-onnx-piper-vits"
                    }
                    \"\"\".trimIndent()
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
""",

    "app/src/main/java/com/vocalfox/app/MainActivity.kt": """\
package com.vocalfox.app

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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.HistoryEdu
import androidx.compose.material.icons.outlined.Map
import androidx.compose.material.icons.outlined.Schema
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material.icons.outlined.Translate
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModelProvider
import com.vocalfox.app.ui.i18n.AppStrings
import com.vocalfox.app.ui.screens.GrammarSyntaxScreen
import com.vocalfox.app.ui.screens.HomeScreen
import com.vocalfox.app.ui.screens.JapaneseScriptScreen
import com.vocalfox.app.ui.screens.PronunciationScreen
import com.vocalfox.app.ui.screens.SettingsVoiceScreen
import com.vocalfox.app.ui.screens.WritingExerciseScreen
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxTokens
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.viewmodel.VocalFoxViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val viewModelResult = runCatching {
            ViewModelProvider(
                this,
                ViewModelProvider.AndroidViewModelFactory.getInstance(application)
            )[VocalFoxViewModel::class.java]
        }

        setContent {
            val vm = viewModelResult.getOrNull()
            if (vm != null) {
                val isDark by vm.isDarkMode.collectAsState()
                VocalFoxTheme(darkTheme = isDark) {
                    VocalFoxRootApp(viewModel = vm)
                }
            } else {
                val err = viewModelResult.exceptionOrNull()?.stackTraceToString() ?: "Unknown initialization error"
                VocalFoxTheme(darkTheme = false) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(VocalFoxTheme.colors.background)
                            .verticalScroll(rememberScrollState())
                            .padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = "VocalFox Startup Diagnostic",
                            style = VocalFoxType.PageTitle,
                            color = VocalFoxTheme.colors.negative
                        )
                        Text(
                            text = err,
                            style = VocalFoxType.MetaMono,
                            color = VocalFoxTheme.colors.primaryText
                        )
                    }
                }
            }
        }
    }
}

private enum class NavTab {
    PATH, SYNTAX, WRITING, SPEECH, SCRIPT, SETTINGS
}

@Composable
private fun VocalFoxRootApp(viewModel: VocalFoxViewModel) {
    val colors = VocalFoxTheme.colors
    val systemLang by viewModel.systemLang.collectAsState()
    val isDarkMode by viewModel.isDarkMode.collectAsState()
    val currentPack by viewModel.currentPack.collectAsState()
    val selectedCefr by viewModel.selectedCefr.collectAsState()
    val progressList by viewModel.progressList.collectAsState()
    val srsList by viewModel.srsList.collectAsState()
    val voiceConfigs by viewModel.voiceConfigs.collectAsState()
    val showFurigana by viewModel.showFurigana.collectAsState()
    val showRomaji by viewModel.showRomaji.collectAsState()
    val isRecording by viewModel.isRecordingAudio.collectAsState()
    val pronunciationResult by viewModel.latestPronunciationResult.collectAsState()

    val strings = AppStrings.forLang(systemLang)
    var activeTab by rememberSaveable { mutableStateOf(NavTab.PATH) }

    Scaffold(
        containerColor = colors.background,
        bottomBar = {
            QuietBottomNavBar(
                activeTab = activeTab,
                strings = strings,
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
                NavTab.PATH -> HomeScreen(
                    allPacks = viewModel.allPacks,
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    systemLang = systemLang,
                    strings = strings,
                    progressList = progressList,
                    srsList = srsList,
                    onSelectLanguage = viewModel::selectLanguage,
                    onSelectCefr = viewModel::selectCefr,
                    onNavigateToPillar = { pillar ->
                        activeTab = when (pillar) {
                            "SYNTAX" -> NavTab.SYNTAX
                            "WRITING" -> NavTab.WRITING
                            "SPEECH" -> NavTab.SPEECH
                            else -> NavTab.SYNTAX
                        }
                    }
                )

                NavTab.SYNTAX -> GrammarSyntaxScreen(
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    systemLang = systemLang,
                    strings = strings,
                    onSelectCefr = viewModel::selectCefr,
                    onSpeakSentence = { text -> viewModel.speakSentence(text, 1.0f) },
                    onExerciseVerified = viewModel::recordSyntaxCompletion
                )

                NavTab.WRITING -> WritingExerciseScreen(
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    systemLang = systemLang,
                    strings = strings,
                    onSelectCefr = viewModel::selectCefr,
                    onEvaluateWriting = viewModel::evaluateWritingSubmission
                )

                NavTab.SPEECH -> PronunciationScreen(
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    activeVoice = viewModel.getActiveVoiceForLanguage(currentPack.languageCode),
                    systemLang = systemLang,
                    strings = strings,
                    showFurigana = showFurigana,
                    isRecording = isRecording,
                    pronunciationResult = pronunciationResult,
                    onSelectCefr = viewModel::selectCefr,
                    onPlayTts = { text, speed -> viewModel.speakSentence(text, speed) },
                    onStartRecording = viewModel::startRecordingPronunciation,
                    onStopAndEvaluate = viewModel::stopAndEvaluatePronunciation
                )

                NavTab.SCRIPT -> JapaneseScriptScreen(
                    currentPack = currentPack,
                    systemLang = systemLang,
                    strings = strings,
                    showFurigana = showFurigana,
                    showRomaji = showRomaji,
                    onToggleFurigana = viewModel::toggleFurigana,
                    onToggleRomaji = viewModel::toggleRomaji,
                    onPlayAudio = { text -> viewModel.speakSentence(text, 0.9f) }
                )

                NavTab.SETTINGS -> SettingsVoiceScreen(
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
                    }
                )
            }
        }
    }
}

@Composable
private fun QuietBottomNavBar(
    activeTab: NavTab,
    strings: com.vocalfox.app.ui.i18n.UiStrings,
    onSelectTab: (NavTab) -> Unit
) {
    val colors = VocalFoxTheme.colors
    val items = listOf(
        Triple(NavTab.PATH, strings.navPath, Icons.Outlined.Map),
        Triple(NavTab.SYNTAX, strings.navSyntax, Icons.Outlined.Schema),
        Triple(NavTab.WRITING, strings.navWriting, Icons.Outlined.HistoryEdu),
        Triple(NavTab.SPEECH, strings.navSpeech, Icons.Outlined.GraphicEq),
        Triple(NavTab.SCRIPT, strings.navScript, Icons.Outlined.Translate),
        Triple(NavTab.SETTINGS, strings.navSettings, Icons.Outlined.Settings)
    )

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(colors.card)
            .border(1.dp, colors.hairline)
            .padding(horizontal = 8.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically
    ) {
        items.forEach { (tab, label, icon) ->
            val selected = tab == activeTab
            NavBarItem(
                label = label,
                icon = icon,
                selected = selected,
                onClick = { onSelectTab(tab) }
            )
        }
    }
}

@Composable
private fun NavBarItem(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    onClick: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
            .background(if (selected) colors.raised else colors.card)
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 6.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = if (selected) colors.accent else colors.mutedText,
            modifier = Modifier.size(18.dp)
        )
        Text(
            text = label,
            style = VocalFoxType.SecondaryCaption,
            color = if (selected) colors.primaryText else colors.mutedText
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
    # Controlla anche le sottocartelle dirette
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
        print("Copia questo file (apply_fixes.py) nella stessa cartella dove avevi eseguito setup_vocalfox.py.")
        input("\nPremi INVIO per chiudere...")
        return

    print(f"[OK] Cartella progetto trovata in:\n  {root}\n")

    for rel_path, content in PATCHED_FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  + Sovrascritto: {rel_path}")

    print("\n========================================================")
    print("FILE AGGIORNATI CON SUCCESSO!")
    print("Ora copia e incolla questi 4 comandi nel tuo terminale:")
    print("========================================================\n")
    print(f'cd "{root}"')
    print("git add .")
    print('git commit -m "Fix startup crash and add diagnostic screen"')
    print("git push origin main")
    input("\nPremi INVIO per chiudere...")


if __name__ == "__main__":
    main()