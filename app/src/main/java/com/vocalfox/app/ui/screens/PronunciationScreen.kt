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
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.Stop
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
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
    val drill = currentPack.pronunciationDrills.firstOrNull { it.cefr == selectedCefr }
        ?: currentPack.pronunciationDrills.first()

    var selectedWordIndex by remember(drill.id, pronunciationResult) { mutableStateOf(0) }

    val micPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            onStartRecording(drill)
        } else {
            onStopAndEvaluate(drill, null)
        }
    }

    val mascotState = when {
        pronunciationResult == null -> MascotState.LOGO_IDLE
        pronunciationResult.overallScore >= 85 -> MascotState.CELEBRATE
        pronunciationResult.overallScore >= 60 -> MascotState.STRICT_COACH
        else -> MascotState.ENCOURAGE_SAD
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
                    text = strings.pronunciationHeader,
                    style = VocalFoxType.PageTitle,
                    color = colors.primaryText
                )
                Text(
                    text = "${activeVoice.displayName} · ${activeVoice.onnxFileName}",
                    style = VocalFoxType.MetaMono,
                    color = colors.mutedText
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
            if (showFurigana && drill.furiganaOrReading.isNotBlank()) {
                Text(
                    text = drill.furiganaOrReading,
                    style = VocalFoxType.MetaMono,
                    color = colors.accent
                )
            }

            Text(
                text = drill.targetSentence,
                style = VocalFoxType.SentenceDisplay,
                color = colors.primaryText
            )

            Text(
                text = drill.fullIpa,
                style = VocalFoxType.MetaMono,
                color = colors.secondaryText
            )

            Text(
                text = drill.translation.get(systemLang),
                style = VocalFoxType.SecondaryCaption,
                color = colors.mutedText
            )

            Spacer(modifier = Modifier.height(4.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .background(colors.raised)
                        .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .clickable { onPlayTts(drill.targetSentence, 1.0f) }
                        .padding(vertical = 10.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.VolumeUp,
                        contentDescription = null,
                        tint = colors.primaryText,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = strings.playNormalAction,
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                }

                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .background(colors.raised)
                        .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .clickable { onPlayTts(drill.targetSentence, 0.75f) }
                        .padding(vertical = 10.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.SlowMotionVideo,
                        contentDescription = null,
                        tint = colors.primaryText,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = strings.playSlowAction,
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                    .background(if (isRecording) colors.negative else colors.accent)
                    .clickable {
                        if (isRecording) {
                            onStopAndEvaluate(drill, null)
                        } else {
                            val granted = ContextCompat.checkSelfPermission(
                                context,
                                Manifest.permission.RECORD_AUDIO
                            ) == PackageManager.PERMISSION_GRANTED
                            if (granted) {
                                onStartRecording(drill)
                            } else {
                                micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                            }
                        }
                    }
                    .padding(vertical = 12.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (isRecording) Icons.Outlined.Stop else Icons.Outlined.Mic,
                    contentDescription = null,
                    tint = colors.onAccent,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (isRecording) strings.stopRecordingAction else strings.holdToRecordAction,
                    style = VocalFoxType.BodyMedium,
                    color = colors.onAccent
                )
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
                text = strings.articulatoryTipLabel,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )
            drill.criticalPhonemes.forEach { trap ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .background(colors.raised)
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "${trap.grapheme} /${trap.ipa}/",
                        style = VocalFoxType.MetaMono,
                        color = colors.accent
                    )
                    Text(
                        text = trap.trapDescription.get(systemLang),
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }
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
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = strings.phoneticBreakdownTitle,
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                    Text(
                        text = "${pronunciationResult.overallScore}/100 · ${"%.2f".format(pronunciationResult.durationRatio)}x",
                        style = VocalFoxType.MetaMono,
                        color = when {
                            pronunciationResult.overallScore >= 85 -> colors.positive
                            pronunciationResult.overallScore >= 65 -> colors.warning
                            else -> colors.negative
                        }
                    )
                }

                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    pronunciationResult.wordFeedbacks.forEachIndexed { idx, wf ->
                        val statusColor = when (wf.status) {
                            PhonemeAccuracyStatus.ACCURATE -> colors.positive
                            PhonemeAccuracyStatus.STRESS_OR_PITCH -> colors.warning
                            PhonemeAccuracyStatus.MISPRONOUNCED -> colors.negative
                        }
                        Column(
                            modifier = Modifier
                                .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                                .background(if (selectedWordIndex == idx) colors.raised else colors.background)
                                .clickable { selectedWordIndex = idx }
                                .padding(horizontal = 10.dp, vertical = 8.dp)
                        ) {
                            Text(
                                text = wf.word,
                                style = VocalFoxType.BodyMedium,
                                color = colors.primaryText
                            )
                            Box(
                                modifier = Modifier
                                    .padding(vertical = 4.dp)
                                    .height(3.dp)
                                    .width((wf.word.length * 9).coerceAtLeast(24).dp)
                                    .background(statusColor)
                            )
                            Text(
                                text = "/${wf.observedIpa}/ · ${wf.score}%",
                                style = VocalFoxType.MetaMono,
                                color = statusColor
                            )
                        }
                    }
                }

                val inspectedWord = pronunciationResult.wordFeedbacks.getOrNull(selectedWordIndex)
                if (inspectedWord != null) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                            .background(colors.raised)
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Text(
                            text = "${inspectedWord.word} — Target /${inspectedWord.expectedIpa}/ vs Observed /${inspectedWord.observedIpa}/",
                            style = VocalFoxType.MetaMono,
                            color = colors.primaryText
                        )
                        Text(
                            text = inspectedWord.diagnosticNote,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )
                    }
                }
            }
        }

        MascotPedagogicalBanner(
            state = mascotState,
            title = if (pronunciationResult != null) {
                "IPA Alignment · ${pronunciationResult.overallScore}%"
            } else {
                strings.articulatoryTipLabel
            },
            subtitle = drill.articulatoryTip.get(systemLang),
            metaBadge = drill.cefr.name
        )

        Spacer(modifier = Modifier.height(16.dp))
    }
}
