#!/usr/bin/env python3
"""
patch_vocalfox.py
Applica:
1. Fix padding barra di scrittura messaggio in LiveConversationScreen.kt (zero spazio vuoto sopra il menu inferiore)
2. Fix outline verde/rosso parola per parola nella composizione frase in OnboardingAndLessonScreens.kt
3. Feature GeminiHandoffHelper.kt per aprire direttamente l'app ufficiale Google Gemini con prompt pre-caricato
"""

from pathlib import Path

FILES: dict[str, str] = {
    "app/src/main/AndroidManifest.xml": """\
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.INTERNET" />

    <queries>
        <package android:name="com.google.android.apps.bard" />
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
        <intent>
            <action android:name="android.speech.RecognitionService" />
        </intent>
    </queries>

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:label="Vocalfox"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
""",

    "app/src/main/java/com/vocalfox/app/audio/GeminiHandoffHelper.kt": """\
package com.vocalfox.app.audio

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.ui.i18n.SystemLang

/**
 * Costruisce un prompt didattico calibrato su lingua, livello CEFR e argomento della lezione,
 * lo copia negli appunti e apre direttamente l'app ufficiale Google Gemini (`com.google.android.apps.bard`)
 * senza bisogno di alcuna API key.
 */
object GeminiHandoffHelper {
    private const val GEMINI_PACKAGE = "com.google.android.apps.bard"

    fun buildTutorPrompt(
        targetLanguageCode: String,
        cefrLevel: CefrLevel,
        systemLang: SystemLang,
        topic: String? = null
    ): String {
        val isIt = systemLang == SystemLang.IT
        val targetLangIt = if (targetLanguageCode == "de") "Tedesco" else "Spagnolo"
        val targetLangEn = if (targetLanguageCode == "de") "German" else "Spanish"

        return if (isIt) {
            val topicClause = if (!topic.isNullOrBlank()) {
                " sull'argomento '$topic'"
            } else {
                " su situazioni della vita quotidiana"
            }
            "Agisci come un tutor madrelingua di $targetLangIt per uno studente di livello ${cefrLevel.name}. " +
                "Facciamo una conversazione pratica$topicClause. " +
                "Usa frasi naturali e brevi adatte al livello ${cefrLevel.name}, parla sempre in $targetLangIt " +
                "e, se faccio errori, aggiungi una breve nota di correzione in Italiano prima di farmi la domanda successiva. " +
                "Inizia tu adesso salutandomi e facendomi la prima domanda in $targetLangIt."
        } else {
            val topicClause = if (!topic.isNullOrBlank()) {
                " about '$topic'"
            } else {
                " about everyday situations"
            }
            "Act as a native $targetLangEn tutor for a ${cefrLevel.name}-level student. " +
                "Let's have a practical conversation$topicClause. " +
                "Use natural, concise sentences suited to level ${cefrLevel.name}, always reply in $targetLangEn, " +
                "and if I make a mistake, include a brief correction note in English before asking your next question. " +
                "Please start now by greeting me and asking the first question in $targetLangEn."
        }
    }

    fun launchGeminiAppWithPrompt(
        context: Context,
        targetLanguageCode: String,
        cefrLevel: CefrLevel,
        systemLang: SystemLang,
        topic: String? = null
    ) {
        val prompt = buildTutorPrompt(
            targetLanguageCode = targetLanguageCode,
            cefrLevel = cefrLevel,
            systemLang = systemLang,
            topic = topic
        )

        // 1. Copia sempre il prompt negli appunti così è pronto anche per Gemini Live vocale
        try {
            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as? ClipboardManager
            clipboard?.setPrimaryClip(ClipData.newPlainText("Vocalfox Gemini Tutor", prompt))
            val toastText = if (systemLang == SystemLang.IT) {
                "Prompt copiato! Incollalo o avvia Gemini Live"
            } else {
                "Prompt copied! Paste it or start Gemini Live"
            }
            Toast.makeText(context, toastText, Toast.LENGTH_LONG).show()
        } catch (_: Throwable) {}

        // 2. Prova ad inviare direttamente il testo all'app ufficiale Google Gemini
        try {
            val sendIntent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, prompt)
                setPackage(GEMINI_PACKAGE)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            if (sendIntent.resolveActivity(context.packageManager) != null) {
                context.startActivity(sendIntent)
                return
            }
        } catch (_: Throwable) {}

        // 3. Fallback: apri l'app Google Gemini installata tramite il suo Launch Intent
        try {
            val launchIntent = context.packageManager.getLaunchIntentForPackage(GEMINI_PACKAGE)
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(launchIntent)
                return
            }
        } catch (_: Throwable) {}

        // 4. Fallback web: apri gemini.google.com nel browser
        try {
            val webIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://gemini.google.com/app")).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(webIntent)
        } catch (_: Throwable) {}
    }
}
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/LiveConversationScreen.kt": """\
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
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AutoAwesome
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
import com.vocalfox.app.audio.GeminiHandoffHelper
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
    var showInlineKeyEditor by remember { mutableStateOf(false) }

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
                    text = "Hallo! Ich bin dein Vocalfox Tutor (${selectedCefr.name}). Wollen wir über '$selectedScenario' auf Deutsch sprechen?",
                    translation = if (isIt) "Ciao! Sono il tuo tutor Vocalfox (${selectedCefr.name}). Parliamo di '$selectedScenario' in tedesco?" else "Hello! I am your Vocalfox tutor. Shall we speak German?",
                    grammarCorrection = ""
                )
            } else {
                TutorChatMessage(
                    isUser = false,
                    text = "¡Hola! Soy tu tutor Vocalfox (${selectedCefr.name}). ¿Hablamos sobre '$selectedScenario' en español?",
                    translation = if (isIt) "Ciao! Sono il tuo tutor Vocalfox (${selectedCefr.name}). Parliamo di '$selectedScenario' in spagnolo?" else "Hello! I am your Vocalfox tutor. Shall we speak Spanish?",
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
            errorMessage = if (isIt) "Inserisci una API Key oppure tocca 'Parla su Gemini' in alto per usare l'app Gemini gratis." else "Enter an API Key or tap 'Open Gemini' above to use the official Gemini app."
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
            .imePadding()
            .padding(horizontal = 20.dp)
    ) {
        Spacer(modifier = Modifier.height(10.dp))

        // Top Header + Pulsante diretto App Google Gemini + Pulsante API Key
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "Live AI · ${currentPack.languageName.get(systemLang)} (${selectedCefr.name})",
                    style = VocalFoxType.PageTitle,
                    color = colors.primaryText
                )
                Text(
                    text = if (isIt) "Chatta qui o apri Gemini Live vocale" else "Chat here or open Gemini Live voice",
                    style = VocalFoxType.SecondaryCaption,
                    color = colors.secondaryText
                )
            }

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Pulsante Diretto App Google Gemini (Zero API Key richiesta!)
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(14.dp))
                        .background(colors.accent)
                        .clickable {
                            GeminiHandoffHelper.launchGeminiAppWithPrompt(
                                context = context,
                                targetLanguageCode = currentPack.languageCode,
                                cefrLevel = selectedCefr,
                                systemLang = systemLang,
                                topic = selectedScenario
                            )
                        }
                        .padding(horizontal = 12.dp, vertical = 9.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Outlined.AutoAwesome,
                        contentDescription = null,
                        tint = colors.onAccent,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = if (isIt) "Parla su Gemini" else "Open Gemini",
                        style = VocalFoxType.BodyMedium,
                        color = colors.onAccent
                    )
                }

                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(colors.card)
                        .border(1.dp, if (showInlineKeyEditor) colors.accent else colors.hairline, CircleShape)
                        .clickable { showInlineKeyEditor = !showInlineKeyEditor },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Outlined.Key, contentDescription = "API Key", tint = colors.secondaryText, modifier = Modifier.size(18.dp))
                }
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
                    text = if (isIt) "Chiave API Google Gemini (Opzionale per chat interna)" else "Google Gemini API Key (Optional for in-app chat)",
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
                            text = if (isIt) "Vocalfox sta rispondendo..." else "Vocalfox is replying...",
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(6.dp)) }
        }

        // FIX 1: Barra di input posizionata subito sopra la bottomBar dello Scaffold (senza i 104.dp di vuoto!)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp, bottom = 10.dp),
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
                        text = if (currentPack.languageCode == "de") "Scrivi un messaggio in tedesco..." else "Scrivi un messaggio in spagnolo...",
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
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/OnboardingAndLessonScreens.kt": """\
package com.vocalfox.app.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
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
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.SlowMotionVideo
import androidx.compose.material.icons.outlined.Stop
import androidx.compose.material.icons.outlined.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.vocalfox.app.audio.GeminiHandoffHelper
import com.vocalfox.app.audio.PhonemeAccuracyStatus
import com.vocalfox.app.audio.PronunciationResult
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.GrammarSyntaxExercise
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.domain.model.WritingExercise
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.AnimatedWebpSplashPlayer
import com.vocalfox.app.ui.theme.MascotPedagogicalBanner
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.theme.VocalFoxWordmark

data class GuidedUnitBundle(
    val unitIndex: Int,
    val cefr: CefrLevel,
    val chapterBadge: String = "",
    val title: String,
    val subtitle: String,
    val durationMinutes: Int,
    val tintColor: Color,
    val mascotPose: MascotState,
    val grammarExercise: GrammarSyntaxExercise,
    val writingExercise: WritingExercise,
    val pronunciationDrill: PronunciationDrill
)

@Composable
fun SplashScreenOverlay(
    onFinished: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .clickable { onFinished() },
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            AnimatedWebpSplashPlayer(size = 240.dp)
            VocalFoxWordmark(height = 44.dp)
        }
    }
}

@Composable
fun OnboardingScreen(
    allPacks: Map<String, LanguagePack>,
    selectedLangCode: String,
    systemLang: SystemLang,
    strings: UiStrings,
    onSelectSystemLang: (SystemLang) -> Unit,
    onSelectTargetLang: (String) -> Unit,
    onCompleteOnboarding: (CefrLevel) -> Unit
) {
    val colors = VocalFoxTheme.colors
    var inPlacementMode by remember { mutableStateOf(false) }
    var questionIdx by remember { mutableIntStateOf(0) }
    var correctCount by remember { mutableIntStateOf(0) }

    val pack = allPacks[selectedLangCode] ?: allPacks.values.first()
    val placementQuestions = remember(pack.languageCode) {
        CefrLevel.entries.mapNotNull { lvl ->
            pack.grammarExercises.firstOrNull { it.cefr == lvl }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .navigationBarsPadding()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        VocalFoxWordmark(height = 34.dp)

        if (!inPlacementMode) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(VocalFoxPalette.TintWarmAmber)
                    .padding(20.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                VocalFoxMascot(state = MascotState.LOGO_IDLE, size = 84.dp)
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = strings.onboardingWelcomeTitle,
                        style = VocalFoxType.SectionTitle,
                        color = VocalFoxPalette.FoxDeepInkBrown
                    )
                    Text(
                        text = strings.onboardingWelcomeSub,
                        style = VocalFoxType.SecondaryCaption,
                        color = VocalFoxPalette.FoxDeepInkBrown.copy(alpha = 0.8f)
                    )
                }
            }

            Text(
                text = strings.chooseUiLanguageLabel,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                SystemLang.entries.forEach { lang ->
                    val active = lang == systemLang
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (active) colors.accent else colors.card)
                            .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                            .clickable { onSelectSystemLang(lang) }
                            .padding(vertical = 14.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = lang.displayName,
                            style = VocalFoxType.BodyMedium,
                            color = if (active) colors.onAccent else colors.primaryText
                        )
                    }
                }
            }

            Text(
                text = strings.chooseTargetLanguageLabel,
                style = VocalFoxType.BodyMedium,
                color = colors.primaryText
            )
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                allPacks.values.forEach { p ->
                    val isSelected = p.languageCode == selectedLangCode
                    val flagBadge = when (p.languageCode) {
                        "es" -> "ES · Español (200 Unità A1–B2)"
                        "de" -> "DE · Deutsch (200 Unità A1–B2)"
                        else -> p.languageCode.uppercase()
                    }
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (isSelected) colors.card else colors.raised)
                            .border(
                                width = if (isSelected) 2.dp else 1.dp,
                                color = if (isSelected) colors.accent else colors.hairline,
                                shape = RoundedCornerShape(14.dp)
                            )
                            .clickable { onSelectTargetLang(p.languageCode) }
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = p.languageName.get(systemLang),
                                style = VocalFoxType.SectionTitle,
                                color = colors.primaryText
                            )
                            Text(
                                text = flagBadge,
                                style = VocalFoxType.MetaMono,
                                color = colors.secondaryText
                            )
                        }
                        if (isSelected) {
                            Box(
                                modifier = Modifier
                                    .size(28.dp)
                                    .clip(CircleShape)
                                    .background(colors.accent),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.Check,
                                    contentDescription = null,
                                    tint = colors.onAccent,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }
                    }
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.accent)
                    .clickable { onCompleteOnboarding(CefrLevel.A1) }
                    .padding(18.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = strings.startFromScratchTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.onAccent
                    )
                    Text(
                        text = strings.startFromScratchSub,
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.onAccent.copy(alpha = 0.9f)
                    )
                }
                Icon(
                    imageVector = Icons.Outlined.ArrowForward,
                    contentDescription = null,
                    tint = colors.onAccent
                )
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                    .clickable {
                        questionIdx = 0
                        correctCount = 0
                        inPlacementMode = true
                    }
                    .padding(18.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = strings.takePlacementTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Text(
                        text = strings.takePlacementSub,
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }
                Icon(
                    imageVector = Icons.Outlined.ArrowForward,
                    contentDescription = null,
                    tint = colors.accent
                )
            }
        } else {
            val currentQ = placementQuestions.getOrNull(questionIdx)
            if (currentQ != null) {
                val options = remember(currentQ.id) {
                    (listOf(currentQ.blankTarget) + currentQ.distractors).shuffled()
                }
                Text(
                    text = "${strings.placementHeader} (${questionIdx + 1}/${placementQuestions.size})",
                    style = VocalFoxType.MetaMono,
                    color = colors.accent
                )
                LinearProgressIndicator(
                    progress = { (questionIdx + 1).toFloat() / placementQuestions.size.coerceAtLeast(1) },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp)
                        .clip(RoundedCornerShape(4.dp)),
                    color = colors.accent,
                    trackColor = colors.raised
                )

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                        .padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Text(
                        text = currentQ.title.get(systemLang),
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                    Text(
                        text = currentQ.promptSentence,
                        style = VocalFoxType.SentenceDisplay,
                        color = colors.primaryText
                    )

                    options.forEach { opt ->
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(colors.raised)
                                .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                                .clickable {
                                    if (opt == currentQ.blankTarget) {
                                        correctCount++
                                    }
                                    if (questionIdx + 1 < placementQuestions.size) {
                                        questionIdx++
                                    } else {
                                        val assigned = when (correctCount) {
                                            0, 1 -> CefrLevel.A1
                                            2 -> CefrLevel.A2
                                            3 -> CefrLevel.B1
                                            else -> CefrLevel.B2
                                        }
                                        onCompleteOnboarding(assigned)
                                    }
                                }
                                .padding(16.dp)
                        ) {
                            Text(
                                text = opt,
                                style = VocalFoxType.BodyMedium,
                                color = colors.primaryText
                            )
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun GuidedLessonScreen(
    bundle: GuidedUnitBundle,
    systemLang: SystemLang,
    strings: UiStrings,
    isRecording: Boolean,
    pronunciationResult: PronunciationResult?,
    onSpeakText: (String, Float) -> Unit,
    onStartRecording: (PronunciationDrill) -> Unit,
    onStopAndEvaluate: (PronunciationDrill) -> Unit,
    onCompleteUnit: (GuidedUnitBundle, Int) -> Unit,
    onClose: () -> Unit
) {
    val context = LocalContext.current
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT
    var currentStep by remember(bundle.unitIndex) { mutableIntStateOf(0) } // 0..5

    val animatedProgress by animateFloatAsState(
        targetValue = (currentStep + 1) / 6f,
        animationSpec = tween(300),
        label = "lesson_progress"
    )

    val micPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) onStartRecording(bundle.pronunciationDrill)
        else onStopAndEvaluate(bundle.pronunciationDrill)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .navigationBarsPadding()
            .padding(horizontal = 20.dp, vertical = 14.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(colors.raised)
                    .clickable(onClick = onClose),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Outlined.Close,
                    contentDescription = null,
                    tint = colors.primaryText,
                    modifier = Modifier.size(20.dp)
                )
            }

            LinearProgressIndicator(
                progress = { animatedProgress },
                modifier = Modifier
                    .weight(1f)
                    .height(10.dp)
                    .clip(RoundedCornerShape(5.dp)),
                color = colors.accent,
                trackColor = colors.raised
            )

            Text(
                text = "${(currentStep + 1).coerceAtMost(5)}/5",
                style = VocalFoxType.MetaMono,
                color = colors.secondaryText
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        AnimatedContent(
            targetState = currentStep,
            transitionSpec = {
                fadeIn(animationSpec = tween(220)) togetherWith fadeOut(animationSpec = tween(180))
            },
            modifier = Modifier.weight(1f),
            label = "step_transition"
        ) { step ->
            when (step) {
                // STEP 0: Vocabulary & Concept Discovery
                0 -> {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = "${bundle.cefr.name} · Unità ${bundle.unitIndex + 1} · ${strings.stepLearnWords}",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Text(
                            text = bundle.title,
                            style = VocalFoxType.PageTitle,
                            color = colors.primaryText
                        )
                        Text(
                            text = strings.tapWordToListenHint,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )

                        bundle.grammarExercise.syntaxTokens.forEach { token ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(16.dp))
                                    .background(colors.card)
                                    .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                    .clickable { onSpeakText(token.surface, 1.0f) }
                                    .padding(18.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(
                                    modifier = Modifier.weight(1f),
                                    verticalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    Text(
                                        text = token.surface,
                                        style = VocalFoxType.SentenceDisplay,
                                        color = colors.primaryText
                                    )
                                    Text(
                                        text = token.gloss.get(systemLang),
                                        style = VocalFoxType.Body,
                                        color = colors.secondaryText
                                    )
                                }
                                Box(
                                    modifier = Modifier
                                        .size(44.dp)
                                        .clip(CircleShape)
                                        .background(VocalFoxPalette.TintWarmAmber),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = null,
                                        tint = VocalFoxPalette.FoxFurOrangeDark
                                    )
                                }
                            }
                        }

                        MascotPedagogicalBanner(
                            state = MascotState.THINKING,
                            title = if (isIt) "Regola chiave" else "Key rule",
                            subtitle = bundle.grammarExercise.explanation.get(systemLang)
                        )

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = strings.continueButton,
                            onClick = { currentStep = 1 }
                        )
                    }
                }

                // STEP 1: Multiple-Choice Quiz (Zero TTS Spoiler)
                1 -> {
                    val ex = bundle.grammarExercise
                    val options = remember(ex.id) {
                        (listOf(ex.blankTarget) + ex.distractors).shuffled()
                    }
                    var picked by remember(ex.id) { mutableStateOf<String?>(null) }
                    var verified by remember(ex.id) { mutableStateOf(false) }
                    val isRight = picked == ex.blankTarget

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = strings.stepQuizChoice,
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Text(
                            text = strings.tapOptionToHearHint,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Text(
                                text = ex.promptSentence.replace("___", picked ?: " _____ "),
                                style = VocalFoxType.SentenceDisplay,
                                color = colors.primaryText
                            )

                            options.forEach { option ->
                                val selected = picked == option
                                val borderCol = when {
                                    verified && option == ex.blankTarget -> colors.positive
                                    verified && selected && !isRight -> colors.negative
                                    selected -> colors.accent
                                    else -> colors.hairline
                                }
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(if (selected) colors.raised else colors.background)
                                        .border(2.dp, borderCol, RoundedCornerShape(12.dp))
                                        .clickable {
                                            picked = option
                                            verified = false
                                            onSpeakText(option, 1.0f)
                                        }
                                        .padding(16.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = option,
                                        style = VocalFoxType.BodyMedium,
                                        color = colors.primaryText
                                    )
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = null,
                                        tint = colors.mutedText,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                            }
                        }

                        if (verified) {
                            MascotPedagogicalBanner(
                                state = if (isRight) MascotState.CELEBRATE else MascotState.STRICT_COACH,
                                title = if (isRight) "Corretto" else ex.blankTarget,
                                subtitle = ex.explanation.get(systemLang)
                            )
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!verified) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!verified && picked != null) {
                                    verified = true
                                    onSpeakText(ex.promptSentence.replace("___", ex.blankTarget), 1.0f)
                                } else if (verified) {
                                    currentStep = 2
                                }
                            }
                        )
                    }
                }

                // STEP 2: Meaning & Inflection Comprehension Check
                2 -> {
                    val tokens = bundle.grammarExercise.syntaxTokens
                    val targetToken = tokens.firstOrNull()
                    val correctMeaning = targetToken?.gloss?.get(systemLang).orEmpty()
                    val distractorMeanings = remember(bundle.unitIndex) {
                        val otherGlosses = tokens.drop(1).map { it.gloss.get(systemLang) }
                        val defaults = if (isIt) listOf("Ieri sera tardi", "Domani pomeriggio") else listOf("Late last night", "Tomorrow afternoon")
                        (listOf(correctMeaning) + otherGlosses + defaults).distinct().take(4).shuffled()
                    }
                    var pickedMeaning by remember(bundle.unitIndex) { mutableStateOf<String?>(null) }
                    var verifiedMeaning by remember(bundle.unitIndex) { mutableStateOf(false) }

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = if (isIt) "Passo 3 · Riconosci il significato" else "Step 3 · Meaning check",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .clickable { onSpeakText(targetToken?.surface.orEmpty(), 1.0f) }
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Text(
                                text = if (isIt) "Cosa significa questa espressione?" else "What does this expression mean?",
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.secondaryText
                            )
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Icon(Icons.Outlined.VolumeUp, null, tint = colors.accent)
                                Text(
                                    text = targetToken?.surface.orEmpty(),
                                    style = VocalFoxType.PageTitle,
                                    color = colors.primaryText
                                )
                            }
                        }

                        distractorMeanings.forEach { mOpt ->
                            val selected = pickedMeaning == mOpt
                            val borderCol = when {
                                verifiedMeaning && mOpt == correctMeaning -> colors.positive
                                verifiedMeaning && selected && mOpt != correctMeaning -> colors.negative
                                selected -> colors.accent
                                else -> colors.hairline
                            }
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(if (selected) colors.raised else colors.card)
                                    .border(2.dp, borderCol, RoundedCornerShape(12.dp))
                                    .clickable {
                                        pickedMeaning = mOpt
                                        verifiedMeaning = false
                                    }
                                    .padding(16.dp)
                            ) {
                                Text(mOpt, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                            }
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!verifiedMeaning) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!verifiedMeaning && pickedMeaning != null) {
                                    verifiedMeaning = true
                                } else if (verifiedMeaning) {
                                    currentStep = 3
                                }
                            }
                        )
                    }
                }

                // STEP 3: FIX 2 — Interactive Sentence Builder with Per-Word Green/Red Outline
                3 -> {
                    val wrt = bundle.writingExercise
                    val targetSentence = wrt.referenceTargets.firstOrNull().orEmpty()
                    val allWords = remember(wrt.id) {
                        targetSentence
                            .replace(".", "")
                            .replace(",", "")
                            .replace("¿", "")
                            .replace("?", "")
                            .split(" ")
                            .filter { it.isNotBlank() }
                            .ifEmpty { bundle.grammarExercise.scrambleTokens }
                    }
                    val shuffledBank = remember(wrt.id) { allWords.shuffled() }
                    val selectedWords = remember(wrt.id) { mutableStateListOf<String>() }
                    var checked by remember(wrt.id) { mutableStateOf(false) }

                    val builtRight = selectedWords.size == allWords.size &&
                        selectedWords.indices.all { idx ->
                            selectedWords[idx].equals(allWords[idx], ignoreCase = true)
                        }

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = if (isIt) "Passo 4 · Componi la frase" else "Step 4 · Build the sentence",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )
                        Text(
                            text = strings.buildSentenceInstruction,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(18.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = wrt.sourcePrompt.get(systemLang),
                                style = VocalFoxType.SentenceDisplay,
                                color = colors.primaryText
                            )
                        }

                        // Assembled Sentence Area: Green outline for right word in right slot, Red for wrong slot
                        FlowRow(
                            modifier = Modifier
                                .fillMaxWidth()
                                .heightIn(min = 104.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.raised)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            selectedWords.forEachIndexed { index, w ->
                                val isWordAtPosCorrect = checked &&
                                    allWords.getOrNull(index)?.equals(w, ignoreCase = true) == true

                                val tileBorderColor = when {
                                    !checked -> colors.accent
                                    isWordAtPosCorrect -> colors.positive
                                    else -> colors.negative
                                }
                                val tileBgColor = when {
                                    !checked -> colors.card
                                    isWordAtPosCorrect -> colors.positive.copy(alpha = 0.12f)
                                    else -> colors.negative.copy(alpha = 0.12f)
                                }
                                val tileTextColor = when {
                                    !checked -> colors.primaryText
                                    isWordAtPosCorrect -> colors.positive
                                    else -> colors.negative
                                }

                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(tileBgColor)
                                        .border(2.dp, tileBorderColor, RoundedCornerShape(10.dp))
                                        .clickable {
                                            selectedWords.removeAt(index)
                                            checked = false
                                        }
                                        .padding(horizontal = 12.dp, vertical = 8.dp)
                                ) {
                                    Text(
                                        text = w,
                                        style = VocalFoxType.BodyMedium,
                                        color = tileTextColor
                                    )
                                }
                            }
                        }

                        // Shuffled Word Bank
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            shuffledBank.forEach { word ->
                                val alreadyUsed = selectedWords.count { it == word } >= allWords.count { it == word }
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(if (alreadyUsed) colors.raised else colors.card)
                                        .border(1.dp, colors.hairline, RoundedCornerShape(10.dp))
                                        .clickable(enabled = !alreadyUsed) {
                                            selectedWords.add(word)
                                            checked = false
                                            onSpeakText(word, 1.0f)
                                        }
                                        .padding(horizontal = 14.dp, vertical = 10.dp)
                                ) {
                                    Text(
                                        text = word,
                                        style = VocalFoxType.BodyMedium,
                                        color = if (alreadyUsed) colors.mutedText else colors.primaryText
                                    )
                                }
                            }
                        }

                        if (checked) {
                            MascotPedagogicalBanner(
                                state = if (builtRight) MascotState.CELEBRATE else MascotState.STRICT_COACH,
                                title = if (builtRight) {
                                    if (isIt) "Frase perfetta!" else "Perfect sentence!"
                                } else {
                                    targetSentence
                                },
                                subtitle = if (builtRight) {
                                    wrt.jitFeedback.get(systemLang)
                                } else {
                                    if (isIt) {
                                        "Le parole in verde sono al posto giusto, quelle in rosso vanno spostate. Tocca una parola per correggerla o premi Continua."
                                    } else {
                                        "Green words are in the right spot, red ones need adjustment. Tap a word to fix it or press Continue."
                                    }
                                }
                            )
                        }

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = if (!checked) strings.checkButton else strings.continueButton,
                            onClick = {
                                if (!checked && selectedWords.isNotEmpty()) {
                                    checked = true
                                    onSpeakText(targetSentence, 1.0f)
                                } else if (checked) {
                                    currentStep = 4
                                }
                            }
                        )
                    }
                }

                // STEP 4: Final Pronunciation & Shadowing
                4 -> {
                    val drill = bundle.pronunciationDrill
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = if (isIt) "Passo 5 · Ascolta e pronuncia" else "Step 5 · Listen & speak aloud",
                            style = VocalFoxType.MetaMono,
                            color = colors.accent
                        )

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(colors.card)
                                .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
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
                                        .clickable { onSpeakText(drill.targetSentence, 1.0f) }
                                        .padding(vertical = 12.dp),
                                    horizontalArrangement = Arrangement.Center,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Outlined.VolumeUp, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(strings.listenNormal, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                                }
                                Row(
                                    modifier = Modifier
                                        .weight(1f)
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(colors.raised)
                                        .clickable { onSpeakText(drill.targetSentence, 0.75f) }
                                        .padding(vertical = 12.dp),
                                    horizontalArrangement = Arrangement.Center,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Outlined.SlowMotionVideo, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(strings.listenSlow, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                                }
                            }

                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(14.dp))
                                    .background(if (isRecording) colors.negative else colors.accent)
                                    .clickable {
                                        if (isRecording) {
                                            onStopAndEvaluate(drill)
                                        } else {
                                            val granted = ContextCompat.checkSelfPermission(
                                                context,
                                                Manifest.permission.RECORD_AUDIO
                                            ) == PackageManager.PERMISSION_GRANTED
                                            if (granted) onStartRecording(drill)
                                            else micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                                        }
                                    }
                                    .padding(vertical = 16.dp),
                                horizontalArrangement = Arrangement.Center,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = if (isRecording) Icons.Outlined.Stop else Icons.Outlined.Mic,
                                    contentDescription = null,
                                    tint = colors.onAccent
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = if (isRecording) strings.stopListening else strings.tapToSpeak,
                                    style = VocalFoxType.BodyMedium,
                                    color = colors.onAccent
                                )
                            }
                        }

                        if (pronunciationResult != null) {
                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                pronunciationResult.wordFeedbacks.forEach { wf ->
                                    val col = when (wf.status) {
                                        PhonemeAccuracyStatus.ACCURATE -> colors.positive
                                        PhonemeAccuracyStatus.STRESS_OR_PITCH -> colors.warning
                                        PhonemeAccuracyStatus.MISPRONOUNCED -> colors.negative
                                    }
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(10.dp))
                                            .background(colors.card)
                                            .border(2.dp, col, RoundedCornerShape(10.dp))
                                            .clickable { onSpeakText(wf.word, 0.85f) }
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

                        MascotPedagogicalBanner(
                            state = if ((pronunciationResult?.overallScore ?: 0) >= 80) MascotState.CELEBRATE else MascotState.LOGO_IDLE,
                            title = if (pronunciationResult != null) "${pronunciationResult.overallScore}%" else bundle.cefr.name,
                            subtitle = drill.articulatoryTip.get(systemLang)
                        )

                        Spacer(modifier = Modifier.weight(1f))

                        PrimaryBottomButton(
                            text = strings.finishUnitButton,
                            onClick = {
                                onCompleteUnit(bundle, pronunciationResult?.overallScore ?: 95)
                                currentStep = 5
                            }
                        )
                    }
                }

                // STEP 5: Celebratory Completion Screen + Direct Handoff to Google Gemini App
                else -> {
                    val langCode = if (bundle.grammarExercise.id.startsWith("de")) "de" else "es"
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        VocalFoxMascot(
                            state = MascotState.CELEBRATE,
                            size = 150.dp,
                            tintBackground = VocalFoxPalette.TintSoftGold
                        )
                        Spacer(modifier = Modifier.height(20.dp))
                        Text(
                            text = strings.unitCompletedTitle,
                            style = VocalFoxType.PageTitle,
                            color = colors.primaryText
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = strings.unitCompletedSubtitle,
                            style = VocalFoxType.Body,
                            color = colors.secondaryText
                        )
                        Spacer(modifier = Modifier.height(24.dp))

                        // Pulsante per continuare a praticare l'argomento della lezione nell'app Google Gemini
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(14.dp))
                                .background(colors.card)
                                .border(1.5.dp, colors.accent, RoundedCornerShape(14.dp))
                                .clickable {
                                    GeminiHandoffHelper.launchGeminiAppWithPrompt(
                                        context = context,
                                        targetLanguageCode = langCode,
                                        cefrLevel = bundle.cefr,
                                        systemLang = systemLang,
                                        topic = bundle.title
                                    )
                                }
                                .padding(vertical = 14.dp, horizontal = 16.dp),
                            horizontalArrangement = Arrangement.Center,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.AutoAwesome,
                                contentDescription = null,
                                tint = colors.accent,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = if (isIt) "Pratica '${bundle.title}' su Gemini Live" else "Practice '${bundle.title}' on Gemini Live",
                                style = VocalFoxType.BodyMedium,
                                color = colors.accent
                            )
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        PrimaryBottomButton(
                            text = strings.continueButton,
                            onClick = onClose
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun PrimaryBottomButton(
    text: String,
    onClick: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(colors.accent)
            .clickable(onClick = onClick)
            .padding(vertical = 16.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = VocalFoxType.SectionTitle,
            color = colors.onAccent
        )
    }
}
"""
}


def find_project_root() -> Path | None:
    candidates = [
        Path(__file__).resolve().parent,
        Path.cwd(),
    ]
    for base in list(candidates):
        if base.exists():
            for child in base.iterdir():
                if child.is_dir():
                    candidates.append(child)

    for folder in candidates:
        if (folder / "settings.gradle.kts").exists():
            return folder
    return None


def main() -> None:
    root = find_project_root()
    if root is None:
        print("[ERRORE] Non riesco a trovare settings.gradle.kts!")
        return

    print(f"[Vocalfox Patch] Applicazione fix su:\n  {root}\n")

    for rel_path, content in FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  + Aggiornato: {rel_path}")

    print("\n========================================================")
    print("PATCH APPLICATA CON SUCCESSO!")
    print("Esegui ora:")
    print("========================================================\n")
    print(f'cd "{root}"')
    print("git add -A")
    print('git commit -m "Fix chat input bottom spacing, add green/red word bank outlines & Gemini app handoff"')
    print("git push origin main")


if __name__ == "__main__":
    main()