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
