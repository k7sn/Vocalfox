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
