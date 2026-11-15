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
