package com.vocalfox.app.ui.screens

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
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.GrammarSyntaxExercise
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.SyntaxToken
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.MascotPedagogicalBanner
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxTokens
import com.vocalfox.app.ui.theme.VocalFoxType

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun GrammarSyntaxScreen(
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    strings: UiStrings,
    onSelectCefr: (CefrLevel) -> Unit,
    onSpeakSentence: (String) -> Unit,
    onExerciseVerified: (GrammarSyntaxExercise, Boolean) -> Unit
) {
    val colors = VocalFoxTheme.colors
    val exercise = currentPack.grammarExercises.firstOrNull { it.cefr == selectedCefr }
        ?: currentPack.grammarExercises.first()

    var selectedOption by remember(exercise.id) { mutableStateOf<String?>(null) }
    var inspectedToken by remember(exercise.id) { mutableStateOf<SyntaxToken?>(exercise.syntaxTokens.firstOrNull()) }
    var isVerified by remember(exercise.id) { mutableStateOf(false) }
    var isCorrect by remember(exercise.id) { mutableStateOf(false) }

    val scrambledChoiceOrder = remember(exercise.id) { mutableStateListOf<String>() }
    val allOptions = remember(exercise.id) {
        (listOf(exercise.blankTarget) + exercise.distractors).shuffled()
    }

    LaunchedEffect(exercise.id) {
        scrambledChoiceOrder.clear()
    }

    val mascotState = when {
        !isVerified -> MascotState.THINKING
        isCorrect -> MascotState.CELEBRATE
        else -> MascotState.STRICT_COACH
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = strings.syntaxStudioHeader,
                    style = VocalFoxType.PageTitle,
                    color = colors.primaryText
                )
                Text(
                    text = exercise.title.get(systemLang),
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.secondaryText
                )
            }

            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                CefrLevel.entries.forEach { level ->
                    val active = level == selectedCefr
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                            .background(if (active) colors.accent else colors.raised)
                            .clickable { onSelectCefr(level) }
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = level.name,
                            style = VocalFoxType.MetaMono,
                            color = if (active) colors.onAccent else colors.secondaryText
                        )
                    }
                }
            }
        }

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = strings.syntaxLegendTitle,
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.mutedText
                )
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                        .background(colors.raised)
                        .clickable {
                            onSpeakSentence(
                                exercise.promptSentence.replace("___", exercise.blankTarget)
                            )
                        }
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.VolumeUp,
                        contentDescription = null,
                        tint = colors.secondaryText,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = "Piper TTS",
                        style = VocalFoxType.MetaMono,
                        color = colors.secondaryText
                    )
                }
            }

            FlowRow(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                exercise.syntaxTokens.forEach { token ->
                    val roleColor = syntaxColorForRole(token.roleCode)
                    val isSelectedToken = inspectedToken == token
                    Column(
                        modifier = Modifier
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                            .background(if (isSelectedToken) colors.raised else Color.Transparent)
                            .clickable { inspectedToken = token }
                            .padding(horizontal = 8.dp, vertical = 6.dp),
                        horizontalAlignment = Alignment.Start
                    ) {
                        Text(
                            text = token.surface,
                            style = VocalFoxType.SentenceDisplay,
                            color = colors.primaryText
                        )
                        Box(
                            modifier = Modifier
                                .padding(top = 4.dp, bottom = 4.dp)
                                .height(3.dp)
                                .width((token.surface.length * 10).coerceAtLeast(28).dp)
                                .background(roleColor)
                        )
                        Text(
                            text = "${token.roleCode} · /${token.ipa}/",
                            style = VocalFoxType.MetaMono,
                            color = roleColor
                        )
                    }
                }
            }

            if (inspectedToken != null) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .background(colors.raised)
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "${inspectedToken!!.surface} (${inspectedToken!!.roleCode})",
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                    Text(
                        text = inspectedToken!!.gloss.get(systemLang),
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }
            }
        }

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = strings.reorderInstruction,
                style = VocalFoxType.SecondaryCaption,
                color = colors.secondaryText
            )

            Text(
                text = exercise.promptSentence.replace("___", selectedOption ?: " [ ___ ] "),
                style = VocalFoxType.SentenceDisplay,
                color = colors.primaryText
            )

            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                allOptions.forEach { option ->
                    val isPicked = selectedOption == option
                    val borderColor = when {
                        isVerified && option == exercise.blankTarget -> colors.positive
                        isVerified && isPicked && !isCorrect -> colors.negative
                        isPicked -> colors.accent
                        else -> colors.hairline
                    }
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                            .background(if (isPicked) colors.raised else colors.background)
                            .border(1.dp, borderColor, RoundedCornerShape(VocalFoxTokens.RadiusControl))
                            .clickable {
                                selectedOption = option
                                isVerified = false
                            }
                            .padding(horizontal = 16.dp, vertical = 10.dp)
                    ) {
                        Text(
                            text = option,
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                    }
                }
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                    .background(colors.accent)
                    .clickable {
                        if (selectedOption != null) {
                            isVerified = true
                            isCorrect = (selectedOption == exercise.blankTarget)
                            onExerciseVerified(exercise, isCorrect)
                        }
                    }
                    .padding(vertical = 12.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = strings.checkAnswerAction,
                    style = VocalFoxType.BodyMedium,
                    color = colors.onAccent
                )
            }
        }

        MascotPedagogicalBanner(
            state = mascotState,
            title = strings.grammarNoteLabel,
            subtitle = exercise.explanation.get(systemLang),
            metaBadge = exercise.cefr.name
        )

        Spacer(modifier = Modifier.height(16.dp))
    }
}

private fun syntaxColorForRole(roleCode: String): Color {
    return when {
        roleCode.contains("V2") || roleCode.contains("VERB") -> VocalFoxPalette.SyntaxVerbV2
        roleCode.contains("END") || roleCode.contains("SUBORD") -> VocalFoxPalette.SyntaxSubordinateVerb
        roleCode.contains("SUBJ") && roleCode.contains("MOD") -> VocalFoxPalette.SyntaxSubjunctive
        roleCode.contains("PART") -> VocalFoxPalette.SyntaxParticle
        roleCode.contains("SUBJ") || roleCode.contains("TOPIC") -> VocalFoxPalette.SyntaxSubject
        else -> VocalFoxPalette.SyntaxObject
    }
}
