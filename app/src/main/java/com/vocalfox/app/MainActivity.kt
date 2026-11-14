package com.vocalfox.app

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Add
import androidx.compose.material.icons.outlined.Bolt
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Explore
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material3.Icon
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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModelProvider
import com.vocalfox.app.ui.i18n.AppStrings
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.screens.GuidedLessonScreen
import com.vocalfox.app.ui.screens.GuidedUnitBundle
import com.vocalfox.app.ui.screens.HomeScreen
import com.vocalfox.app.ui.screens.JapaneseScriptScreen
import com.vocalfox.app.ui.screens.OnboardingScreen
import com.vocalfox.app.ui.screens.PronunciationScreen
import com.vocalfox.app.ui.screens.SettingsVoiceScreen
import com.vocalfox.app.ui.screens.SplashScreenOverlay
import com.vocalfox.app.ui.screens.buildGuidedUnitsForPack
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
    TODAY, EXPLORE, SPEECH_LAB, PROFILE
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
    val showFurigana by viewModel.showFurigana.collectAsState()
    val showRomaji by viewModel.showRomaji.collectAsState()
    val isRecording by viewModel.isRecordingAudio.collectAsState()
    val pronunciationResult by viewModel.latestPronunciationResult.collectAsState()

    val strings = AppStrings.forLang(systemLang)

    var showSplash by rememberSaveable { mutableStateOf(true) }
    var hasCompletedOnboarding by rememberSaveable {
        mutableStateOf(prefs.getBoolean("onboarding_done", false))
    }
    var activeTab by rememberSaveable { mutableStateOf(MainTab.TODAY) }
    var showQuickPopover by remember { mutableStateOf(false) }
    var activeGuidedUnit by remember { mutableStateOf<GuidedUnitBundle?>(null) }

    LaunchedEffect(Unit) {
        // Default to Italian if not configured yet
        viewModel.setSystemLanguage(SystemLang.IT)
        delay(1800L)
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

    // Full-Screen Guided Lesson Mode
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

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
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

                MainTab.EXPLORE -> JapaneseScriptScreen(
                    currentPack = currentPack,
                    systemLang = systemLang,
                    strings = strings,
                    showFurigana = showFurigana,
                    showRomaji = showRomaji,
                    onToggleFurigana = viewModel::toggleFurigana,
                    onToggleRomaji = viewModel::toggleRomaji,
                    onPlayAudio = { text -> viewModel.speakSentence(text, 0.9f) }
                )

                MainTab.SPEECH_LAB -> PronunciationScreen(
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

                MainTab.PROFILE -> Column(modifier = Modifier.fillMaxSize()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = strings.profileSettingsTitle,
                            style = VocalFoxType.SectionTitle,
                            color = colors.primaryText
                        )
                        Box(
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
                                style = VocalFoxType.MetaMono,
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
                        }
                    )
                }
            }
        }

        // PAGE 3 OF PDF: Popover Quick-Action Menu above the Floating "+" Button
        AnimatedVisibility(
            visible = showQuickPopover,
            enter = fadeIn(),
            exit = fadeOut(),
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 96.dp, start = 28.dp, end = 28.dp)
        ) {
            val units = buildGuidedUnitsForPack(currentPack, selectedCefr, systemLang)
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .shadow(16.dp, RoundedCornerShape(24.dp))
                    .clip(RoundedCornerShape(24.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(24.dp))
                    .padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                PopoverActionRow(
                    icon = Icons.Outlined.PlayArrow,
                    title = strings.startLessonPop,
                    badge = "+4",
                    isHighlighted = true,
                    onClick = {
                        showQuickPopover = false
                        activeGuidedUnit = units.firstOrNull()
                    }
                )
                PopoverActionRow(
                    icon = Icons.Outlined.Bolt,
                    title = strings.quickQuizPop,
                    badge = "+10",
                    isHighlighted = false,
                    onClick = {
                        showQuickPopover = false
                        activeGuidedUnit = units.lastOrNull()
                    }
                )
                PopoverActionRow(
                    icon = Icons.Outlined.GraphicEq,
                    title = strings.speechLabPop,
                    badge = "+3",
                    isHighlighted = false,
                    onClick = {
                        showQuickPopover = false
                        activeTab = MainTab.SPEECH_LAB
                    }
                )
                PopoverActionRow(
                    icon = Icons.Outlined.Refresh,
                    title = strings.reviewMistakesPop,
                    badge = "+2",
                    isHighlighted = false,
                    onClick = {
                        showQuickPopover = false
                        activeTab = MainTab.EXPLORE
                    }
                )
            }
        }

        // PAGE 3 OF PDF: Floating 3-Item Pill Bottom Navigation Bar
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 20.dp)
                .shadow(12.dp, RoundedCornerShape(36.dp))
                .clip(RoundedCornerShape(36.dp))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(36.dp))
                .padding(horizontal = 20.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.spacedBy(28.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            FloatingNavIcon(
                icon = Icons.Outlined.Home,
                label = strings.navToday,
                selected = activeTab == MainTab.TODAY,
                onClick = {
                    showQuickPopover = false
                    activeTab = MainTab.TODAY
                }
            )

            // Center Primary Action Circle ("+" / Quick Session Popover)
            Box(
                modifier = Modifier
                    .size(52.dp)
                    .clip(CircleShape)
                    .background(colors.accent)
                    .clickable { showQuickPopover = !showQuickPopover },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = if (showQuickPopover) Icons.Outlined.Close else Icons.Outlined.Add,
                    contentDescription = null,
                    tint = colors.onAccent,
                    modifier = Modifier.size(26.dp)
                )
            }

            FloatingNavIcon(
                icon = Icons.Outlined.Explore,
                label = strings.navExplore,
                selected = activeTab == MainTab.EXPLORE || activeTab == MainTab.SPEECH_LAB,
                onClick = {
                    showQuickPopover = false
                    activeTab = MainTab.EXPLORE
                }
            )
        }
    }
}

@Composable
private fun PopoverActionRow(
    icon: ImageVector,
    title: String,
    badge: String,
    isHighlighted: Boolean,
    onClick: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(if (isHighlighted) colors.raised else Color.Transparent)
            .clickable(onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = colors.accent,
                modifier = Modifier.size(20.dp)
            )
            Text(
                text = title,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )
        }
        Text(
            text = badge,
            style = VocalFoxType.MetaMono,
            color = colors.mutedText
        )
    }
}

@Composable
private fun FloatingNavIcon(
    icon: ImageVector,
    label: String,
    selected: Boolean,
    onClick: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(20.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 8.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = if (selected) colors.accent else colors.mutedText,
            modifier = Modifier.size(22.dp)
        )
        Text(
            text = label,
            style = VocalFoxType.BodyMedium,
            color = if (selected) colors.primaryText else colors.mutedText
        )
    }
}
