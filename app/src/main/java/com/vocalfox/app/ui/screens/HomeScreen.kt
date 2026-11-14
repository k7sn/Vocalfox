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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.HistoryEdu
import androidx.compose.material.icons.outlined.Schedule
import androidx.compose.material.icons.outlined.Schema
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.vocalfox.app.data.local.MistakeSrsEntity
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxTokens
import com.vocalfox.app.ui.theme.VocalFoxType

@Composable
fun HomeScreen(
    allPacks: Map<String, LanguagePack>,
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    strings: UiStrings,
    progressList: List<UserProgressEntity>,
    srsList: List<MistakeSrsEntity>,
    onSelectLanguage: (String) -> Unit,
    onSelectCefr: (CefrLevel) -> Unit,
    onNavigateToPillar: (String) -> Unit
) {
    val colors = VocalFoxTheme.colors
    val completedInLevel = progressList.count { it.cefrLevel == selectedCefr.name && it.bestScore >= 70 }
    val dueSrsCount = srsList.size

    val mascotState = when {
        dueSrsCount > 4 -> MascotState.STRICT_COACH
        completedInLevel >= 3 -> MascotState.CELEBRATE
        else -> MascotState.LOGO_IDLE
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        item {
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    VocalFoxMascot(
                        state = MascotState.LOGO_IDLE,
                        size = 40.dp,
                        useLogoEmblem = true
                    )
                    Column {
                        Text(
                            text = "VocalFox",
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                        Text(
                            text = "${currentPack.languageName.get(systemLang)} · ${selectedCefr.name}",
                            style = VocalFoxType.MetaMono,
                            color = colors.mutedText
                        )
                    }
                }

                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(colors.raised)
                        .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                        .padding(4.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    allPacks.keys.forEach { langCode ->
                        val isSelected = langCode == currentPack.languageCode
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                                .background(if (isSelected) colors.card else colors.raised)
                                .clickable { onSelectLanguage(langCode) }
                                .padding(horizontal = 12.dp, vertical = 6.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = langCode.uppercase(),
                                style = VocalFoxType.MetaMono,
                                color = if (isSelected) colors.accent else colors.secondaryText
                            )
                        }
                    }
                }
            }
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CefrLevel.entries.forEach { level ->
                    val isSelected = level == selectedCefr
                    val levelDesc = when (level) {
                        CefrLevel.A1 -> if (systemLang == SystemLang.IT) "Base" else "Foundation"
                        CefrLevel.A2 -> if (systemLang == SystemLang.IT) "Elementare" else "Waystage"
                        CefrLevel.B1 -> if (systemLang == SystemLang.IT) "Intermedio" else "Threshold"
                        CefrLevel.B2 -> if (systemLang == SystemLang.IT) "Avanzato" else "Vantage"
                    }
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isSelected) colors.card else colors.raised)
                            .border(
                                width = 1.dp,
                                color = if (isSelected) colors.accent else colors.hairline,
                                shape = RoundedCornerShape(12.dp)
                            )
                            .clickable { onSelectCefr(level) }
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Text(
                            text = level.name,
                            style = VocalFoxType.BodyMedium,
                            color = if (isSelected) colors.accent else colors.primaryText
                        )
                        Text(
                            text = levelDesc,
                            style = VocalFoxType.MetaMono,
                            color = colors.mutedText
                        )
                    }
                }
            }
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                StatMetricCard(
                    label = strings.streakDaysLabel,
                    figure = "14d",
                    comparison = strings.vsLastWeek,
                    modifier = Modifier.weight(1f)
                )
                StatMetricCard(
                    label = strings.masteredUnitsLabel,
                    figure = "${progressList.size}",
                    comparison = "${selectedCefr.name} ($completedInLevel/3)",
                    modifier = Modifier.weight(1f)
                )
                StatMetricCard(
                    label = strings.dueReviewsLabel,
                    figure = "$dueSrsCount",
                    comparison = "SM-2 queue",
                    modifier = Modifier.weight(1f)
                )
            }
        }

        item {
            val syntaxEx = currentPack.grammarExercises.firstOrNull { it.cefr == selectedCefr }
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                    .padding(20.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                VocalFoxMascot(state = mascotState, size = 72.dp)

                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = syntaxEx?.title?.get(systemLang) ?: strings.pathHeader,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Text(
                        text = syntaxEx?.explanation?.get(systemLang).orEmpty(),
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText,
                        maxLines = 2
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                            .background(colors.accent)
                            .clickable { onNavigateToPillar("SYNTAX") }
                            .padding(horizontal = 16.dp, vertical = 10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = strings.resumeStudyAction,
                            style = VocalFoxType.BodyMedium,
                            color = colors.onAccent
                        )
                        Icon(
                            imageVector = Icons.Outlined.ArrowForward,
                            contentDescription = null,
                            tint = colors.onAccent,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }
        }

        item {
            val syntaxEx = currentPack.grammarExercises.firstOrNull { it.cefr == selectedCefr }
            val writingEx = currentPack.writingExercises.firstOrNull { it.cefr == selectedCefr }
            val speechEx = currentPack.pronunciationDrills.firstOrNull { it.cefr == selectedCefr }

            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                PillarLessonRow(
                    icon = Icons.Outlined.Schema,
                    pillarCode = "${selectedCefr.name} · 01",
                    title = strings.syntaxStudioHeader,
                    subtitle = syntaxEx?.title?.get(systemLang).orEmpty(),
                    isCompleted = progressList.any { it.itemKey == syntaxEx?.id && it.bestScore >= 75 },
                    onClick = { onNavigateToPillar("SYNTAX") }
                )
                PillarLessonRow(
                    icon = Icons.Outlined.HistoryEdu,
                    pillarCode = "${selectedCefr.name} · 02",
                    title = strings.writingStudioHeader,
                    subtitle = writingEx?.grammarRuleTitle?.get(systemLang).orEmpty(),
                    isCompleted = progressList.any { it.itemKey == writingEx?.id && it.bestScore >= 75 },
                    onClick = { onNavigateToPillar("WRITING") }
                )
                PillarLessonRow(
                    icon = Icons.Outlined.GraphicEq,
                    pillarCode = "${selectedCefr.name} · 03",
                    title = strings.pronunciationHeader,
                    subtitle = speechEx?.targetSentence.orEmpty(),
                    isCompleted = progressList.any { it.itemKey == speechEx?.id && it.bestScore >= 75 },
                    onClick = { onNavigateToPillar("SPEECH") }
                )
            }
        }

        if (srsList.isNotEmpty()) {
            item {
                Text(
                    text = strings.dueReviewsLabel,
                    style = VocalFoxType.BodyMedium,
                    color = colors.primaryText
                )
            }
            items(srsList.take(4)) { srs ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Schedule,
                        contentDescription = null,
                        tint = colors.mutedText,
                        modifier = Modifier.size(18.dp)
                    )
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = srs.promptPreview,
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                        Text(
                            text = srs.lastMistakeNote,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText,
                            maxLines = 1
                        )
                    }
                    Text(
                        text = "EF ${"%.1f".format(srs.easeFactor)} · ${srs.intervalDays}d",
                        style = VocalFoxType.MetaMono,
                        color = colors.accent
                    )
                }
            }
        }

        item { Spacer(modifier = Modifier.height(24.dp)) }
    }
}

@Composable
private fun StatMetricCard(
    label: String,
    figure: String,
    comparison: String,
    modifier: Modifier = Modifier
) {
    val colors = VocalFoxTheme.colors
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(colors.card)
            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Text(
            text = label,
            style = VocalFoxType.SecondaryCaption,
            color = colors.secondaryText,
            maxLines = 1
        )
        Text(
            text = figure,
            style = VocalFoxType.CardFigure,
            color = colors.primaryText
        )
        Text(
            text = comparison,
            style = VocalFoxType.MetaMono,
            color = colors.mutedText,
            maxLines = 1
        )
    }
}

@Composable
private fun PillarLessonRow(
    icon: ImageVector,
    pillarCode: String,
    title: String,
    subtitle: String,
    isCompleted: Boolean,
    onClick: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(colors.card)
            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = colors.secondaryText,
            modifier = Modifier.size(18.dp)
        )
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    style = VocalFoxType.BodyMedium,
                    color = colors.primaryText
                )
                Text(
                    text = pillarCode,
                    style = VocalFoxType.MetaMono,
                    color = colors.mutedText
                )
            }
            Text(
                text = subtitle,
                style = VocalFoxType.SecondaryCaption,
                color = colors.secondaryText,
                maxLines = 1
            )
        }
        Icon(
            imageVector = if (isCompleted) Icons.Outlined.CheckCircle else Icons.Outlined.ArrowForward,
            contentDescription = null,
            tint = if (isCompleted) colors.positive else colors.mutedText,
            modifier = Modifier.size(18.dp)
        )
    }
}
