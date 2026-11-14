#!/usr/bin/env python3
"""
fix_quotes.py
Corregge le virgolette nella stringa di benvenuto in LiveConversationScreen.kt.
"""

from pathlib import Path

LIVE_CONVERSATION_KT = """\
package com.vocalfox.app.ui.screens

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.speech.RecognizerIntent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Key
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.Send
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.vocalfox.app.audio.GeminiLiveTutorClient
import com.vocalfox.app.audio.TutorChatMessage
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import kotlinx.coroutines.launch

@Composable
fun LiveConversationScreen(
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    onSpeakText: (String, Float) -> Unit,
    onOpenSettingsForApiKey: () -> Unit
) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("vocalfox_prefs", Context.MODE_PRIVATE) }
    val colors = VocalFoxTheme.colors
    val scope = rememberCoroutineScope()
    val isIt = systemLang == SystemLang.IT

    var apiKey by remember { mutableStateOf(prefs.getString("gemini_api_key", "").orEmpty()) }
    var showInlineKeyEditor by remember { mutableStateOf(apiKey.isBlank()) }

    val scenarios = remember(isIt) {
        if (isIt) {
            listOf(
                "Conversazione libera",
                "Al Bar e Ristorante",
                "Viaggio, Hotel e Stazione",
                "Colloquio di Lavoro",
                "Dibattito d'Attualità"
            )
        } else {
            listOf(
                "Free Conversation",
                "At the Café & Restaurant",
                "Travel, Hotel & Station",
                "Job Interview",
                "Current Events Debate"
            )
        }
    }

    var selectedScenario by remember { mutableStateOf(scenarios.first()) }
    var userInput by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    val messages = remember(currentPack.languageCode, selectedScenario) {
        mutableStateListOf(
            if (currentPack.languageCode == "de") {
                TutorChatMessage(
                    isUser = false,
                    text = "Hallo! Ich bin dein VocalFox Tutor (${selectedCefr.name}). Wollen wir über '$selectedScenario' auf Deutsch sprechen?",
                    translation = if (isIt) "Ciao! Sono il tuo tutor VocalFox (${selectedCefr.name}). Parliamo di '$selectedScenario' in tedesco?" else "Hello! I am your VocalFox tutor. Shall we speak German?",
                    grammarCorrection = ""
                )
            } else {
                TutorChatMessage(
                    isUser = false,
                    text = "¡Hola! Soy tu tutor VocalFox (${selectedCefr.name}). ¿Hablamos sobre '$selectedScenario' en español?",
                    translation = if (isIt) "Ciao! Sono il tuo tutor VocalFox (${selectedCefr.name}). Parliamo di '$selectedScenario' in spagnolo?" else "Hello! I am your VocalFox tutor. Shall we speak Spanish?",
                    grammarCorrection = ""
                )
            }
        )
    }

    fun sendUserTurn(textToSend: String) {
        val trimmed = textToSend.trim()
        if (trimmed.isBlank() || isLoading) return
        if (apiKey.isBlank()) {
            showInlineKeyEditor = true
            errorMessage = if (isIt) "Inserisci prima la tua API Key gratuita di Google Gemini qui sopra." else "Please enter your Google Gemini API key above first."
            return
        }

        errorMessage = null
        messages.add(TutorChatMessage(isUser = true, text = trimmed))
        userInput = ""
        isLoading = true

        scope.launch {
            val res = GeminiLiveTutorClient.sendMessageToTutor(
                apiKey = apiKey,
                targetLanguageCode = currentPack.languageCode,
                cefrLevel = selectedCefr,
                systemLang = systemLang,
                scenarioTitle = selectedScenario,
                history = messages.dropLast(1),
                userMessage = trimmed
            )
            isLoading = false
            res.onSuccess { replyMsg ->
                messages.add(replyMsg)
                onSpeakText(replyMsg.text, 1.0f)
            }.onFailure { err ->
                errorMessage = err.localizedMessage ?: "Errore chiamata Gemini"
            }
        }
    }

    val speechRecognizerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val spoken = result.data
                ?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                ?.firstOrNull()
            if (!spoken.isNullOrBlank()) {
                sendUserTurn(spoken)
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp)
    ) {
        Spacer(modifier = Modifier.height(10.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "Live AI Tutor · ${currentPack.languageName.get(systemLang)} (${selectedCefr.name})",
                    style = VocalFoxType.PageTitle,
                    color = colors.primaryText
                )
                Text(
                    text = if (isIt) "Parla o scrivi con Gemini Live e ricevi correzioni istantanee" else "Speak or type with Gemini Live and get instant feedback",
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.secondaryText
                )
            }
            Box(
                modifier = Modifier
                    .size(42.dp)
                    .clip(CircleShape)
                    .background(colors.card)
                    .border(1.dp, if (apiKey.isBlank()) colors.accent else colors.hairline, CircleShape)
                    .clickable { showInlineKeyEditor = !showInlineKeyEditor },
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Outlined.Key, contentDescription = "API Key", tint = colors.accent, modifier = Modifier.size(20.dp))
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        if (showInlineKeyEditor) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.card)
                    .border(1.5.dp, colors.accent, RoundedCornerShape(16.dp))
                    .padding(14.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Text(
                    text = if (isIt) "Chiave API Google Gemini (AI Studio)" else "Google Gemini API Key (AI Studio)",
                    style = VocalFoxType.BodyMedium,
                    color = colors.primaryText
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
                            .padding(horizontal = 12.dp, vertical = 10.dp)
                    ) {
                        if (apiKey.isEmpty()) {
                            Text("AIzaSy...", style = VocalFoxType.MetaMono, color = colors.mutedText)
                        }
                        BasicTextField(
                            value = apiKey,
                            onValueChange = { apiKey = it },
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
                                prefs.edit().putString("gemini_api_key", apiKey.trim()).apply()
                                showInlineKeyEditor = false
                                errorMessage = null
                            }
                            .padding(horizontal = 14.dp, vertical = 10.dp)
                    ) {
                        Text(
                            text = if (isIt) "Salva" else "Save",
                            style = VocalFoxType.BodyMedium,
                            color = colors.onAccent
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            scenarios.forEach { scen ->
                val active = scen == selectedScenario
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (active) colors.accent else colors.card)
                        .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                        .clickable { selectedScenario = scen }
                        .padding(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = scen,
                        style = VocalFoxType.SecondaryCaption,
                        color = if (active) colors.onAccent else colors.primaryText
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        if (errorMessage != null) {
            Text(
                text = errorMessage!!,
                style = VocalFoxType.SecondaryCaption,
                color = colors.negative,
                modifier = Modifier.padding(vertical = 4.dp)
            )
        }

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(messages) { msg ->
                if (!msg.isUser) {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        if (msg.grammarCorrection.isNotBlank()) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(VocalFoxPalette.TintMintSage)
                                    .padding(12.dp)
                            ) {
                                Text(
                                    text = "Consiglio: ${msg.grammarCorrection}",
                                    style = VocalFoxType.SecondaryCaption,
                                    color = VocalFoxPalette.FoxDeepInkBrown
                                )
                            }
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalAlignment = Alignment.Top
                        ) {
                            VocalFoxMascot(
                                state = MascotState.LOGO_IDLE,
                                size = 48.dp,
                                tintBackground = VocalFoxPalette.TintWarmAmber
                            )
                            Column(
                                modifier = Modifier
                                    .weight(1f)
                                    .clip(RoundedCornerShape(18.dp))
                                    .background(colors.card)
                                    .border(1.dp, colors.hairline, RoundedCornerShape(18.dp))
                                    .padding(14.dp),
                                verticalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Text(
                                    text = msg.text,
                                    style = VocalFoxType.BodyMedium,
                                    color = colors.primaryText
                                )
                                if (msg.translation.isNotBlank()) {
                                    Text(
                                        text = msg.translation,
                                        style = VocalFoxType.SecondaryCaption,
                                        color = colors.secondaryText
                                    )
                                }
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(colors.raised)
                                            .clickable { onSpeakText(msg.text, 1.0f) }
                                            .padding(horizontal = 10.dp, vertical = 6.dp),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        Icon(Icons.Outlined.VolumeUp, null, tint = colors.accent, modifier = Modifier.size(15.dp))
                                        Text("1.0x", style = VocalFoxType.MetaMono, color = colors.primaryText)
                                    }
                                    Row(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(colors.raised)
                                            .clickable { onSpeakText(msg.text, 0.75f) }
                                            .padding(horizontal = 10.dp, vertical = 6.dp),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        Icon(Icons.Outlined.SlowMotionVideo, null, tint = colors.accent, modifier = Modifier.size(15.dp))
                                        Text("0.75x", style = VocalFoxType.MetaMono, color = colors.primaryText)
                                    }
                                }
                            }
                        }
                    }
                } else {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.End
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(18.dp))
                                .background(colors.accent)
                                .padding(horizontal = 16.dp, vertical = 12.dp)
                        ) {
                            Text(
                                text = msg.text,
                                style = VocalFoxType.BodyMedium,
                                color = colors.onAccent
                            )
                        }
                    }
                }
            }

            if (isLoading) {
                item {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        modifier = Modifier.padding(8.dp)
                    ) {
                        CircularProgressIndicator(
                            color = colors.accent,
                            strokeWidth = 2.5.dp,
                            modifier = Modifier.size(22.dp)
                        )
                        Text(
                            text = if (isIt) "VocalFox sta rispondendo..." else "VocalFox is replying...",
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(8.dp)) }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp, bottom = 104.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(colors.raised)
                    .border(1.dp, colors.hairline, CircleShape)
                    .clickable {
                        try {
                            val localeTag = if (currentPack.languageCode == "de") "de-DE" else "es-ES"
                            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                                putExtra(RecognizerIntent.EXTRA_LANGUAGE, localeTag)
                            }
                            speechRecognizerLauncher.launch(intent)
                        } catch (_: Throwable) {
                            errorMessage = if (isIt) "Riconoscimento vocale non disponibile, usa la tastiera." else "Voice recognition unavailable, please type."
                        }
                    },
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Outlined.Mic, contentDescription = "Speak", tint = colors.accent, modifier = Modifier.size(22.dp))
            }

            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(24.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(24.dp))
                    .padding(horizontal = 16.dp, vertical = 14.dp)
            ) {
                if (userInput.isEmpty()) {
                    Text(
                        text = if (currentPack.languageCode == "de") "Scrivi o parla in tedesco..." else "Scrivi o parla in spagnolo...",
                        style = VocalFoxType.Body,
                        color = colors.mutedText
                    )
                }
                BasicTextField(
                    value = userInput,
                    onValueChange = { userInput = it },
                    textStyle = VocalFoxType.Body.copy(color = colors.primaryText),
                    cursorBrush = SolidColor(colors.accent),
                    modifier = Modifier.fillMaxWidth()
                )
            }

            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(colors.accent)
                    .clickable { sendUserTurn(userInput) },
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Outlined.Send, contentDescription = "Send", tint = colors.onAccent, modifier = Modifier.size(20.dp))
            }
        }
    }
}
"""


def main() -> None:
    root = Path.cwd()
    if not (root / "settings.gradle.kts").exists():
        root = Path(__file__).resolve().parent

    target = root / "app/src/main/java/com/vocalfox/app/ui/screens/LiveConversationScreen.kt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(LIVE_CONVERSATION_KT, encoding="utf-8")
    print(f"[OK] Corretto: {target}")
    print("\nEsegui ora:")
    print("git add -A")
    print('git commit -m "Fix quotes in LiveConversationScreen.kt"')
    print("git push origin main")


if __name__ == "__main__":
    main()