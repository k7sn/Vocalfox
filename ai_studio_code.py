#!/usr/bin/env python3
"""
upgrade_vocalfox_v2.py
Fix completo compilazione Kotlin + UI Design Example.pdf + Splash WebP + Dataset Espanso A1-B2.
"""

import shutil
from pathlib import Path

FILES: dict[str, str] = {
    "app/src/main/java/com/vocalfox/app/ui/i18n/AppStrings.kt": """\
package com.vocalfox.app.ui.i18n

enum class SystemLang(val code: String, val displayName: String) {
    IT("it", "Italiano"),
    EN("en", "English")
}

data class UiStrings(
    // V2 Navigation & Guided Flow
    val navToday: String,
    val navExplore: String,
    val startLessonPop: String,
    val quickQuizPop: String,
    val speechLabPop: String,
    val reviewMistakesPop: String,
    val dailyGoalTitle: String,
    val streakTitle: String,
    val wordsLearnedTitle: String,
    val startUnitAction: String,
    val onboardingWelcomeTitle: String,
    val onboardingWelcomeSub: String,
    val chooseUiLanguageLabel: String,
    val chooseTargetLanguageLabel: String,
    val startFromScratchTitle: String,
    val startFromScratchSub: String,
    val takePlacementTitle: String,
    val takePlacementSub: String,
    val placementHeader: String,
    val placementResultTitle: String,
    val stepLearnWords: String,
    val stepQuizChoice: String,
    val stepBuildSentence: String,
    val stepSpeakAloud: String,
    val tapWordToListenHint: String,
    val tapOptionToHearHint: String,
    val buildSentenceInstruction: String,
    val checkButton: String,
    val continueButton: String,
    val finishUnitButton: String,
    val unitCompletedTitle: String,
    val unitCompletedSubtitle: String,
    val listenNormal: String,
    val listenSlow: String,
    val tapToSpeak: String,
    val stopListening: String,
    val exploreHeader: String,
    val tabVocabulary: String,
    val tabAlphabetScript: String,
    val profileSettingsTitle: String,
    val changeLevelSection: String,
    val retakePlacementAction: String,
    val systemLanguageSection: String,
    val darkModeLabel: String,
    val voiceModelsSection: String,

    // Legacy & Secondary Screen Compatibility Labels (Human-Friendly, Zero Jargon)
    val navPath: String,
    val navSyntax: String,
    val navWriting: String,
    val navSpeech: String,
    val navScript: String,
    val navSettings: String,
    val pathHeader: String,
    val streakDaysLabel: String,
    val dueReviewsLabel: String,
    val masteredUnitsLabel: String,
    val vsLastWeek: String,
    val resumeStudyAction: String,
    val syntaxStudioHeader: String,
    val syntaxLegendTitle: String,
    val checkAnswerAction: String,
    val nextExerciseAction: String,
    val reorderInstruction: String,
    val grammarNoteLabel: String,
    val writingStudioHeader: String,
    val writingPromptLabel: String,
    val writingInputHint: String,
    val evaluateWritingAction: String,
    val expectedChecklistLabel: String,
    val pronunciationHeader: String,
    val playNormalAction: String,
    val playSlowAction: String,
    val holdToRecordAction: String,
    val stopRecordingAction: String,
    val phoneticBreakdownTitle: String,
    val articulatoryTipLabel: String,
    val scriptHeader: String,
    val showFuriganaLabel: String,
    val showRomajiLabel: String,
    val settingsHeader: String,
    val appearanceSection: String,
    val activeVoiceLabel: String,
    val previewVoiceAction: String,
    val offlineStorageNote: String
)

object AppStrings {
    private val italian = UiStrings(
        navToday = "Oggi",
        navExplore = "Esplora",
        startLessonPop = "Inizia lezione del giorno",
        quickQuizPop = "Sfida lampo (Tutte le domande)",
        speechLabPop = "Laboratorio di pronuncia",
        reviewMistakesPop = "Dizionario e Scrittura",
        dailyGoalTitle = "Obiettivo di oggi",
        streakTitle = "Giorni di fila",
        wordsLearnedTitle = "Unità superate",
        startUnitAction = "Inizia",
        onboardingWelcomeTitle = "Impara una lingua in modo naturale",
        onboardingWelcomeSub = "Percorso guidato passo dopo passo, audio chiaro e zero connessione richiesta.",
        chooseUiLanguageLabel = "La tua lingua",
        chooseTargetLanguageLabel = "Cosa vuoi imparare?",
        startFromScratchTitle = "Parto completamente da zero",
        startFromScratchSub = "Inizia dal Livello A1 con le prime parole, i saluti e le frasi base.",
        takePlacementTitle = "Conosco già qualcosa (Test rapido)",
        takePlacementSub = "Rispondi a 4 domande veloci per trovare il tuo livello di partenza.",
        placementHeader = "Test di livello iniziale",
        placementResultTitle = "Livello consigliato:",
        stepLearnWords = "Passo 1 · Ascolta e scopri le parole",
        stepQuizChoice = "Passo 2 · Scegli l'opzione corretta",
        stepBuildSentence = "Passo 3 · Componi la frase",
        stepSpeakAloud = "Passo 4 · Prova a pronunciarla",
        tapWordToListenHint = "Tocca qualsiasi scheda per sentire come si pronuncia",
        tapOptionToHearHint = "Tocca una risposta per ascoltarla, poi premi Verifica",
        buildSentenceInstruction = "Tocca i blocchi nell'ordine giusto per comporre la frase",
        checkButton = "Verifica risposta",
        continueButton = "Continua",
        finishUnitButton = "Completa unità",
        unitCompletedTitle = "Lezione completata",
        unitCompletedSubtitle = "Ottimo lavoro, hai padroneggiato tutte le frasi di questa unità.",
        listenNormal = "Ascolta",
        listenSlow = "Lento",
        tapToSpeak = "Tocca e parla al microfono",
        stopListening = "Ferma e valuta",
        exploreHeader = "Frasario e Scrittura",
        tabVocabulary = "Frasi chiave",
        tabAlphabetScript = "Scrittura e Suoni",
        profileSettingsTitle = "Profilo e Preferenze",
        changeLevelSection = "Cambia livello in qualsiasi momento",
        retakePlacementAction = "Rifai il test iniziale",
        systemLanguageSection = "Lingua dell'app",
        darkModeLabel = "Tema scuro riposante",
        voiceModelsSection = "Voce dell'insegnante",

        navPath = "Oggi",
        navSyntax = "Frasi",
        navWriting = "Scrittura",
        navSpeech = "Voce",
        navScript = "Alfabeto",
        navSettings = "Profilo",
        pathHeader = "Il tuo percorso",
        streakDaysLabel = "Giorni di fila",
        dueReviewsLabel = "Da ripassare",
        masteredUnitsLabel = "Completate",
        vsLastWeek = "+2 questa settimana",
        resumeStudyAction = "Continua lezione",
        syntaxStudioHeader = "Costruzione della frase",
        syntaxLegendTitle = "Tocca le parole per ascoltarle e vederne il significato",
        checkAnswerAction = "Verifica risposta",
        nextExerciseAction = "Prossima domanda",
        reorderInstruction = "Scegli la parola corretta per completare la frase",
        grammarNoteLabel = "Consiglio pratico",
        writingStudioHeader = "Pratica di traduzione",
        writingPromptLabel = "Traduci la seguente frase",
        writingInputHint = "Scrivi qui o tocca i suggerimenti sopra",
        evaluateWritingAction = "Controlla traduzione",
        expectedChecklistLabel = "Parole utili (tocca per inserire)",
        pronunciationHeader = "Allenamento pronuncia",
        playNormalAction = "Ascolta",
        playSlowAction = "Più lento",
        holdToRecordAction = "Tocca e ripeti la frase",
        stopRecordingAction = "Ferma e ascolta il risultato",
        phoneticBreakdownTitle = "Risultato parola per parola",
        articulatoryTipLabel = "Come pronunciarlo bene",
        scriptHeader = "Alfabeto, Kanji e Suoni",
        showFuriganaLabel = "Lettura",
        showRomajiLabel = "Pronuncia",
        settingsHeader = "Impostazioni e Voce",
        appearanceSection = "Aspetto",
        activeVoiceLabel = "Voce selezionata",
        previewVoiceAction = "Ascolta anteprima",
        offlineStorageNote = "Tutte le lezioni e le voci funzionano al 100% senza internet"
    )

    private val english = UiStrings(
        navToday = "Today",
        navExplore = "Explore",
        startLessonPop = "Start today's lesson",
        quickQuizPop = "Quick quiz (All questions)",
        speechLabPop = "Pronunciation studio",
        reviewMistakesPop = "Phrasebook & Script",
        dailyGoalTitle = "Today's goal",
        streakTitle = "Day streak",
        wordsLearnedTitle = "Units passed",
        startUnitAction = "Start",
        onboardingWelcomeTitle = "Learn a language naturally",
        onboardingWelcomeSub = "Step-by-step guided lessons, clear voice audio, 100% offline.",
        chooseUiLanguageLabel = "Your language",
        chooseTargetLanguageLabel = "What do you want to learn?",
        startFromScratchTitle = "I'm starting from scratch",
        startFromScratchSub = "Start at Level A1 with essential words, greetings, and core phrases.",
        takePlacementTitle = "I know some basics (Quick test)",
        takePlacementSub = "Answer 4 quick questions to find your ideal starting level.",
        placementHeader = "Quick placement test",
        placementResultTitle = "Recommended level:",
        stepLearnWords = "Step 1 · Listen & discover words",
        stepQuizChoice = "Step 2 · Pick the right word",
        stepBuildSentence = "Step 3 · Build the sentence",
        stepSpeakAloud = "Step 4 · Speak it aloud",
        tapWordToListenHint = "Tap any card to hear how it sounds",
        tapOptionToHearHint = "Tap an option to hear its pronunciation, then press Check",
        buildSentenceInstruction = "Tap the word tiles in the right order to build the sentence",
        checkButton = "Check answer",
        continueButton = "Continue",
        finishUnitButton = "Complete unit",
        unitCompletedTitle = "Lesson complete",
        unitCompletedSubtitle = "Great job, you mastered every phrase in this unit.",
        listenNormal = "Listen",
        listenSlow = "Slower",
        tapToSpeak = "Tap and speak aloud",
        stopListening = "Stop and score",
        exploreHeader = "Phrasebook & Script",
        tabVocabulary = "Key phrases",
        tabAlphabetScript = "Alphabet & Kanji",
        profileSettingsTitle = "Profile & Preferences",
        changeLevelSection = "Switch level anytime",
        retakePlacementAction = "Retake placement test",
        systemLanguageSection = "App language",
        darkModeLabel = "Dark theme",
        voiceModelsSection = "Teacher voice",

        navPath = "Today",
        navSyntax = "Sentences",
        navWriting = "Writing",
        navSpeech = "Speech",
        navScript = "Alphabet",
        navSettings = "Profile",
        pathHeader = "Your learning path",
        streakDaysLabel = "Day streak",
        dueReviewsLabel = "To review",
        masteredUnitsLabel = "Completed",
        vsLastWeek = "+2 this week",
        resumeStudyAction = "Continue lesson",
        syntaxStudioHeader = "Sentence building",
        syntaxLegendTitle = "Tap any word to hear it and see its meaning",
        checkAnswerAction = "Check answer",
        nextExerciseAction = "Next question",
        reorderInstruction = "Pick the right word to complete the sentence",
        grammarNoteLabel = "Helpful tip",
        writingStudioHeader = "Translation practice",
        writingPromptLabel = "Translate this sentence",
        writingInputHint = "Type here or tap the hint words above",
        evaluateWritingAction = "Check translation",
        expectedChecklistLabel = "Helpful words (tap to insert)",
        pronunciationHeader = "Pronunciation practice",
        playNormalAction = "Listen",
        playSlowAction = "Slower",
        holdToRecordAction = "Tap and repeat the sentence",
        stopRecordingAction = "Stop and see feedback",
        phoneticBreakdownTitle = "Word-by-word feedback",
        articulatoryTipLabel = "Pronunciation tip",
        scriptHeader = "Alphabet, Kanji & Sounds",
        showFuriganaLabel = "Reading",
        showRomajiLabel = "Pronunciation",
        settingsHeader = "Settings & Voice",
        appearanceSection = "Appearance",
        activeVoiceLabel = "Active voice",
        previewVoiceAction = "Preview voice",
        offlineStorageNote = "All lessons and voices work 100% offline without internet"
    )

    fun forLang(lang: SystemLang): UiStrings = when (lang) {
        SystemLang.IT -> italian
        SystemLang.EN -> english
    }
}
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/PronunciationScreen.kt": """\
package com.vocalfox.app.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.Stop
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.vocalfox.app.audio.PhonemeAccuracyStatus
import com.vocalfox.app.audio.PronunciationResult
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.domain.model.VoicePreset
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.MascotPedagogicalBanner
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxTokens
import com.vocalfox.app.ui.theme.VocalFoxType

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun PronunciationScreen(
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    activeVoice: VoicePreset,
    systemLang: SystemLang,
    strings: UiStrings,
    showFurigana: Boolean,
    isRecording: Boolean,
    pronunciationResult: PronunciationResult?,
    onSelectCefr: (CefrLevel) -> Unit,
    onPlayTts: (String, Float) -> Unit,
    onStartRecording: (PronunciationDrill) -> Unit,
    onStopAndEvaluate: (PronunciationDrill, String?) -> Unit
) {
    val context = LocalContext.current
    val colors = VocalFoxTheme.colors

    val drillsForLevel = remember(currentPack.languageCode, selectedCefr) {
        currentPack.pronunciationDrills.filter { it.cefr == selectedCefr }
            .ifEmpty { currentPack.pronunciationDrills }
    }
    var drillIndex by remember(currentPack.languageCode, selectedCefr) { mutableIntStateOf(0) }
    val drill = drillsForLevel[drillIndex % drillsForLevel.size]

    var selectedWordIndex by remember(drill.id, pronunciationResult) { mutableIntStateOf(0) }

    val micPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) onStartRecording(drill)
        else onStopAndEvaluate(drill, null)
    }

    val mascotState = when {
        pronunciationResult == null -> MascotState.LOGO_IDLE
        pronunciationResult.overallScore >= 85 -> MascotState.CELEBRATE
        pronunciationResult.overallScore >= 60 -> MascotState.THINKING
        else -> MascotState.ENCOURAGE_SAD
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 14.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = strings.pronunciationHeader,
            style = VocalFoxType.PageTitle,
            color = colors.primaryText
        )

        // Full-width level selector (Never squashes the title!)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            CefrLevel.entries.forEach { level ->
                val active = level == selectedCefr
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (active) colors.accent else colors.card)
                        .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                        .clickable { onSelectCefr(level) }
                        .padding(vertical = 10.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = level.name,
                        style = VocalFoxType.BodyMedium,
                        color = if (active) colors.onAccent else colors.primaryText
                    )
                }
            }
        }

        // Phrase Navigation Counter
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Frase ${drillIndex + 1} di ${drillsForLevel.size} · Voce: ${activeVoice.displayName}",
                style = VocalFoxType.SecondaryCaption,
                color = colors.secondaryText
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(8.dp))
                        .clickable {
                            drillIndex = if (drillIndex > 0) drillIndex - 1 else drillsForLevel.lastIndex
                        }
                        .padding(8.dp)
                ) {
                    Icon(Icons.Outlined.ArrowBack, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                }
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(8.dp))
                        .clickable {
                            drillIndex = (drillIndex + 1) % drillsForLevel.size
                        }
                        .padding(8.dp)
                ) {
                    Icon(Icons.Outlined.ArrowForward, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                }
            }
        }

        // Main Sentence Card
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            if (showFurigana && drill.furiganaOrReading.isNotBlank()) {
                Text(
                    text = drill.furiganaOrReading,
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.accent
                )
            }

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
                        .clickable { onPlayTts(drill.targetSentence, 1.0f) }
                        .padding(vertical = 12.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Outlined.VolumeUp, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(strings.playNormalAction, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                }

                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(12.dp))
                        .background(colors.raised)
                        .clickable { onPlayTts(drill.targetSentence, 0.75f) }
                        .padding(vertical = 12.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Outlined.SlowMotionVideo, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(strings.playSlowAction, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(if (isRecording) colors.negative else colors.accent)
                    .clickable {
                        if (isRecording) {
                            onStopAndEvaluate(drill, null)
                        } else {
                            val granted = ContextCompat.checkSelfPermission(
                                context,
                                Manifest.permission.RECORD_AUDIO
                            ) == PackageManager.PERMISSION_GRANTED
                            if (granted) onStartRecording(drill)
                            else micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    }
                    .padding(vertical = 14.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (isRecording) Icons.Outlined.Stop else Icons.Outlined.Mic,
                    contentDescription = null,
                    tint = colors.onAccent,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (isRecording) strings.stopRecordingAction else strings.holdToRecordAction,
                    style = VocalFoxType.BodyMedium,
                    color = colors.onAccent
                )
            }
        }

        if (pronunciationResult != null) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "${strings.phoneticBreakdownTitle} (${pronunciationResult.overallScore}%)",
                    style = VocalFoxType.SectionTitle,
                    color = colors.primaryText
                )

                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    pronunciationResult.wordFeedbacks.forEachIndexed { idx, wf ->
                        val statusColor = when (wf.status) {
                            PhonemeAccuracyStatus.ACCURATE -> colors.positive
                            PhonemeAccuracyStatus.STRESS_OR_PITCH -> colors.warning
                            PhonemeAccuracyStatus.MISPRONOUNCED -> colors.negative
                        }
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(10.dp))
                                .background(if (selectedWordIndex == idx) colors.raised else colors.background)
                                .border(2.dp, statusColor, RoundedCornerShape(10.dp))
                                .clickable {
                                    selectedWordIndex = idx
                                    onPlayTts(wf.word, 0.85f)
                                }
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
        }

        MascotPedagogicalBanner(
            state = mascotState,
            title = strings.articulatoryTipLabel,
            subtitle = drill.articulatoryTip.get(systemLang)
        )

        Spacer(modifier = Modifier.height(100.dp))
    }
}
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/SettingsVoiceScreen.kt": """\
package com.vocalfox.app.ui.screens

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
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
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
    onPreviewVoice: (String, VoicePreset) -> Unit
) {
    val colors = VocalFoxTheme.colors

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
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
                            .clickable { onSelectSystemLang(lang) }
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
                onCheckedChange = onToggleDarkMode,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = colors.onAccent,
                    checkedTrackColor = colors.accent
                )
            )
        }

        // Clean Teacher Voice Picker (No technical .onnx file paths shown)
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
                                .clickable { onSelectVoicePreset(pack.languageCode, preset) }
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

        Spacer(modifier = Modifier.height(100.dp))
    }
}
""",

    "app/src/main/assets/packs/es_pack.json": """\
{
  "languageCode": "es",
  "languageName": {
    "en": "Spanish",
    "it": "Spagnolo"
  },
  "availableVoices": [
    {
      "voiceId": "es_ES-carlfm-high",
      "displayName": "Carlos (Spagna)",
      "gender": "Maschile",
      "timbre": "Calda e naturale",
      "onnxFileName": "es_ES-carlfm-high.onnx",
      "sampleRateHz": 22050
    },
    {
      "voiceId": "es_MX-ald-medium",
      "displayName": "Elena (Studio)",
      "gender": "Femminile",
      "timbre": "Chiara e scandita",
      "onnxFileName": "es_MX-ald-medium.onnx",
      "sampleRateHz": 22050
    }
  ],
  "grammarExercises": [
    {
      "id": "es_a1_u1",
      "cefr": "A1",
      "title": {
        "en": "Unit 1 · Greetings & ordering at a café",
        "it": "Unità 1 · Saluti e ordinare al bar"
      },
      "promptSentence": "Hola, buenos días. Yo ___ un café con leche, por favor.",
      "blankTarget": "quiero",
      "distractors": ["queremos", "eres", "estoy"],
      "scrambleTokens": ["Yo", "quiero", "un", "café", "con", "leche"],
      "syntaxTokens": [
        {
          "surface": "Buenos días",
          "roleCode": "A1",
          "ipa": "ˈbwenos ˈðias",
          "gloss": {
            "en": "Good morning",
            "it": "Buongiorno (usato fino a pranzo)"
          }
        },
        {
          "surface": "Yo quiero",
          "roleCode": "VERB",
          "ipa": "ʝo ˈkjeɾo",
          "gloss": {
            "en": "I want / I would like",
            "it": "Io voglio / Vorrei (da querer)"
          }
        },
        {
          "surface": "un café con leche",
          "roleCode": "OBJ",
          "ipa": "uŋ kaˈfe kon ˈletʃe",
          "gloss": {
            "en": "a coffee with milk",
            "it": "un caffè macchiato / caffellatte"
          }
        },
        {
          "surface": "por favor",
          "roleCode": "PART",
          "ipa": "poɾ faˈβoɾ",
          "gloss": {
            "en": "please",
            "it": "per favore"
          }
        }
      ],
      "explanation": {
        "en": "Use 'quiero' (I want) or 'quisiera' (I would like) followed by what you are ordering.",
        "it": "Per ordinare in modo semplice usa 'quiero' (voglio/vorrei) seguito dalla bevanda o dal piatto."
      }
    },
    {
      "id": "es_a1_u2",
      "cefr": "A1",
      "title": {
        "en": "Unit 2 · Introducing yourself (Ser vs Estar)",
        "it": "Unità 2 · Presentarsi e dire dove ci si trova"
      },
      "promptSentence": "Yo soy de Roma, pero ahora ___ en Madrid.",
      "blankTarget": "estoy",
      "distractors": ["soy", "eres", "está"],
      "scrambleTokens": ["Yo", "soy", "de", "Roma", "pero", "estoy", "en", "Madrid"],
      "syntaxTokens": [
        {
          "surface": "Yo soy de",
          "roleCode": "SUBJ",
          "ipa": "ʝo ˈsoj ðe",
          "gloss": {
            "en": "I am from (origin)",
            "it": "Io sono di (origine permanente -> ser)"
          }
        },
        {
          "surface": "pero ahora",
          "roleCode": "CONN",
          "ipa": "ˈpeɾo aˈoɾa",
          "gloss": {
            "en": "but now",
            "it": "ma adesso / ora"
          }
        },
        {
          "surface": "estoy en Madrid",
          "roleCode": "VERB",
          "ipa": "esˈtoj en maˈðɾið",
          "gloss": {
            "en": "I am located in Madrid",
            "it": "mi trovo a Madrid (posizione -> estar)"
          }
        }
      ],
      "explanation": {
        "en": "Use 'ser' (soy) for your hometown or nationality, and 'estar' (estoy) for where you are located right now.",
        "it": "Usa 'ser' (soy) per la tua città d'origine o nazionalità, ed 'estar' (estoy) per indicare dove ti trovi."
      }
    },
    {
      "id": "es_a1_u3",
      "cefr": "A1",
      "title": {
        "en": "Unit 3 · Asking for the bill & prices",
        "it": "Unità 3 · Chiedere il conto e i prezzi"
      },
      "promptSentence": "Disculpe, ¿cuánto ___ estos dos bocadillos?",
      "blankTarget": "cuestan",
      "distractors": ["cuesta", "cuesto", "están"],
      "scrambleTokens": ["¿Cuánto", "cuestan", "estos", "dos", "bocadillos?"],
      "syntaxTokens": [
        {
          "surface": "Disculpe",
          "roleCode": "PART",
          "ipa": "disˈkulpe",
          "gloss": {
            "en": "Excuse me (polite)",
            "it": "Mi scusi (formale)"
          }
        },
        {
          "surface": "¿cuánto cuestan",
          "roleCode": "VERB",
          "ipa": "ˈkwanto ˈkwestan",
          "gloss": {
            "en": "how much do they cost",
            "it": "quanto costano (plurale da costar)"
          }
        },
        {
          "surface": "la cuenta",
          "roleCode": "OBJ",
          "ipa": "la ˈkwenta",
          "gloss": {
            "en": "the bill / check",
            "it": "il conto"
          }
        }
      ],
      "explanation": {
        "en": "Use '¿Cuánto cuesta?' for a single item and '¿Cuánto cuestan?' for plural items.",
        "it": "Usa '¿Cuánto cuesta?' per un oggetto singolare e '¿Cuánto cuestan?' quando chiedi il prezzo di più cose."
      }
    },
    {
      "id": "es_a2_u1",
      "cefr": "A2",
      "title": {
        "en": "Unit 1 · Talking about yesterday",
        "it": "Unità 1 · Raccontare cosa hai fatto ieri"
      },
      "promptSentence": "Ayer nosotros ___ al museo y cenamos cerca del mar.",
      "blankTarget": "fuimos",
      "distractors": ["vamos", "iban", "fue"],
      "scrambleTokens": ["Ayer", "nosotros", "fuimos", "al", "museo"],
      "syntaxTokens": [
        {
          "surface": "Ayer",
          "roleCode": "CONN",
          "ipa": "aˈʝeɾ",
          "gloss": {
            "en": "Yesterday",
            "it": "Ieri"
          }
        },
        {
          "surface": "fuimos al museo",
          "roleCode": "VERB",
          "ipa": "ˈfwimos al muˈseo",
          "gloss": {
            "en": "we went to the museum",
            "it": "siamo andati al museo (passato di ir)"
          }
        },
        {
          "surface": "cerca del mar",
          "roleCode": "OBJ",
          "ipa": "ˈθeɾka ðel maɾ",
          "gloss": {
            "en": "near the sea",
            "it": "vicino al mare"
          }
        }
      ],
      "explanation": {
        "en": "With specific past time markers like 'ayer' (yesterday), use the indefinido: 'fui, fuiste, fue, fuimos'.",
        "it": "Con indicatori precisi come 'ayer' (ieri), usa il passato semplice (indefinido): 'fui, fuiste, fue, fuimos'."
      }
    },
    {
      "id": "es_a2_u2",
      "cefr": "A2",
      "title": {
        "en": "Unit 2 · Ongoing actions in the past",
        "it": "Unità 2 · Azioni in corso nel passato"
      },
      "promptSentence": "Mientras yo ___ el informe, sonó el teléfono.",
      "blankTarget": "leía",
      "distractors": ["leí", "leo", "leeré"],
      "scrambleTokens": ["Mientras", "yo", "leía", "el", "informe"],
      "syntaxTokens": [
        {
          "surface": "Mientras",
          "roleCode": "CONN",
          "ipa": "ˈmjentɾas",
          "gloss": {
            "en": "While",
            "it": "Mentre"
          }
        },
        {
          "surface": "yo leía",
          "roleCode": "VERB",
          "ipa": "ʝo leˈia",
          "gloss": {
            "en": "I was reading",
            "it": "io leggevo / stavo leggendo"
          }
        },
        {
          "surface": "sonó el teléfono",
          "roleCode": "V2",
          "ipa": "soˈno el teˈlefono",
          "gloss": {
            "en": "the phone rang",
            "it": "è squillato il telefono"
          }
        }
      ],
      "explanation": {
        "en": "Use the imperfect ('leía') for the background action in progress, and the preterite ('sonó') for the sudden event.",
        "it": "Usa l'imperfetto ('leía') per l'azione in corso e il passato semplice ('sonó') per l'evento improvviso."
      }
    },
    {
      "id": "es_b1_u1",
      "cefr": "B1",
      "title": {
        "en": "Unit 1 · Expressing wishes & doubts",
        "it": "Unità 1 · Esprimere desideri, dubbi e consigli"
      },
      "promptSentence": "Te recomiendo que ___ el tren de alta velocidad.",
      "blankTarget": "tomes",
      "distractors": ["tomas", "tomarás", "tomaste"],
      "scrambleTokens": ["Te", "recomiendo", "que", "tomes", "el", "tren"],
      "syntaxTokens": [
        {
          "surface": "Te recomiendo que",
          "roleCode": "CONN",
          "ipa": "te rekoˈmjendo ke",
          "gloss": {
            "en": "I recommend that you",
            "it": "Ti consiglio di / che tu"
          }
        },
        {
          "surface": "tomes",
          "roleCode": "SUBJ_MOD",
          "ipa": "ˈtomes",
          "gloss": {
            "en": "take (present subjunctive)",
            "it": "prenda (congiuntivo presente di tomar)"
          }
        },
        {
          "surface": "alta velocidad",
          "roleCode": "OBJ",
          "ipa": "ˈalta βeloθiˈðað",
          "gloss": {
            "en": "high speed",
            "it": "alta velocità"
          }
        }
      ],
      "explanation": {
        "en": "Verbs of advice and desire ('recomendar que', 'querer que') trigger the subjunctive ('tomes') in the second clause.",
        "it": "I verbi di consiglio o desiderio ('recomendar que', 'querer que') richiedono il congiuntivo ('tomes')."
      }
    },
    {
      "id": "es_b1_u2",
      "cefr": "B1",
      "title": {
        "en": "Unit 2 · Future plans with 'cuando'",
        "it": "Unità 2 · Progetti futuri con 'cuando'"
      },
      "promptSentence": "Cuando ___ a Barcelona, visitaremos la Sagrada Familia.",
      "blankTarget": "lleguemos",
      "distractors": ["llegamos", "llegaremos", "llegábamos"],
      "scrambleTokens": ["Cuando", "lleguemos", "a", "Barcelona", "visitaremos"],
      "syntaxTokens": [
        {
          "surface": "Cuando lleguemos",
          "roleCode": "SUBJ_MOD",
          "ipa": "ˈkwando ʎeˈɣemos",
          "gloss": {
            "en": "When we arrive (future event)",
            "it": "Quando arriveremo (in spagnolo vuole il congiuntivo)"
          }
        },
        {
          "surface": "visitaremos",
          "roleCode": "VERB",
          "ipa": "bisitaˈɾemos",
          "gloss": {
            "en": "we will visit",
            "it": "visiteremo"
          }
        }
      ],
      "explanation": {
        "en": "Unlike Italian or English, Spanish uses 'cuando + present subjunctive' ('cuando lleguemos') when talking about the future.",
        "it": "A differenza dell'italiano, dopo 'cuando' riferito al futuro lo spagnolo usa sempre il congiuntivo presente ('cuando lleguemos')."
      }
    },
    {
      "id": "es_b2_u1",
      "cefr": "B2",
      "title": {
        "en": "Unit 1 · Hypothetical past (If I had known...)",
        "it": "Unità 1 · Ipotesi nel passato (Se avessi saputo...)"
      },
      "promptSentence": "Si ___ las cláusulas a tiempo, habríamos evitado el problema.",
      "blankTarget": "hubiéramos revisado",
      "distractors": ["revisábamos", "habremos revisado", "revisaríamos"],
      "scrambleTokens": ["Si", "hubiéramos", "revisado", "las", "cláusulas"],
      "syntaxTokens": [
        {
          "surface": "Si hubiéramos revisado",
          "roleCode": "SUBJ_MOD",
          "ipa": "si uˈβjeɾamos reβiˈsaðo",
          "gloss": {
            "en": "If we had reviewed",
            "it": "Se avessimo controllato"
          }
        },
        {
          "surface": "habríamos evitado",
          "roleCode": "VERB",
          "ipa": "aˈβɾiamos eβiˈtaðo",
          "gloss": {
            "en": "we would have avoided",
            "it": "avremmo evitato"
          }
        }
      ],
      "explanation": {
        "en": "For past hypothetical situations, pair 'Si + hubiera/hubiéramos + participle' with 'habría + participle'.",
        "it": "Per le ipotesi nel passato usa 'Si + hubiera/hubiéramos + participio' seguito dal condizionale composto ('habríamos evitado')."
      }
    },
    {
      "id": "es_b2_u2",
      "cefr": "B2",
      "title": {
        "en": "Unit 2 · Advanced debate & concession",
        "it": "Unità 2 · Argomentare e concedere (Por muy... que)"
      },
      "promptSentence": "Por muy difícil que ___ el proyecto, lo terminaremos hoy.",
      "blankTarget": "parezca",
      "distractors": ["parece", "pareció", "parecería"],
      "scrambleTokens": ["Por", "muy", "difícil", "que", "parezca"],
      "syntaxTokens": [
        {
          "surface": "Por muy difícil que",
          "roleCode": "CONN",
          "ipa": "poɾ muj ðiˈfiθil ke",
          "gloss": {
            "en": "No matter how difficult",
            "it": "Per quanto difficile"
          }
        },
        {
          "surface": "parezca",
          "roleCode": "SUBJ_MOD",
          "ipa": "paˈɾeθka",
          "gloss": {
            "en": "it may seem (subjunctive of parecer)",
            "it": "possa sembrare (congiuntivo di parecer)"
          }
        }
      ],
      "explanation": {
        "en": "'Por muy + adjective + que + subjunctive' expresses 'however / no matter how' in fluent B2 Spanish.",
        "it": "La struttura 'Por muy + aggettivo + que + congiuntivo' traduce 'per quanto possa essere...'."
      }
    }
  ],
  "writingExercises": [
    {
      "id": "es_a1_w1",
      "cefr": "A1",
      "sourcePrompt": {
        "en": "We want two coffees with hot milk, please.",
        "it": "Vorremmo due caffè con latte caldo, per favore."
      },
      "referenceTargets": ["Queremos dos cafés con leche caliente por favor"],
      "requiredMorphemes": ["queremos", "dos", "leche", "caliente"],
      "grammarRuleTitle": {
        "en": "Ordering drinks and food",
        "it": "Ordinare bevande al bar"
      },
      "jitFeedback": {
        "en": "In Spanish, adjectives like 'caliente' (hot) go after the noun 'leche' (milk).",
        "it": "In spagnolo l'aggettivo 'caliente' (caldo) va dopo il nome 'leche' (latte)."
      }
    },
    {
      "id": "es_a1_w2",
      "cefr": "A1",
      "sourcePrompt": {
        "en": "I am from Italy, but now I am in Madrid.",
        "it": "Io sono italiano, ma adesso mi trovo a Madrid."
      },
      "referenceTargets": ["Yo soy de Italia pero ahora estoy en Madrid"],
      "requiredMorphemes": ["soy", "pero", "ahora", "estoy"],
      "grammarRuleTitle": {
        "en": "Origin (soy) vs current location (estoy)",
        "it": "Origine (soy) vs posizione attuale (estoy)"
      },
      "jitFeedback": {
        "en": "Use 'soy' for origin and 'estoy' with 'en' for where you are right now.",
        "it": "Usa 'soy' per l'origine ed 'estoy en' per il luogo in cui ti trovi ora."
      }
    },
    {
      "id": "es_a2_w1",
      "cefr": "A2",
      "sourcePrompt": {
        "en": "Yesterday I gave the keys to my neighbor before leaving.",
        "it": "Ieri ho dato le chiavi al mio vicino prima di uscire."
      },
      "referenceTargets": ["Ayer le di las llaves a mi vecino antes de salir"],
      "requiredMorphemes": ["ayer", "le di", "llaves", "antes de salir"],
      "grammarRuleTitle": {
        "en": "Past actions & 'antes de + infinitive'",
        "it": "Raccontare il passato e 'antes de + infinito'"
      },
      "jitFeedback": {
        "en": "Remember to place 'le' before 'di' (I gave him).",
        "it": "Ricorda di mettere 'le' prima di 'di' (gli ho dato)."
      }
    },
    {
      "id": "es_b1_w1",
      "cefr": "B1",
      "sourcePrompt": {
        "en": "When you arrive at the station, call me on the phone.",
        "it": "Quando arrivi alla stazione, chiamami al telefono."
      },
      "referenceTargets": ["Cuando llegues a la estación llámame por teléfono"],
      "requiredMorphemes": ["cuando", "llegues", "estación", "llámame"],
      "grammarRuleTitle": {
        "en": "Future time clause with 'cuando + subjunctive'",
        "it": "Frasi al futuro con 'cuando + congiuntivo'"
      },
      "jitFeedback": {
        "en": "Use 'cuando llegues' (subjunctive) for future events.",
        "it": "Usa 'cuando llegues' (congiuntivo) perché l'azione deve ancora avvenire."
      }
    },
    {
      "id": "es_b2_w1",
      "cefr": "B2",
      "sourcePrompt": {
        "en": "No matter how complex the negotiation seems, we will find an agreement.",
        "it": "Per quanto complessa sembri la trattativa, troveremo un accordo."
      },
      "referenceTargets": ["Por muy compleja que parezca la negociación encontraremos un acuerdo"],
      "requiredMorphemes": ["por muy", "parezca", "encontraremos", "acuerdo"],
      "grammarRuleTitle": {
        "en": "Concessive structure 'Por muy ... que'",
        "it": "Struttura concessiva 'Por muy ... que'"
      },
      "jitFeedback": {
        "en": "Pair 'Por muy compleja que parezca' with the future 'encontraremos'.",
        "it": "Abbina 'Por muy compleja que parezca' al futuro 'encontraremos'."
      }
    }
  ],
  "pronunciationDrills": [
    {
      "id": "es_a1_s1",
      "cefr": "A1",
      "targetSentence": "Hola, buenos días, quiero un café con leche caliente.",
      "furiganaOrReading": "Pronuncia chiara di 'qu' (ch) e 'll/ch'",
      "fullIpa": "/ˈola ˈbwenos ˈðias ˈkjeɾo uŋ kaˈfe kon ˈletʃe kaˈljente/",
      "translation": {
        "en": "Hello, good morning, I would like a coffee with hot milk.",
        "it": "Ciao, buongiorno, vorrei un caffè con latte caldo."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Remember that the 'h' in 'Hola' is completely silent, and 'quiero' is pronounced 'kiero'.",
        "it": "Ricorda che la 'h' di 'Hola' è sempre muta, e 'quiero' si legge 'chiero'."
      }
    },
    {
      "id": "es_a2_s1",
      "cefr": "A2",
      "targetSentence": "Ayer llevé las llaves bajo la lluvia suave.",
      "furiganaOrReading": "Suono morbido della B e della V spagnola",
      "fullIpa": "/aˈʝeɾ ʎeˈβe las ˈʎaβes ˈbaxo la ˈʎuβja ˈswaβe/",
      "translation": {
        "en": "Yesterday I carried the keys under the gentle rain.",
        "it": "Ieri ho portato le chiavi sotto la pioggia leggera."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "In Spanish, 'b' and 'v' sound identical: keep your lips soft without pressing your teeth on your lip.",
        "it": "In spagnolo la 'b' e la 'v' hanno lo stesso identico suono morbido fra le labbra."
      }
    },
    {
      "id": "es_b1_s1",
      "cefr": "B1",
      "targetSentence": "Cuando llegues a la estación, llámame para ir juntos.",
      "furiganaOrReading": "Intonazione fluida e suono aspirato della J in 'juntos'",
      "fullIpa": "/ˈkwando ˈʎeɣes a la estaˈθjon ˈʎamame ˈpaɾa iɾ ˈxuntos/",
      "translation": {
        "en": "When you arrive at the station, call me so we can go together.",
        "it": "Quando arrivi alla stazione, chiamami per andare insieme."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Pronounce 'gue' in 'llegues' with a hard G (like 'gh' in Italian), keeping the 'u' silent.",
        "it": "Pronuncia 'gue' in 'llegues' come il suono italiano 'ghe', senza far sentire la 'u'."
      }
    },
    {
      "id": "es_b2_s1",
      "cefr": "B2",
      "targetSentence": "Si hubiéramos previsto las consecuencias, habríamos actuado con prudencia.",
      "furiganaOrReading": "Legatura vocale (sinalefe) e ritmo naturale B2",
      "fullIpa": "/si uˈβjeɾamos pɾeˈβisto las konsekˈwenθjas aˈβɾiamos akˈtwaðo kon pɾuˈðenθja/",
      "translation": {
        "en": "Had we foreseen the consequences, we would have acted with prudence.",
        "it": "Se avessimo previsto le conseguenze, avremmo agito con prudenza."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Link 'Si hubiéramos' smoothly in a single breath without pausing between the words.",
        "it": "Unisci 'Si hubiéramos' in un solo fiato fluido (la 'h' non interrompe il suono)."
      }
    }
  ],
  "scriptCards": [
    {
      "symbol": "ñ",
      "scriptCategory": "Suoni Spagnoli",
      "readingOrFurigana": "Eñe",
      "romajiOrIpa": "gn",
      "meaning": {
        "en": "Like 'gn' in Italian 'montagna' (mañana, año)",
        "it": "Si pronuncia esattamente come 'gn' in italiano (mañana, año)"
      },
      "exampleWord": "mañana",
      "exampleReading": "magnana (domani / mattina)",
      "strokeCount": 2
    },
    {
      "symbol": "ll",
      "scriptCategory": "Suoni Spagnoli",
      "readingOrFurigana": "Doble ele",
      "romajiOrIpa": "gl / y",
      "meaning": {
        "en": "Palatal sound similar to 'gli' or 'y' (llave, calle)",
        "it": "Suono dolce simile a 'gli' o 'j' (llave = chiave, calle = via)"
      },
      "exampleWord": "calle",
      "exampleReading": "caglie / caye (strada)",
      "strokeCount": 2
    },
    {
      "symbol": "j",
      "scriptCategory": "Suoni Spagnoli",
      "readingOrFurigana": "Jota",
      "romajiOrIpa": "kh aspirata",
      "meaning": {
        "en": "Strong throat breath like 'ch' in Loch (jamón, viaje)",
        "it": "Suono aspirato di gola (jamón = prosciutto, viaje = viaggio)"
      },
      "exampleWord": "viaje",
      "exampleReading": "viakhe (viaggio)",
      "strokeCount": 1
    },
    {
      "symbol": "qu",
      "scriptCategory": "Suoni Spagnoli",
      "readingOrFurigana": "Qu + e/i",
      "romajiOrIpa": "ch dura",
      "meaning": {
        "en": "Pronounced like 'k', the 'u' is silent (quiero, queso)",
        "it": "Si legge come 'ch' dura italiana senza pronunciare la 'u' (quiero, queso)"
      },
      "exampleWord": "queso",
      "exampleReading": "cheso (formaggio)",
      "strokeCount": 2
    }
  ]
}
""",

    "app/src/main/assets/packs/de_pack.json": """\
{
  "languageCode": "de",
  "languageName": {
    "en": "German",
    "it": "Tedesco"
  },
  "availableVoices": [
    {
      "voiceId": "de_DE-thorsten-high",
      "displayName": "Thorsten (Hochdeutsch)",
      "gender": "Maschile",
      "timbre": "Calda e chiara",
      "onnxFileName": "de_DE-thorsten-high.onnx",
      "sampleRateHz": 22050
    },
    {
      "voiceId": "de_DE-kerstin-medium",
      "displayName": "Kerstin (Hannover)",
      "gender": "Femminile",
      "timbre": "Nitida e scandita",
      "onnxFileName": "de_DE-kerstin-medium.onnx",
      "sampleRateHz": 22050
    }
  ],
  "grammarExercises": [
    {
      "id": "de_a1_u1",
      "cefr": "A1",
      "title": {
        "en": "Unit 1 · Greetings & ordering in Berlin",
        "it": "Unità 1 · Salutare e ordinare a Berlino"
      },
      "promptSentence": "Guten Tag, ich ___ gern einen Kaffee und ein Wasser.",
      "blankTarget": "möchte",
      "distractors": ["möchten", "bin", "hast"],
      "scrambleTokens": ["Ich", "möchte", "gern", "einen", "Kaffee"],
      "syntaxTokens": [
        {
          "surface": "Guten Tag",
          "roleCode": "A1",
          "ipa": "ˈɡuːtn̩ taːk",
          "gloss": {
            "en": "Good day / Hello",
            "it": "Buongiorno"
          }
        },
        {
          "surface": "ich möchte gern",
          "roleCode": "V2",
          "ipa": "ɪç ˈmœçtə ɡɛʁn",
          "gloss": {
            "en": "I would gladly like",
            "it": "vorrei volentieri (cortese)"
          }
        },
        {
          "surface": "einen Kaffee",
          "roleCode": "OBJ",
          "ipa": "ˈaɪnən ˈkafe",
          "gloss": {
            "en": "a coffee (accusative)",
            "it": "un caffè (oggetto diretto)"
          }
        }
      ],
      "explanation": {
        "en": "'Ich möchte gern...' is the most natural, polite way to order anything in German.",
        "it": "'Ich möchte gern...' (vorrei volentieri) è la formula più naturale ed educata per ordinare in tedesco."
      }
    },
    {
      "id": "de_a1_u2",
      "cefr": "A1",
      "title": {
        "en": "Unit 2 · Time words at the start of a sentence",
        "it": "Unità 2 · Quando inizi la frase con 'Oggi' o 'Domani'"
      },
      "promptSentence": "Morgen ___ ich mit dem Zug nach München.",
      "blankTarget": "fahre",
      "distractors": ["fahren", "fährst", "gefahren"],
      "scrambleTokens": ["Morgen", "fahre", "ich", "nach", "München"],
      "syntaxTokens": [
        {
          "surface": "Morgen",
          "roleCode": "CONN",
          "ipa": "ˈmɔʁɡn̩",
          "gloss": {
            "en": "Tomorrow",
            "it": "Domani"
          }
        },
        {
          "surface": "fahre ich",
          "roleCode": "V2",
          "ipa": "ˈfaːʁə ɪç",
          "gloss": {
            "en": "I travel (verb before 'ich')",
            "it": "vado io (il verbo resta sempre al 2° posto)"
          }
        },
        {
          "surface": "mit dem Zug",
          "roleCode": "OBJ",
          "ipa": "mɪt deːm tsuːk",
          "gloss": {
            "en": "by train",
            "it": "con il treno"
          }
        }
      ],
      "explanation": {
        "en": "In German, the action verb is always the second block: if you start with 'Morgen', say 'Morgen fahre ich' (not 'Morgen ich fahre').",
        "it": "In tedesco il verbo sta sempre al 2° posto: se inizi con 'Morgen' (Domani), dici 'Morgen fahre ich'."
      }
    },
    {
      "id": "de_a2_u1",
      "cefr": "A2",
      "title": {
        "en": "Unit 1 · Explaining why with 'weil' (because)",
        "it": "Unità 1 · Spiegare il perché con 'weil' (perché)"
      },
      "promptSentence": "Ich bleibe heute zu Hause, weil es draußen stark ___.",
      "blankTarget": "regnet",
      "distractors": ["regnen", "geregnet", "regnest"],
      "scrambleTokens": ["weil", "es", "draußen", "stark", "regnet"],
      "syntaxTokens": [
        {
          "surface": "Ich bleibe zu Hause",
          "roleCode": "V2",
          "ipa": "ɪç ˈblaɪbə tsu ˈhaʊzə",
          "gloss": {
            "en": "I stay at home",
            "it": "Resto a casa"
          }
        },
        {
          "surface": "weil es draußen",
          "roleCode": "CONN",
          "ipa": "vaɪl ɛs ˈdʁaʊsn̩",
          "gloss": {
            "en": "because outside it...",
            "it": "perché fuori..."
          }
        },
        {
          "surface": "stark regnet",
          "roleCode": "V-END",
          "ipa": "ʃtaʁk ˈʁeːɡnət",
          "gloss": {
            "en": "rains heavily (verb at the end)",
            "it": "piove forte (dopo 'weil' il verbo va in fondo)"
          }
        }
      ],
      "explanation": {
        "en": "After 'weil' (because) or 'dass' (that), push the conjugated verb to the very end of the sentence.",
        "it": "Dopo 'weil' (perché) o 'dass' (che), il verbo coniugato scivola sempre in fondo alla frase."
      }
    },
    {
      "id": "de_b1_u1",
      "cefr": "B1",
      "title": {
        "en": "Unit 1 · Expressing contrast with 'obwohl' & 'trotz'",
        "it": "Unità 1 · Esprimere contrasto con 'trotz' (nonostante)"
      },
      "promptSentence": "Trotz ___ starken Regens sind wir pünktlich angekommen.",
      "blankTarget": "des",
      "distractors": ["dem", "den", "der"],
      "scrambleTokens": ["Trotz", "des", "starken", "Regens", "sind", "wir", "angekommen"],
      "syntaxTokens": [
        {
          "surface": "Trotz des starken Regens",
          "roleCode": "CONN",
          "ipa": "tʁɔts dɛs ˈʃtaʁkn̩ ˈʁeːɡn̩s",
          "gloss": {
            "en": "Despite the heavy rain",
            "it": "Nonostante la forte pioggia"
          }
        },
        {
          "surface": "sind wir angekommen",
          "roleCode": "V2",
          "ipa": "zɪnt viːɐ̯ ˈanɡəkɔmən",
          "gloss": {
            "en": "we arrived",
            "it": "siamo arrivati"
          }
        }
      ],
      "explanation": {
        "en": "'Trotz' (despite) takes 'des' for masculine and neuter words: 'Trotz des Regens' (despite the rain).",
        "it": "Dopo 'Trotz' (nonostante) si usa 'des' con i nomi maschili e neutri: 'Trotz des Regens'."
      }
    },
    {
      "id": "de_b2_u1",
      "cefr": "B2",
      "title": {
        "en": "Unit 1 · Proportional 'The more..., the more...' (Je... desto)",
        "it": "Unità 1 · Costruzione 'Più..., più...' (Je... desto)"
      },
      "promptSentence": "Je mehr wir auf Deutsch sprechen, ___ einfacher wird es.",
      "blankTarget": "desto",
      "distractors": ["weil", "obwohl", "damit"],
      "scrambleTokens": ["Je", "mehr", "wir", "sprechen", "desto", "einfacher", "wird", "es"],
      "syntaxTokens": [
        {
          "surface": "Je mehr wir sprechen",
          "roleCode": "V-END",
          "ipa": "jeː meːɐ̯ viːɐ̯ ˈʃpʁɛçn̩",
          "gloss": {
            "en": "The more we speak",
            "it": "Più parliamo (verbo alla fine nella prima parte)"
          }
        },
        {
          "surface": "desto einfacher wird es",
          "roleCode": "V2",
          "ipa": "ˈdɛsto ˈaɪnfaxɐ vɪʁt ɛs",
          "gloss": {
            "en": "the easier it becomes",
            "it": "più facile diventa"
          }
        }
      ],
      "explanation": {
        "en": "Pair 'Je + comparative ... (verb at end)' with 'desto + comparative + verb'.",
        "it": "Usa la coppia 'Je ... (verbo in fondo), desto + comparativo + verbo'."
      }
    }
  ],
  "writingExercises": [
    {
      "id": "de_a1_w1",
      "cefr": "A1",
      "sourcePrompt": {
        "en": "Tomorrow I am traveling by train to Munich.",
        "it": "Domani vado in treno a Monaco."
      },
      "referenceTargets": ["Morgen fahre ich mit dem Zug nach München"],
      "requiredMorphemes": ["morgen", "fahre", "zug", "münchen"],
      "grammarRuleTitle": {
        "en": "Starting with a time word (Morgen fahre ich...)",
        "it": "Iniziare con una parola di tempo (Morgen fahre ich...)"
      },
      "jitFeedback": {
        "en": "Keep 'fahre' right after 'Morgen'.",
        "it": "Metti 'fahre' subito dopo 'Morgen'."
      }
    },
    {
      "id": "de_a2_w1",
      "cefr": "A2",
      "sourcePrompt": {
        "en": "Could you tell me when the museum opens?",
        "it": "Potrebbe dirmi quando apre il museo?"
      },
      "referenceTargets": ["Könnten Sie mir bitte sagen wann das Museum öffnet"],
      "requiredMorphemes": ["könnten", "wann", "museum", "öffnet"],
      "grammarRuleTitle": {
        "en": "Polite questions (wann ... öffnet)",
        "it": "Domande cortesi indirette (wann ... öffnet)"
      },
      "jitFeedback": {
        "en": "After 'wann', put 'öffnet' (opens) at the end of the sentence.",
        "it": "Dopo 'wann' (quando), metti il verbo 'öffnet' (apre) alla fine."
      }
    },
    {
      "id": "de_b1_w1",
      "cefr": "B1",
      "sourcePrompt": {
        "en": "Although the contract was signed yesterday, some details are missing.",
        "it": "Sebbene il contratto sia stato firmato ieri, mancano alcuni dettagli."
      },
      "referenceTargets": ["Obwohl der Vertrag gestern unterschrieben wurde fehlen einige Details"],
      "requiredMorphemes": ["obwohl", "wurde", "fehlen", "details"],
      "grammarRuleTitle": {
        "en": "Connecting clauses with 'Obwohl' (Although)",
        "it": "Collegare due frasi con 'Obwohl' (Sebbene)"
      },
      "jitFeedback": {
        "en": "End the first clause with 'wurde' and start the second immediately with 'fehlen'.",
        "it": "Chiudi la prima parte con 'wurde' e inizia subito la seconda con 'fehlen'."
      }
    },
    {
      "id": "de_b2_w1",
      "cefr": "B2",
      "sourcePrompt": {
        "en": "The more carefully we analyze the data, the more reliable the forecast becomes.",
        "it": "Più attentamente analizziamo i dati, più affidabile diventa la previsione."
      },
      "referenceTargets": ["Je sorgfältiger wir die Daten analysieren desto zuverlässiger wird die Prognose"],
      "requiredMorphemes": ["je", "analysieren", "desto", "wird"],
      "grammarRuleTitle": {
        "en": "Je ... desto proportional structure",
        "it": "Costruzione proporzionale Je ... desto"
      },
      "jitFeedback": {
        "en": "Use 'Je ... analysieren' followed by 'desto zuverlässiger wird ...'.",
        "it": "Usa 'Je ... analysieren' seguito da 'desto zuverlässiger wird ...'."
      }
    }
  ],
  "pronunciationDrills": [
    {
      "id": "de_a1_s1",
      "cefr": "A1",
      "targetSentence": "Guten Tag, ich möchte gern fünf grüne Bücher.",
      "furiganaOrReading": "Suono dolce di 'ch' in ich/möchte e vocali con Umlaut (ö, ü)",
      "fullIpa": "/ˈɡuːtn̩ taːk ɪç ˈmœçtə ɡɛʁn fʏnf ˈɡʁyːnə ˈbyːçɐ/",
      "translation": {
        "en": "Good day, I would like five green books.",
        "it": "Buongiorno, vorrei volentieri cinque libri verdi."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "For 'ü' in 'fünf', 'grüne', and 'Bücher', say 'i' while rounding your lips as if whistling.",
        "it": "Per pronunciare la 'ü' di 'fünf' e 'Bücher', pronuncia una 'i' tenendo però le labbra arrotondate come per dire 'u'."
      }
    },
    {
      "id": "de_a2_s1",
      "cefr": "A2",
      "targetSentence": "Morgen fahre ich mit dem Zug nach München.",
      "furiganaOrReading": "Differenza tra 'ch' dura (nach) e 'ch' dolce (München)",
      "fullIpa": "/ˈmɔʁɡn̩ ˈfaːʁə ɪç mɪt deːm tsuːk naːx ˈmʏnçn̩/",
      "translation": {
        "en": "Tomorrow I am traveling by train to Munich.",
        "it": "Domani vado in treno a Monaco."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Remember that German 'Z' in 'Zug' is always pronounced crisp like 'ts' (tsug).",
        "it": "Ricorda che la 'Z' tedesca in 'Zug' si legge sempre aspra come 'ts' (tsug)."
      }
    },
    {
      "id": "de_b1_s1",
      "cefr": "B1",
      "targetSentence": "Trotz des starken Regens sind wir pünktlich angekommen.",
      "furiganaOrReading": "Ritmo naturale e accento su 'pünktlich' e 'angekommen'",
      "fullIpa": "/tʁɔts dɛs ˈʃtaʁkn̩ ˈʁeːɡn̩s zɪnt viːɐ̯ ˈpʏŋktlɪç ˈanɡəkɔmən/",
      "translation": {
        "en": "Despite the heavy rain we arrived on time.",
        "it": "Nonostante la forte pioggia siamo arrivati puntuali."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Place clear emphasis on the first syllable of 'angekommen' (AN-gekommen).",
        "it": "Appoggia bene la voce sulla prima sillaba 'AN' di 'angekommen'."
      }
    },
    {
      "id": "de_b2_s1",
      "cefr": "B2",
      "targetSentence": "Je sorgfältiger wir die Daten analysieren, desto besser wird das Ergebnis.",
      "furiganaOrReading": "Fluidità tra proposizione principale e subordinata",
      "fullIpa": "/jeː ˈzɔʁkfɛltɪɡɐ viːɐ̯ diː ˈdaːtn̩ analyˈziːʁən ˈdɛsto ˈbɛsɐ vɪʁt das ɛɐ̯ˈɡeːpnɪs/",
      "translation": {
        "en": "The more carefully we analyze the data, the better the result becomes.",
        "it": "Più attentamente analizziamo i dati, migliore diventa il risultato."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Keep your voice slightly rising at 'analysieren' before dropping cleanly on 'Ergebnis'.",
        "it": "Mantieni l'intonazione leggermente sospesa su 'analysieren' per poi scendere su 'Ergebnis'."
      }
    }
  ],
  "scriptCards": [
    {
      "symbol": "ä / Ä",
      "scriptCategory": "Suoni Tedeschi",
      "readingOrFurigana": "A-Umlaut",
      "romajiOrIpa": "e aperta",
      "meaning": {
        "en": "Pronounced like an open 'e' (Mädchen, spät)",
        "it": "Si legge come una 'e' aperta italiana (Mädchen = ragazza, spät = tardi)"
      },
      "exampleWord": "spät",
      "exampleReading": "shpet (tardi)",
      "strokeCount": 3
    },
    {
      "symbol": "ö / Ö",
      "scriptCategory": "Suoni Tedeschi",
      "readingOrFurigana": "O-Umlaut",
      "romajiOrIpa": "oe arrotondata",
      "meaning": {
        "en": "Say 'e' with rounded lips (schön, möchte)",
        "it": "Pronuncia una 'e' tenendo le labbra arrotondate (schön = bello)"
      },
      "exampleWord": "schön",
      "exampleReading": "shœn (bello)",
      "strokeCount": 3
    },
    {
      "symbol": "ü / Ü",
      "scriptCategory": "Suoni Tedeschi",
      "readingOrFurigana": "U-Umlaut",
      "romajiOrIpa": "iu stretta",
      "meaning": {
        "en": "Say 'i' with rounded lips (fünf, Bücher)",
        "it": "Pronuncia una 'i' con le labbra chiuse a cerchio (fünf = cinque)"
      },
      "exampleWord": "fünf",
      "exampleReading": "fynf (cinque)",
      "strokeCount": 3
    },
    {
      "symbol": "ß",
      "scriptCategory": "Suoni Tedeschi",
      "readingOrFurigana": "Eszett",
      "romajiOrIpa": "ss sorda",
      "meaning": {
        "en": "Sharp 's' sound after long vowels (Straße, groß)",
        "it": "Doppia 's' sorda dopo una vocale lunga (Straße = strada, groß = grande)"
      },
      "exampleWord": "Straße",
      "exampleReading": "shtrasse (strada)",
      "strokeCount": 1
    }
  ]
}
""",

    "app/src/main/assets/packs/ja_pack.json": """\
{
  "languageCode": "ja",
  "languageName": {
    "en": "Japanese",
    "it": "Giapponese"
  },
  "availableVoices": [
    {
      "voiceId": "ja_JP-kokoro-medium",
      "displayName": "Kokoro (Tokyo)",
      "gender": "Femminile",
      "timbre": "Naturale e limpida",
      "onnxFileName": "ja_JP-kokoro-medium.onnx",
      "sampleRateHz": 22050
    },
    {
      "voiceId": "ja_JP-kenji-high",
      "displayName": "Kenji (Standard)",
      "gender": "Maschile",
      "timbre": "Calda e profonda",
      "onnxFileName": "ja_JP-kenji-high.onnx",
      "sampleRateHz": 22050
    }
  ],
  "grammarExercises": [
    {
      "id": "ja_a1_u1",
      "cefr": "A1",
      "title": {
        "en": "Unit 1 · Greetings & introducing yourself",
        "it": "Unità 1 · Salutare e presentarsi (わたしは...です)"
      },
      "promptSentence": "はじめまして。わたし ___ イタリア人です。",
      "blankTarget": "は",
      "distractors": ["を", "に", "で"],
      "scrambleTokens": ["わたし", "は", "イタリア人", "です"],
      "syntaxTokens": [
        {
          "surface": "はじめまして",
          "roleCode": "A1",
          "ipa": "hadʑimemaɕite",
          "gloss": {
            "en": "Nice to meet you (hajímemashite)",
            "it": "Piacere di conoscerti (hajimemashite)"
          }
        },
        {
          "surface": "わたしは",
          "roleCode": "TOPIC_PART",
          "ipa": "ɰataɕi ɰa",
          "gloss": {
            "en": "As for me (watashi wa)",
            "it": "Io / Quanto a me (watashi wa)"
          }
        },
        {
          "surface": "イタリア人です",
          "roleCode": "V-END",
          "ipa": "itaɾiadʑiɴ desɯ",
          "gloss": {
            "en": "am Italian (itariá-jin desu)",
            "it": "sono italiano (itaria-jin desu)"
          }
        }
      ],
      "explanation": {
        "en": "The particle は (written 'ha' but pronounced 'wa') marks the topic of the sentence ('As for me...').",
        "it": "La particella は (si scrive 'ha' ma si legge 'wa') indica il protagonista della frase ('Io...')."
      }
    },
    {
      "id": "ja_a1_u2",
      "cefr": "A1",
      "title": {
        "en": "Unit 2 · Daily actions & direct object (を)",
        "it": "Unità 2 · Azioni quotidiane e oggetto diretto (を)"
      },
      "promptSentence": "わたしは毎朝コーヒー ___ 飲みます。",
      "blankTarget": "を",
      "distractors": ["は", "に", "へ"],
      "scrambleTokens": ["わたしは", "毎朝", "コーヒー", "を", "飲みます"],
      "syntaxTokens": [
        {
          "surface": "毎朝 (まいあさ)",
          "roleCode": "CONN",
          "ipa": "maiasa",
          "gloss": {
            "en": "Every morning (mai-asa)",
            "it": "Ogni mattina (mai-asa)"
          }
        },
        {
          "surface": "コーヒーを",
          "roleCode": "OBJ_PART",
          "ipa": "koːçiː o",
          "gloss": {
            "en": "coffee (kōhī o)",
            "it": "il caffè (kōhī + particella oggetto を 'o')"
          }
        },
        {
          "surface": "飲みます (のみます)",
          "roleCode": "V-END",
          "ipa": "nomimasɯ",
          "gloss": {
            "en": "drink (nomimasu)",
            "it": "bevo (nomimasu - il verbo va sempre alla fine)"
          }
        }
      ],
      "explanation": {
        "en": "Put を (pronounced 'o') right after the thing you eat, drink, or read, and place the verb at the end.",
        "it": "Metti を (si legge 'o') subito dopo la cosa che bevi o mangi, e chiudi la frase col verbo (飲みます)."
      }
    },
    {
      "id": "ja_a2_u1",
      "cefr": "A2",
      "title": {
        "en": "Unit 1 · Receiving help & kindness (〜てくれました)",
        "it": "Unità 1 · Ringraziare per un favore ricevuto (〜てくれました)"
      },
      "promptSentence": "友だちが東京の地図を書いて ___。",
      "blankTarget": "くれました",
      "distractors": ["あげました", "もらいました", "いきました"],
      "scrambleTokens": ["友だちが", "地図を", "書いて", "くれました"],
      "syntaxTokens": [
        {
          "surface": "友だちが (ともだちが)",
          "roleCode": "SUBJ_PART",
          "ipa": "tomodatɕi ɡa",
          "gloss": {
            "en": "My friend (tomodachi ga)",
            "it": "Un amico (tomodachi ga)"
          }
        },
        {
          "surface": "書いて (かいて)",
          "roleCode": "VERB",
          "ipa": "kaite",
          "gloss": {
            "en": "wrote / drew (kaite)",
            "it": "ha disegnato / scritto (forma in -te)"
          }
        },
        {
          "surface": "くれました",
          "roleCode": "V-END",
          "ipa": "kɯɾemaɕita",
          "gloss": {
            "en": "did it for me (kuremashita)",
            "it": "per me (indica un favore fatto a te)"
          }
        }
      ],
      "explanation": {
        "en": "Adding くれました (kuremashita) to a verb in -te form shows gratitude that someone did it for your benefit.",
        "it": "Aggiungere くれました (kuremashita) dopo un verbo in -te indica che qualcuno ha fatto quell'azione per aiutarti."
      }
    },
    {
      "id": "ja_b1_u1",
      "cefr": "B1",
      "title": {
        "en": "Unit 1 · Reporting news ('According to...')",
        "it": "Unità 1 · Riportare una notizia (〜によると...そうです)"
      },
      "promptSentence": "天気予報によると、明日は雪が降る ___ です。",
      "blankTarget": "そう",
      "distractors": ["よう", "はず", "ため"],
      "scrambleTokens": ["天気予報によると", "明日は", "雪が降る", "そうです"],
      "syntaxTokens": [
        {
          "surface": "天気予報によると",
          "roleCode": "CONN",
          "ipa": "teŋki johoː ni joɾɯto",
          "gloss": {
            "en": "According to the weather forecast",
            "it": "Secondo le previsioni del tempo (tenki yohō ni yoruto)"
          }
        },
        {
          "surface": "雪が降るそうです",
          "roleCode": "V-END",
          "ipa": "jɯki ɡa ɸɯɾɯ soː desɯ",
          "gloss": {
            "en": "it is said it will snow (yuki ga furu sō desu)",
            "it": "pare che nevicherà (yuki ga furu sō desu)"
          }
        }
      ],
      "explanation": {
        "en": "Pair 〜によると ('according to') with plain verb + そうです ('I heard that...').",
        "it": "Abbina 〜によると ('secondo...') al verbo semplice seguito da そうです ('pare che / ho sentito che')."
      }
    },
    {
      "id": "ja_b2_u1",
      "cefr": "B2",
      "title": {
        "en": "Unit 1 · 'The more..., the more...' (〜ば〜ほど)",
        "it": "Unità 1 · 'Più..., più...' (〜ば〜ほど)"
      },
      "promptSentence": "日本語は勉強 ___ 勉強するほどおもしろくなります。",
      "blankTarget": "すれば",
      "distractors": ["したら", "すると", "しながら"],
      "scrambleTokens": ["日本語は", "勉強すれば", "勉強するほど", "おもしろくなります"],
      "syntaxTokens": [
        {
          "surface": "勉強すれば勉強するほど",
          "roleCode": "CONN",
          "ipa": "beŋkjoː sɯɾeba beŋkjoː sɯɾɯ hodo",
          "gloss": {
            "en": "The more you study (benkyō sureba benkyō suru hodo)",
            "it": "Più studi (benkyō sureba benkyō suru hodo)"
          }
        },
        {
          "surface": "おもしろくなります",
          "roleCode": "V-END",
          "ipa": "omoɕiɾokɯ naɾimasɯ",
          "gloss": {
            "en": "the more interesting it becomes",
            "it": "più diventa interessante (omoshiroku narimasu)"
          }
        }
      ],
      "explanation": {
        "en": "Repeat the verb in the conditional -eba form and dictionary form + ほど to express 'the more X, the more Y'.",
        "it": "Ripeti il verbo nella forma in -eba + forma base + ほど per dire 'più fai X, più succede Y'."
      }
    }
  ],
  "writingExercises": [
    {
      "id": "ja_a1_w1",
      "cefr": "A1",
      "sourcePrompt": {
        "en": "I go to Tokyo Station by subway every morning.",
        "it": "Ogni mattina vado alla stazione di Tokyo in metropolitana."
      },
      "referenceTargets": ["私は毎朝地下鉄で東京駅へ行きます"],
      "requiredMorphemes": ["毎朝", "地下鉄で", "東京駅", "行きます"],
      "grammarRuleTitle": {
        "en": "Transport (で) and destination (へ / に)",
        "it": "Mezzo di trasporto (で) e destinazione (へ / に)"
      },
      "jitFeedback": {
        "en": "Use で after 地下鉄 (subway) and へ after 東京駅 (Tokyo Station).",
        "it": "Usa で dopo 地下鉄 (metro) e へ dopo 東京駅 (Stazione di Tokyo)."
      }
    },
    {
      "id": "ja_a2_w1",
      "cefr": "A2",
      "sourcePrompt": {
        "en": "Because the train was delayed, I was late for the appointment.",
        "it": "Poiché il treno era in ritardo, non sono arrivato in tempo all'appuntamento."
      },
      "referenceTargets": ["電車が遅れたので約束に間に合いませんでした"],
      "requiredMorphemes": ["電車が", "遅れたので", "約束に", "間に合いませんでした"],
      "grammarRuleTitle": {
        "en": "Polite reason with ので (because)",
        "it": "Spiegare una causa in modo cortese con ので"
      },
      "jitFeedback": {
        "en": "Attach ので after 遅れた (was delayed).",
        "it": "Collega ので (poiché) subito dopo 遅れた (ha tardato)."
      }
    },
    {
      "id": "ja_b1_w1",
      "cefr": "B1",
      "sourcePrompt": {
        "en": "According to the weather forecast, it will snow tomorrow night.",
        "it": "Secondo le previsioni meteo, domani sera nevicherà."
      },
      "referenceTargets": ["天気予報によると明日の夜は雪が降るそうです"],
      "requiredMorphemes": ["天気予報によると", "明日の夜", "雪が降る", "そうです"],
      "grammarRuleTitle": {
        "en": "〜によると ... そうです",
        "it": "Costruzione 〜によると ... そうです"
      },
      "jitFeedback": {
        "en": "End with 雪が降るそうです.",
        "it": "Chiudi la frase con 雪が降るそうです."
      }
    },
    {
      "id": "ja_b2_w1",
      "cefr": "B2",
      "sourcePrompt": {
        "en": "Regardless of experience, we welcome motivated applicants.",
        "it": "Indipendentemente dall'esperienza, accogliamo candidati motivati."
      },
      "referenceTargets": ["経験の有無にかかわらず意欲のある応募者を歓迎します"],
      "requiredMorphemes": ["経験", "にかかわらず", "意欲のある", "歓迎します"],
      "grammarRuleTitle": {
        "en": "Formal 〜にかかわらず (regardless of)",
        "it": "Espressione formale 〜にかかわらず (a prescindere da)"
      },
      "jitFeedback": {
        "en": "Use 経験の有無にかかわらず at the start of the clause.",
        "it": "Inizia con 経験の有無にかかわらず (indipendentemente dall'avere esperienza)."
      }
    }
  ],
  "pronunciationDrills": [
    {
      "id": "ja_a1_s1",
      "cefr": "A1",
      "targetSentence": "はじめまして、わたしは毎朝コーヒーを飲みます。",
      "furiganaOrReading": "Hajimemashite, watashi wa maiasa kōhī o nomimasu",
      "fullIpa": "/hadʑimemaɕite ɰataɕi ɰa maiasa koːçiː o nomimasɯ/",
      "translation": {
        "en": "Nice to meet you, I drink coffee every morning.",
        "it": "Piacere di conoscerti, io bevo il caffè ogni mattina."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "In 'mashite' and 'nomimasu', the final 'u' is almost whispered.",
        "it": "In 'mashite' e 'nomimasu', la 'u' finale di '-masu' è leggerissima, quasi sussurrata."
      }
    },
    {
      "id": "ja_a2_s1",
      "cefr": "A2",
      "targetSentence": "来週の金曜日に北海道へ出張に行きます。",
      "furiganaOrReading": "Raishū no kin'yōbi ni Hokkaidō e shutchō ni ikimasu",
      "fullIpa": "/ɾaiɕɯː no kiɰ̃joːbi ni hokkaidoː e ɕɯttɕoː ni ikimasɯ/",
      "translation": {
        "en": "Next Friday I am going on a business trip to Hokkaido.",
        "it": "Venerdì prossimo andrò in viaggio di lavoro in Hokkaido."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Make a tiny pause on the double consonant in 'Hokkaidō' (ho-k-kaidō) and 'shutchō' (shu-t-chō).",
        "it": "Fai una piccola tenuta sulla doppia consonante (っ) in 'Hokkaidō' e 'shutchō'."
      }
    },
    {
      "id": "ja_b1_s1",
      "cefr": "B1",
      "targetSentence": "雨が降っているにもかかわらず、大勢の人が集まった。",
      "furiganaOrReading": "Ame ga futte iru nimo kakawarazu, ōzei no hito ga atsumatta",
      "fullIpa": "/ame ɡa ɸɯtte iɾɯ nimo kakawaɾazɯ oːzeː no çito ɡa atsɯmatta/",
      "translation": {
        "en": "Despite the rain, a large crowd of people gathered.",
        "it": "Nonostante piovesse, si sono radunate moltissime persone."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Start 'Ame' (rain) with a higher pitch on 'A-' and drop on '-me'.",
        "it": "Pronuncia 'Ame' (pioggia) partendo più alto sulla 'A-' e scendendo su '-me'."
      }
    },
    {
      "id": "ja_b2_s1",
      "cefr": "B2",
      "targetSentence": "日本語は勉強すれば勉強するほどおもしろくなります。",
      "furiganaOrReading": "Nihongo wa benkyō sureba benkyō suru hodo omoshiroku narimasu",
      "fullIpa": "/ɲihoŋɡo ɰa beŋkjoː sɯɾeba beŋkjoː sɯɾɯ hodo omoɕiɾokɯ naɾimasɯ/",
      "translation": {
        "en": "The more you study Japanese, the more interesting it becomes.",
        "it": "Più studi il giapponese, più diventa interessante."
      },
      "criticalPhonemes": [],
      "articulatoryTip": {
        "en": "Keep an even, steady beat on every syllable without rushing 'benkyō sureba'.",
        "it": "Mantieni un ritmo regolare su ogni sillaba e allunga bene la 'ō' di 'benkyō'."
      }
    }
  ],
  "scriptCards": [
    {
      "symbol": "あ",
      "scriptCategory": "Hiragana",
      "readingOrFurigana": "あ",
      "romajiOrIpa": "a",
      "meaning": {
        "en": "Vowel 'a' (first character of Hiragana)",
        "it": "Vocale 'a' (primo carattere dell'alfabeto Hiragana)"
      },
      "exampleWord": "あさ (朝)",
      "exampleReading": "asa — mattina",
      "strokeCount": 3
    },
    {
      "symbol": "い",
      "scriptCategory": "Hiragana",
      "readingOrFurigana": "い",
      "romajiOrIpa": "i",
      "meaning": {
        "en": "Vowel 'i'",
        "it": "Vocale 'i'"
      },
      "exampleWord": "いま (今)",
      "exampleReading": "ima — adesso",
      "strokeCount": 2
    },
    {
      "symbol": "う",
      "scriptCategory": "Hiragana",
      "readingOrFurigana": "う",
      "romajiOrIpa": "u",
      "meaning": {
        "en": "Vowel 'u'",
        "it": "Vocale 'u'"
      },
      "exampleWord": "うみ (海)",
      "exampleReading": "umi — mare",
      "strokeCount": 2
    },
    {
      "symbol": "え",
      "scriptCategory": "Hiragana",
      "readingOrFurigana": "え",
      "romajiOrIpa": "e",
      "meaning": {
        "en": "Vowel 'e'",
        "it": "Vocale 'e'"
      },
      "exampleWord": "えき (駅)",
      "exampleReading": "eki — stazione",
      "strokeCount": 2
    },
    {
      "symbol": "お",
      "scriptCategory": "Hiragana",
      "readingOrFurigana": "お",
      "romajiOrIpa": "o",
      "meaning": {
        "en": "Vowel 'o'",
        "it": "Vocale 'o'"
      },
      "exampleWord": "おちゃ (お茶)",
      "exampleReading": "ocha — tè verde",
      "strokeCount": 3
    },
    {
      "symbol": "か",
      "scriptCategory": "Hiragana",
      "readingOrFurigana": "か",
      "romajiOrIpa": "ka",
      "meaning": {
        "en": "Syllable 'ka'",
        "it": "Sillaba 'ka'"
      },
      "exampleWord": "かさ (傘)",
      "exampleReading": "kasa — ombrello",
      "strokeCount": 3
    },
    {
      "symbol": "き",
      "scriptCategory": "Hiragana",
      "readingOrFurigana": "き",
      "romajiOrIpa": "ki",
      "meaning": {
        "en": "Syllable 'ki'",
        "it": "Sillaba 'ki'"
      },
      "exampleWord": "きぼう (希望)",
      "exampleReading": "kibō — speranza",
      "strokeCount": 4
    },
    {
      "symbol": "ア",
      "scriptCategory": "Katakana",
      "readingOrFurigana": "ア",
      "romajiOrIpa": "a",
      "meaning": {
        "en": "Katakana 'a' (used for foreign words)",
        "it": "Katakana 'a' (usato per le parole straniere)"
      },
      "exampleWord": "アメリカ",
      "exampleReading": "Amerika — America",
      "strokeCount": 2
    },
    {
      "symbol": "コ",
      "scriptCategory": "Katakana",
      "readingOrFurigana": "コ",
      "romajiOrIpa": "ko",
      "meaning": {
        "en": "Katakana 'ko'",
        "it": "Katakana 'ko'"
      },
      "exampleWord": "コーヒー",
      "exampleReading": "kōhī — caffè",
      "strokeCount": 2
    },
    {
      "symbol": "シ",
      "scriptCategory": "Katakana",
      "readingOrFurigana": "シ",
      "romajiOrIpa": "shi",
      "meaning": {
        "en": "Katakana 'shi'",
        "it": "Katakana 'shi'"
      },
      "exampleWord": "システム",
      "exampleReading": "shisutemu — sistema",
      "strokeCount": 3
    },
    {
      "symbol": "日",
      "scriptCategory": "Kanji N5-N2",
      "readingOrFurigana": "にち / ひ",
      "romajiOrIpa": "NICHI / hi",
      "meaning": {
        "en": "Sun, day, Japan (JLPT N5)",
        "it": "Sole, giorno, Giappone (JLPT N5)"
      },
      "exampleWord": "日本",
      "exampleReading": "にほん (Nihon — Giappone)",
      "strokeCount": 4
    },
    {
      "symbol": "語",
      "scriptCategory": "Kanji N5-N2",
      "readingOrFurigana": "ご / かた(る)",
      "romajiOrIpa": "GO",
      "meaning": {
        "en": "Language, word (JLPT N5)",
        "it": "Lingua, parola (JLPT N5)"
      },
      "exampleWord": "日本語",
      "exampleReading": "にほんご (Nihongo — lingua giapponese)",
      "strokeCount": 14
    },
    {
      "symbol": "駅",
      "scriptCategory": "Kanji N5-N2",
      "readingOrFurigana": "えき",
      "romajiOrIpa": "EKI",
      "meaning": {
        "en": "Train station (JLPT N4)",
        "it": "Stazione ferroviaria (JLPT N4)"
      },
      "exampleWord": "東京駅",
      "exampleReading": "とうきょうえき (Tōkyō-eki — Stazione di Tokyo)",
      "strokeCount": 14
    },
    {
      "symbol": "験",
      "scriptCategory": "Kanji N5-N2",
      "readingOrFurigana": "けん",
      "romajiOrIpa": "KEN",
      "meaning": {
        "en": "Experience, test (JLPT N3)",
        "it": "Esperienza, esame (JLPT N3)"
      },
      "exampleWord": "経験",
      "exampleReading": "けいけん (keiken — esperienza)",
      "strokeCount": 18
    }
  ]
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
        print("Esegui questo script nella cartella del progetto VocalFox.")
        return

    print(f"[VocalFox v2 Fix] Aggiornamento in corso su:\n  {root}\n")

    for rel_path, content in FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  + Aggiornato: {rel_path}")

    drawable_dir = root / "app/src/main/res/drawable-nodpi"
    drawable_dir.mkdir(parents=True, exist_ok=True)

    for asset_name in [
        "splash_screen.webp",
        "logo.png",
        "mascot_idle.png",
        "mascot_celebrate.png",
        "mascot_thinking.png",
        "mascot_strict.png",
        "mascot_sad.png",
        "mascot_sleeping.png",
    ]:
        src_candidate = root / asset_name
        dst_candidate = drawable_dir / asset_name
        if src_candidate.exists() and src_candidate.resolve() != dst_candidate.resolve():
            shutil.copy2(src_candidate, dst_candidate)
            print(f"  + Copiato asset: {asset_name} -> app/src/main/res/drawable-nodpi/{asset_name}")

    print("\n========================================================")
    print("FIX COMPILAZIONE + DATASET ESPANSO APPLICATI!")
    print("Ora esegui questi comandi per fare il push su GitHub:")
    print("========================================================\n")
    print(f'cd "{root}"')
    print("git add .")
    print('git commit -m "Fix AppStrings unresolved references and expand A1-B2 language packs"')
    print("git push origin main")


if __name__ == "__main__":
    main()