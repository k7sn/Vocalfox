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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.unit.dp
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.WritingExercise
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.MascotPedagogicalBanner
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxTokens
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.viewmodel.WritingEvaluationFeedback

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun WritingExerciseScreen(
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    strings: UiStrings,
    onSelectCefr: (CefrLevel) -> Unit,
    onEvaluateWriting: (WritingExercise, String) -> WritingEvaluationFeedback
) {
    val colors = VocalFoxTheme.colors
    val exercise = currentPack.writingExercises.firstOrNull { it.cefr == selectedCefr }
        ?: currentPack.writingExercises.first()

    var userInput by remember(exercise.id) { mutableStateOf("") }
    var feedback by remember(exercise.id) { mutableStateOf<WritingEvaluationFeedback?>(null) }

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
                    text = strings.writingStudioHeader,
                    style = VocalFoxType.PageTitle,
                    color = colors.primaryText
                )
                Text(
                    text = exercise.grammarRuleTitle.get(systemLang),
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
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = strings.writingPromptLabel,
                style = VocalFoxType.SecondaryCaption,
                color = colors.mutedText
            )
            Text(
                text = exercise.sourcePrompt.get(systemLang),
                style = VocalFoxType.SentenceDisplay,
                color = colors.primaryText
            )

            Text(
                text = strings.expectedChecklistLabel,
                style = VocalFoxType.MetaMono,
                color = colors.mutedText
            )
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                exercise.requiredMorphemes.forEach { morpheme ->
                    val isMatched = feedback?.matchedMorphemes?.contains(morpheme) == true
                    val chipColor = when {
                        feedback == null -> colors.raised
                        isMatched -> colors.positive.copy(alpha = 0.16f)
                        else -> colors.negative.copy(alpha = 0.16f)
                    }
                    val textColor = when {
                        feedback == null -> colors.secondaryText
                        isMatched -> colors.positive
                        else -> colors.negative
                    }
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                            .background(chipColor)
                            .clickable {
                                userInput = if (userInput.isBlank()) morpheme else "$userInput $morpheme"
                            }
                            .padding(horizontal = 10.dp, vertical = 6.dp)
                    ) {
                        Text(
                            text = morpheme,
                            style = VocalFoxType.MetaMono,
                            color = textColor
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
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(112.dp)
                    .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                    .background(colors.raised)
                    .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusControl))
                    .padding(12.dp)
            ) {
                if (userInput.isEmpty()) {
                    Text(
                        text = strings.writingInputHint,
                        style = VocalFoxType.Body,
                        color = colors.mutedText
                    )
                }
                BasicTextField(
                    value = userInput,
                    onValueChange = { userInput = it },
                    textStyle = VocalFoxType.Body.copy(color = colors.primaryText),
                    cursorBrush = SolidColor(colors.accent),
                    modifier = Modifier.fillMaxSize()
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .background(colors.accent)
                        .clickable {
                            feedback = onEvaluateWriting(exercise, userInput)
                        }
                        .padding(vertical = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = strings.evaluateWritingAction,
                        style = VocalFoxType.BodyMedium,
                        color = colors.onAccent
                    )
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .background(colors.raised)
                        .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .clickable {
                            userInput = exercise.referenceTargets.firstOrNull().orEmpty()
                        }
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (systemLang == SystemLang.IT) "Modello" else "Model",
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                }
            }
        }

        val currentFeedback = feedback
        if (currentFeedback != null) {
            MascotPedagogicalBanner(
                state = currentFeedback.mascotState,
                title = "${exercise.grammarRuleTitle.get(systemLang)} · ${currentFeedback.score}%",
                subtitle = "${currentFeedback.explanation}\n→ ${exercise.referenceTargets.firstOrNull().orEmpty()}",
                metaBadge = exercise.cefr.name
            )
        } else {
            MascotPedagogicalBanner(
                state = MascotState.THINKING,
                title = exercise.grammarRuleTitle.get(systemLang),
                subtitle = exercise.jitFeedback.get(systemLang),
                metaBadge = exercise.cefr.name
            )
        }

        Spacer(modifier = Modifier.height(16.dp))
    }
}
