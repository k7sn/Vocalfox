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
import com.vocalfox.app.ui.theme.MascotPedagogicalBanner
import com.vocalfox.app.ui.theme.MascotState
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
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        Text(
            text = strings.settingsHeader,
            style = VocalFoxType.PageTitle,
            color = colors.primaryText
        )

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
                text = strings.systemLanguageSection,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                SystemLang.entries.forEach { lang ->
                    val isSelected = lang == systemLang
                    Row(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                            .background(if (isSelected) colors.accent else colors.raised)
                            .clickable { onSelectSystemLang(lang) }
                            .padding(horizontal = 16.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = lang.displayName,
                            style = VocalFoxType.BodyMedium,
                            color = if (isSelected) colors.onAccent else colors.primaryText
                        )
                        Text(
                            text = lang.code.uppercase(),
                            style = VocalFoxType.MetaMono,
                            color = if (isSelected) colors.onAccent else colors.mutedText
                        )
                    }
                }
            }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(horizontal = 20.dp, vertical = 16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    text = strings.appearanceSection,
                    style = VocalFoxType.BodyMedium,
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
                text = strings.voiceModelsSection,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )
            Text(
                text = strings.offlineStorageNote,
                style = VocalFoxType.SecondaryCaption,
                color = colors.secondaryText
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
                        text = "${pack.languageName.get(systemLang)} (${pack.languageCode.uppercase()})",
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )

                    pack.availableVoices.forEach { preset ->
                        val isSelected = preset.voiceId == activeVoiceId
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                                .background(if (isSelected) colors.raised else colors.background)
                                .border(
                                    width = 1.dp,
                                    color = if (isSelected) colors.accent else colors.hairline,
                                    shape = RoundedCornerShape(VocalFoxTokens.RadiusControl)
                                )
                                .clickable { onSelectVoicePreset(pack.languageCode, preset) }
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = preset.displayName,
                                        style = VocalFoxType.BodyMedium,
                                        color = colors.primaryText
                                    )
                                    Text(
                                        text = "${preset.gender} · ${preset.timbre}",
                                        style = VocalFoxType.MetaMono,
                                        color = colors.mutedText
                                    )
                                }
                                Text(
                                    text = preset.onnxFileName,
                                    style = VocalFoxType.MetaMono,
                                    color = colors.secondaryText
                                )
                            }

                            Row(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                                        .background(colors.card)
                                        .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                                        .clickable { onPreviewVoice(pack.languageCode, preset) }
                                        .padding(horizontal = 8.dp, vertical = 6.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = strings.previewVoiceAction,
                                        tint = colors.primaryText,
                                        modifier = Modifier.size(16.dp)
                                    )
                                }
                                if (isSelected) {
                                    Icon(
                                        imageVector = Icons.Outlined.Check,
                                        contentDescription = null,
                                        tint = colors.accent,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        MascotPedagogicalBanner(
            state = MascotState.SLEEPING,
            title = "100% Air-Gapped Runtime",
            subtitle = strings.offlineStorageNote,
            metaBadge = "ONNX"
        )

        Spacer(modifier = Modifier.height(16.dp))
    }
}
