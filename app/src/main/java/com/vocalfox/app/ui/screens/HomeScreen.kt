package com.vocalfox.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.LocalFireDepartment
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.data.repository.CurriculumGenerator
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.theme.VocalFoxWordmark

@Composable
fun HomeScreen(
    allPacks: Map<String, LanguagePack>,
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    strings: UiStrings,
    progressList: List<UserProgressEntity>,
    onSelectLanguage: (String) -> Unit,
    onSelectCefr: (CefrLevel) -> Unit,
    onStartGuidedUnit: (GuidedUnitBundle) -> Unit,
    onOpenProfileSettings: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    val all50Units = remember(currentPack.languageCode, selectedCefr, systemLang) {
        CurriculumGenerator.generate50UnitsForLevel(currentPack, selectedCefr, systemLang)
    }

    var selectedChapterFilter by remember(selectedCefr) { mutableIntStateOf(0) }
    val displayedUnits = remember(all50Units, selectedChapterFilter) {
        if (selectedChapterFilter == 0) {
            all50Units
        } else {
            val startIdx = (selectedChapterFilter - 1) * 10
            all50Units.subList(startIdx, (startIdx + 10).coerceAtMost(all50Units.size))
        }
    }

    val completedCount = progressList.count { it.bestScore >= 70 }
    val realStreakDays = remember(progressList) {
        calculateConsecutiveDayStreak(progressList)
    }

    val dailyTarget = 4
    val completedToday = remember(progressList) {
        val todayDayIndex = System.currentTimeMillis() / 86_400_000L
        progressList.count { (it.completedAtEpochMs / 86_400_000L) == todayDayIndex && it.bestScore >= 70 }
    }
    val dailyProgressRatio = (completedToday.toFloat() / dailyTarget.toFloat()).coerceIn(0f, 1f)

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // TOP BAR: Immagine Vocalfox a sinistra + Badge Lingua e Streak a destra
        item {
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                VocalFoxWordmark(height = 32.dp)

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Badge corso attivo (cliccabile per cambiare lingua nel Profilo)
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                            .clickable(onClick = onOpenProfileSettings)
                            .padding(horizontal = 12.dp, vertical = 7.dp)
                    ) {
                        Text(
                            text = "${currentPack.languageName.get(systemLang)} · ${selectedCefr.name}",
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                    }

                    // Streak reale
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                            .padding(horizontal = 10.dp, vertical = 7.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.LocalFireDepartment,
                            contentDescription = null,
                            tint = if (realStreakDays > 0) colors.accent else colors.mutedText,
                            modifier = Modifier.size(18.dp)
                        )
                        Text(
                            text = "$realStreakDays",
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                    }
                }
            }
        }

        // SELETTORE LIVELLO PULITO (A1, A2, B1, B2)
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CefrLevel.entries.forEach { level ->
                    val isSelected = level == selectedCefr
                    val doneInLevel = progressList.count { it.cefrLevel == level.name && it.bestScore >= 70 }
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (isSelected) colors.accent else colors.card)
                            .border(
                                width = 1.dp,
                                color = if (isSelected) colors.accent else colors.hairline,
                                shape = RoundedCornerShape(14.dp)
                            )
                            .clickable { onSelectCefr(level) }
                            .padding(vertical = 10.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(2.dp)
                    ) {
                        Text(
                            text = level.name,
                            style = VocalFoxType.SectionTitle,
                            color = if (isSelected) colors.onAccent else colors.primaryText,
                            maxLines = 1
                        )
                        Text(
                            text = "$doneInLevel/50",
                            style = VocalFoxType.SecondaryCaption,
                            color = if (isSelected) colors.onAccent.copy(alpha = 0.85f) else colors.mutedText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        // OBIETTIVO GIORNALIERO COMPATTO
        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                    .padding(16.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(68.dp),
                    contentAlignment = Alignment.Center
                ) {
                    val trackCol = colors.raised
                    val arcCol = colors.accent
                    Canvas(modifier = Modifier.fillMaxSize()) {
                        drawArc(
                            color = trackCol,
                            startAngle = 135f,
                            sweepAngle = 270f,
                            useCenter = false,
                            style = Stroke(width = 16f, cap = StrokeCap.Round)
                        )
                        if (dailyProgressRatio > 0f) {
                            drawArc(
                                color = arcCol,
                                startAngle = 135f,
                                sweepAngle = 270f * dailyProgressRatio,
                                useCenter = false,
                                style = Stroke(width = 16f, cap = StrokeCap.Round)
                            )
                        }
                    }
                    Text(
                        text = "$completedToday/$dailyTarget",
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                }

                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = strings.dailyGoalTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Text(
                        text = if (isIt) "$completedCount unità completate in totale" else "$completedCount total units completed",
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }
            }
        }

        // FILTRO CAPITOLI (Tutte, 1-10, 11-20, 21-30, 31-40, 41-50)
        item {
            val chapterFilters = listOf(
                0 to (if (isIt) "Tutte" else "All"),
                1 to "1–10",
                2 to "11–20",
                3 to "21–30",
                4 to "31–40",
                5 to "41–50"
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                chapterFilters.forEach { (chapIdx, label) ->
                    val active = selectedChapterFilter == chapIdx
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(10.dp))
                            .background(if (active) colors.primaryText else colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(10.dp))
                            .clickable { selectedChapterFilter = chapIdx }
                            .padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = if (chapIdx == 0) label else (if (isIt) "Unità $label" else "Units $label"),
                            style = VocalFoxType.BodyMedium,
                            color = if (active) colors.background else colors.secondaryText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        // LISTA DELLE 50 UNITÀ (Card pulite, zero testo spezzato in verticale!)
        itemsIndexed(displayedUnits, key = { _, u -> u.grammarExercise.id }) { idx, unit ->
            val isCompleted = progressList.any { it.itemKey == unit.grammarExercise.id && it.bestScore >= 70 }
            val isNextActive = idx == 0 || !isCompleted

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier
                        .width(16.dp)
                        .fillMaxHeight()
                ) {
                    Spacer(modifier = Modifier.height(22.dp))
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                            .background(
                                when {
                                    isCompleted -> colors.positive
                                    idx == 0 -> colors.accent
                                    else -> colors.raised
                                }
                            )
                            .border(
                                width = 2.dp,
                                color = if (isNextActive) colors.accent else colors.mutedText.copy(alpha = 0.35f),
                                shape = CircleShape
                            )
                    )
                    if (idx < displayedUnits.lastIndex) {
                        Box(
                            modifier = Modifier
                                .width(2.dp)
                                .weight(1f)
                                .padding(vertical = 4.dp)
                                .background(colors.hairline)
                        )
                    }
                }

                // Card Unità Pulita
                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.card)
                        .border(
                            width = if (idx == 0) 1.5.dp else 1.dp,
                            color = if (idx == 0) colors.accent.copy(alpha = 0.5f) else colors.hairline,
                            shape = RoundedCornerShape(16.dp)
                        )
                        .clickable { onStartGuidedUnit(unit) }
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = if (isIt) "Unità ${unit.unitIndex + 1}" else "Unit ${unit.unitIndex + 1}",
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.accent,
                            maxLines = 1
                        )
                        Text(
                            text = unit.title,
                            style = VocalFoxType.SectionTitle,
                            color = colors.primaryText,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            text = unit.subtitle,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )

                        Spacer(modifier = Modifier.height(2.dp))

                        // Bottone orizzontale pulito che non va MAI a capo lettera per lettera
                        Row(
                            modifier = Modifier
                                .clip(RoundedCornerShape(10.dp))
                                .background(if (isCompleted) colors.positive.copy(alpha = 0.12f) else colors.accent)
                                .padding(horizontal = 14.dp, vertical = 7.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = if (isCompleted) Icons.Outlined.Check else Icons.Outlined.PlayArrow,
                                contentDescription = null,
                                tint = if (isCompleted) colors.positive else colors.onAccent,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = if (isCompleted) (if (isIt) "Completata" else "Completed") else strings.startUnitAction,
                                style = VocalFoxType.BodyMedium,
                                color = if (isCompleted) colors.positive else colors.onAccent,
                                maxLines = 1
                            )
                        }
                    }

                    VocalFoxMascot(
                        state = unit.mascotPose,
                        size = 76.dp,
                        tintBackground = unit.tintColor
                    )
                }
            }
        }

        item { Spacer(modifier = Modifier.height(24.dp)) }
    }
}

private fun calculateConsecutiveDayStreak(progressList: List<UserProgressEntity>): Int {
    val completedDays = progressList
        .filter { it.bestScore >= 70 && it.completedAtEpochMs > 0L }
        .map { it.completedAtEpochMs / 86_400_000L }
        .distinct()
        .sortedDescending()

    if (completedDays.isEmpty()) return 0

    val today = System.currentTimeMillis() / 86_400_000L
    if (completedDays.first() < today - 1) return 0

    var streak = 1
    for (i in 0 until completedDays.lastIndex) {
        if (completedDays[i] - completedDays[i + 1] == 1L) {
            streak++
        } else {
            break
        }
    }
    return streak
}

fun buildGuidedUnitsForPack(
    pack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang
): List<GuidedUnitBundle> {
    return CurriculumGenerator.generate50UnitsForLevel(pack, selectedCefr, systemLang)
}
