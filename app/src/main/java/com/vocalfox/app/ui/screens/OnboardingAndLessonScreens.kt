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
