package com.vocalfox.app.ui.screens

import android.content.Context
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
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.vocalfox.app.data.local.VoiceModelConfigEntity
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.VoicePreset
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
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
    onPreviewVoice: (String, VoicePreset) -> Unit,
    selectedTargetLangCode: String = "es",
    onSelectTargetLang: (String) -> Unit = {}
) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("vocalfox_prefs", Context.MODE_PRIVATE) }
    var geminiApiKey by remember { mutableStateOf(prefs.getString("gemini_api_key", "").orEmpty()) }
    var keySavedToast by remember { mutableStateOf(false) }

    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Active Language Course Switcher (Spanish / German)
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = if (isIt) "Corso di lingua attivo" else "Active language course",
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                allPacks.values.forEach { pack ->
                    val active = pack.languageCode == selectedTargetLangCode
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (active) colors.accent else colors.raised)
                            .clickable { onSelectTargetLang(pack.languageCode) }
                            .padding(vertical = 14.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "${pack.languageCode.uppercase()} · ${pack.languageName.get(systemLang)}",
                            style = VocalFoxType.BodyMedium,
                            color = if (active) colors.onAccent else colors.primaryText
                        )
                    }
                }
            }
        }

        // Google Gemini Live AI API Key Configuration
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(
                text = "Google Gemini Live AI (API Key)",
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )
            Text(
                text = if (isIt) "Inserisci la tua API Key di Google AI Studio per conversare dal vivo col tutor VocalFox." else "Enter your Google AI Studio API Key to enable Live AI Conversation.",
                style = VocalFoxType.SecondaryCaption,
                color = colors.secondaryText
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(10.dp))
                        .background(colors.raised)
                        .padding(horizontal = 12.dp, vertical = 12.dp)
                ) {
                    if (geminiApiKey.isEmpty()) {
                        Text("AIzaSy...", style = VocalFoxType.MetaMono, color = colors.mutedText)
                    }
                    BasicTextField(
                        value = geminiApiKey,
                        onValueChange = {
                            geminiApiKey = it
                            keySavedToast = false
                        },
                        textStyle = VocalFoxType.MetaMono.copy(color = colors.primaryText),
                        cursorBrush = SolidColor(colors.accent),
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(10.dp))
                        .background(colors.accent)
                        .clickable {
                            prefs.edit().putString("gemini_api_key", geminiApiKey.trim()).apply()
                            keySavedToast = true
                        }
                        .padding(horizontal = 16.dp, vertical = 12.dp)
                ) {
                    Text(
                        text = if (keySavedToast) "Salvata ✓" else (if (isIt) "Salva" else "Save"),
                        style = VocalFoxType.BodyMedium,
                        color = colors.onAccent
                    )
                }
            }
        }

        // System UI Language Switcher
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = strings.systemLanguageSection,
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                SystemLang.entries.forEach { lang ->
                    val isSelected = lang == systemLang
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isSelected) colors.accent else colors.raised)
                            .clickable { onSelectSystemLang(lang) }
                            .padding(vertical = 12.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = lang.displayName,
                            style = VocalFoxType.BodyMedium,
                            color = if (isSelected) colors.onAccent else colors.primaryText
                        )
                    }
                }
            }
        }

        // Dark Mode Toggle
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(horizontal = 18.dp, vertical = 14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = strings.appearanceSection,
                    style = VocalFoxType.SectionTitle,
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

        // Clean Teacher Voice Picker
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .background(colors.card)
                .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Text(
                text = strings.voiceModelsSection,
                style = VocalFoxType.SectionTitle,
                color = colors.primaryText
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
                        text = pack.languageName.get(systemLang),
                        style = VocalFoxType.BodyMedium,
                        color = colors.accent
                    )

                    pack.availableVoices.forEach { preset ->
                        val isSelected = preset.voiceId == activeVoiceId
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(if (isSelected) colors.raised else colors.background)
                                .border(
                                    width = if (isSelected) 1.5.dp else 1.dp,
                                    color = if (isSelected) colors.accent else colors.hairline,
                                    shape = RoundedCornerShape(12.dp)
                                )
                                .clickable { onSelectVoicePreset(pack.languageCode, preset) }
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Text(
                                    text = preset.displayName,
                                    style = VocalFoxType.BodyMedium,
                                    color = colors.primaryText
                                )
                                Text(
                                    text = "${preset.gender} · ${preset.timbre}",
                                    style = VocalFoxType.SecondaryCaption,
                                    color = colors.secondaryText
                                )
                            }

                            Row(
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(colors.card)
                                        .border(1.dp, colors.hairline, RoundedCornerShape(8.dp))
                                        .clickable { onPreviewVoice(pack.languageCode, preset) }
                                        .padding(8.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = strings.previewVoiceAction,
                                        tint = colors.primaryText,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                                if (isSelected) {
                                    Icon(
                                        imageVector = Icons.Outlined.Check,
                                        contentDescription = null,
                                        tint = colors.accent,
                                        modifier = Modifier.size(20.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(110.dp))
    }
}
