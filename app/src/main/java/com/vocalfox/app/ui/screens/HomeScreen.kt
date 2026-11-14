package com.vocalfox.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material.icons.outlined.Schedule
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType

/**
 * Redesigned Home Screen following Design Example.pdf:
 * - Page 2 Top Bar (Language pill left, VocalFox center, Circular Profile button right)
 * - Page 2 Fitbit-style Daily Progress Ring + 3 Clean Metrics
 * - Page 1 Headspace-style Vertical Timeline with orange active node and large Mascot illustration right
 */
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

    // Build the list of guided units for the current level (plus cross-level units)
    val units = remember(currentPack.languageCode, selectedCefr, systemLang) {
        buildGuidedUnitsForPack(currentPack, selectedCefr, systemLang)
    }

    val completedCount = progressList.count { it.bestScore >= 70 }
    val dailyTarget = 4
    val dailyProgressRatio = (completedCount % (dailyTarget + 1)).toFloat() / dailyTarget.toFloat()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp)
    ) {
        // TOP BAR (Inspired by Page 2 of Design Example.pdf)
        item {
            Spacer(modifier = Modifier.height(6.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Language Switcher Pill
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(20.dp))
                        .background(colors.raised)
                        .padding(4.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    allPacks.keys.forEach { code ->
                        val active = code == currentPack.languageCode
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(16.dp))
                                .background(if (active) colors.card else colors.raised)
                                .clickable { onSelectLanguage(code) }
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = code.uppercase(),
                                style = VocalFoxType.MetaMono,
                                color = if (active) colors.accent else colors.secondaryText
                            )
                        }
                    }
                }

                // Center Title
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "VocalFox",
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Text(
                        text = "${currentPack.languageName.get(systemLang)} · ${selectedCefr.name}",
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }

                // Right Profile / Settings Avatar Button
                Box(
                    modifier = Modifier
                        .size(42.dp)
                        .clip(CircleShape)
                        .background(colors.card)
                        .border(1.dp, colors.hairline, CircleShape)
                        .clickable(onClick = onOpenProfileSettings),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Person,
                        contentDescription = strings.profileSettingsTitle,
                        tint = colors.primaryText,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }

        // CLEAN LEVEL PILLS (Single-line, zero broken text!)
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CefrLevel.entries.forEach { level ->
                    val isSelected = level == selectedCefr
                    Box(
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
                            .padding(vertical = 12.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = level.name,
                            style = VocalFoxType.BodyMedium,
                            color = if (isSelected) colors.onAccent else colors.primaryText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        // DAILY GOAL RING CARD (Inspired by Page 2 of Design Example.pdf)
        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(20.dp))
                    .padding(20.dp),
                horizontalArrangement = Arrangement.spacedBy(20.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(84.dp),
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
                            style = Stroke(width = 18f, cap = StrokeCap.Round)
                        )
                        drawArc(
                            color = arcCol,
                            startAngle = 135f,
                            sweepAngle = 270f * dailyProgressRatio.coerceIn(0.12f, 1f),
                            useCenter = false,
                            style = Stroke(width = 18f, cap = StrokeCap.Round)
                        )
                    }
                    Text(
                        text = "${completedCount % (dailyTarget + 1)}/$dailyTarget",
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                }

                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Text(
                        text = strings.dailyGoalTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Column {
                            Text(
                                text = "14",
                                style = VocalFoxType.CardFigure,
                                color = colors.accent
                            )
                            Text(
                                text = strings.streakTitle,
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.secondaryText,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                        Column {
                            Text(
                                text = "$completedCount",
                                style = VocalFoxType.CardFigure,
                                color = colors.primaryText
                            )
                            Text(
                                text = strings.wordsLearnedTitle,
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.secondaryText,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }
                }
            }
        }

        // HEADSPACE-STYLE VERTICAL TIMELINE (Inspired by Page 1 of Design Example.pdf)
        itemsIndexed(units) { index, unit ->
            val isCompleted = progressList.any { it.itemKey == unit.grammarExercise.id && it.bestScore >= 70 }
            val isActive = index == 0 || !isCompleted

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Left Timeline Column (Dot + Vertical Line)
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier
                        .width(20.dp)
                        .fillMaxHeight()
                ) {
                    Spacer(modifier = Modifier.height(24.dp))
                    Box(
                        modifier = Modifier
                            .size(14.dp)
                            .clip(CircleShape)
                            .background(
                                when {
                                    isCompleted -> colors.positive
                                    index == 0 -> colors.accent
                                    else -> colors.raised
                                }
                            )
                            .border(
                                width = 2.dp,
                                color = if (isActive) colors.accent else colors.mutedText.copy(alpha = 0.4f),
                                shape = CircleShape
                            )
                    )
                    if (index < units.lastIndex) {
                        Box(
                            modifier = Modifier
                                .width(2.dp)
                                .weight(1f)
                                .padding(vertical = 4.dp)
                                .background(colors.hairline)
                        )
                    }
                }

                // Right Lesson Card with Large Mascot Illustration (Page 1 of PDF)
                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(20.dp))
                        .background(colors.card)
                        .border(
                            width = if (index == 0) 1.5.dp else 1.dp,
                            color = if (index == 0) colors.accent.copy(alpha = 0.45f) else colors.hairline,
                            shape = RoundedCornerShape(20.dp)
                        )
                        .clickable { onStartGuidedUnit(unit) }
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(14.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = "${unit.cefr.name} · Unità ${unit.unitIndex + 1}",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Text(
                            text = unit.title,
                            style = VocalFoxType.SectionTitle,
                            color = colors.primaryText,
                            maxLines = 2,
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

                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = if (isCompleted) Icons.Outlined.Check else Icons.Outlined.Schedule,
                                contentDescription = null,
                                tint = if (isCompleted) colors.positive else colors.mutedText,
                                modifier = Modifier.size(15.dp)
                            )
                            Text(
                                text = "${unit.durationMinutes} min",
                                style = VocalFoxType.MetaMono,
                                color = colors.mutedText
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Row(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(colors.accent.copy(alpha = 0.12f))
                                    .padding(horizontal = 10.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.PlayArrow,
                                    contentDescription = null,
                                    tint = colors.accent,
                                    modifier = Modifier.size(14.dp)
                                )
                                Text(
                                    text = strings.startUnitAction,
                                    style = VocalFoxType.MetaMono,
                                    color = colors.accent
                                )
                            }
                        }
                    }

                    // Large, centered Mascot Illustration Box (Page 1 Headspace Card Right Side)
                    VocalFoxMascot(
                        state = unit.mascotPose,
                        size = 96.dp,
                        tintBackground = unit.tintColor
                    )
                }
            }
        }

        item { Spacer(modifier = Modifier.height(100.dp)) }
    }
}

fun buildGuidedUnitsForPack(
    pack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang
): List<GuidedUnitBundle> {
    val tints = listOf(
        VocalFoxPalette.TintWarmAmber,
        VocalFoxPalette.TintSoftGold,
        VocalFoxPalette.TintMintSage,
        VocalFoxPalette.TintCalmSky
    )
    val poses = listOf(
        MascotState.LOGO_IDLE,
        MascotState.CELEBRATE,
        MascotState.THINKING,
        MascotState.STRICT_COACH
    )

    val levelGrammar = pack.grammarExercises.filter { it.cefr == selectedCefr }
        .ifEmpty { pack.grammarExercises }
    val levelWriting = pack.writingExercises.filter { it.cefr == selectedCefr }
        .ifEmpty { pack.writingExercises }
    val levelSpeech = pack.pronunciationDrills.filter { it.cefr == selectedCefr }
        .ifEmpty { pack.pronunciationDrills }

    val count = maxOf(levelGrammar.size, levelWriting.size, levelSpeech.size).coerceAtLeast(1)
    return (0 until count).map { idx ->
        val g = levelGrammar[idx % levelGrammar.size]
        val w = levelWriting[idx % levelWriting.size]
        val s = levelSpeech[idx % levelSpeech.size]
        GuidedUnitBundle(
            unitIndex = idx,
            cefr = selectedCefr,
            title = g.title.get(systemLang),
            subtitle = s.targetSentence,
            durationMinutes = 3 + (idx % 3),
            tintColor = tints[idx % tints.size],
            mascotPose = poses[idx % poses.size],
            grammarExercise = g,
            writingExercise = w,
            pronunciationDrill = s
        )
    }
}
