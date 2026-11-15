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
import androidx.compose.ui.platform.LocalContext
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
    val colors = VocalFoxTheme.colors
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
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
    val colors = VocalFoxTheme.colors
    var inPlacementMode by remember { mutableStateOf(false) }
    var questionIdx by remember { mutableIntStateOf(0) }
    var correctCount by remember { mutableIntStateOf(0) }

    val pack = allPacks[selectedLangCode] ?: allPacks.values.first()
    val placementQuestions = remember(pack.languageCode) {
        CefrLevel.entries.mapNotNull { lvl ->
            pack.grammarExercises.firstOrNull { it.cefr == lvl }
        }
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
                // STEP 0: Vocabulary & Concept Discovery
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

                // STEP 1: Multiple-Choice Quiz (Zero TTS Spoiler)
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

                // STEP 2: Meaning & Inflection Comprehension Check
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

                // STEP 3: FIX 2 — Interactive Sentence Builder with Per-Word Green/Red Outline
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

                        // Assembled Sentence Area: Green outline for right word in right slot, Red for wrong slot
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

                        // Shuffled Word Bank
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

                // STEP 4: Final Pronunciation & Shadowing
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

                // STEP 5: Celebratory Completion Screen + Direct Handoff to Google Gemini App
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

                        // Pulsante per continuare a praticare l'argomento della lezione nell'app Google Gemini
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
