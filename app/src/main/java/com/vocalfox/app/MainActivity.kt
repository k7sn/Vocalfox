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
