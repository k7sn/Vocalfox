package com.vocalfox.app.data.repository

import android.content.Context
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.GrammarSyntaxExercise
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.LocalizedText
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.domain.model.SyntaxToken
import com.vocalfox.app.domain.model.VoicePreset
import com.vocalfox.app.domain.model.WritingExercise
import kotlinx.serialization.json.Json

class PackLoader(private val context: Context) {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    fun loadAllLanguagePacks(): Map<String, LanguagePack> {
        val packs = linkedMapOf<String, LanguagePack>()
        val files = try {
            context.assets.list("packs")
                .orEmpty()
                .filter { it.endsWith("_pack.json") && !it.startsWith("ja") }
                .sorted()
        } catch (_: Throwable) {
            emptyList()
        }

        for (fileName in files) {
            try {
                val rawJson = context.assets.open("packs/$fileName").bufferedReader().use { it.readText() }
                val pack = json.decodeFromString<LanguagePack>(rawJson)
                if (pack.languageCode != "ja") {
                    packs[pack.languageCode] = pack
                }
            } catch (e: Throwable) {
                e.printStackTrace()
            }
        }

        if (packs.isEmpty()) {
            packs["es"] = createEmergencyPack()
        }
        return packs
    }

    companion object {
        fun createEmergencyPack(): LanguagePack = LanguagePack(
            languageCode = "es",
            languageName = LocalizedText("Spanish", "Spagnolo"),
            availableVoices = listOf(
                VoicePreset("es_ES-carlfm-high", "Carlos (Spagna)", "Maschile", "Calda e naturale", "es_ES-carlfm-high.onnx")
            ),
            grammarExercises = listOf(
                GrammarSyntaxExercise(
                    id = "fallback_es_a1",
                    cefr = CefrLevel.A1,
                    title = LocalizedText("Essence vs state (ser / estar)", "Essenza vs stato (ser / estar)"),
                    promptSentence = "La biblioteca central ___ cerrada hoy.",
                    blankTarget = "está",
                    distractors = listOf("es", "son", "están"),
                    scrambleTokens = listOf("La", "biblioteca", "está", "cerrada"),
                    syntaxTokens = listOf(
                        SyntaxToken("La biblioteca", "SUBJ", "la βiβljoˈteka", LocalizedText("Subject", "Soggetto")),
                        SyntaxToken("está", "VERB", "esˈta", LocalizedText("Estar 3rd sg", "Estar 3ª sg")),
                        SyntaxToken("cerrada", "OBJ", "θeˈraða", LocalizedText("Participle", "Participio"))
                    ),
                    explanation = LocalizedText(
                        "Use estar with past participles to express a resulting state.",
                        "Si usa estar con i participi passati per indicare uno stato risultante."
                    )
                )
            ),
            writingExercises = listOf(
                WritingExercise(
                    id = "fallback_es_wrt",
                    cefr = CefrLevel.A1,
                    sourcePrompt = LocalizedText("We want two coffees, please.", "Vorremmo due caffè, per favore."),
                    referenceTargets = listOf("Queremos dos cafés por favor"),
                    requiredMorphemes = listOf("queremos", "dos"),
                    grammarRuleTitle = LocalizedText("Present indicative", "Presente indicativo"),
                    jitFeedback = LocalizedText("Use 'queremos' for 1st person plural.", "Usa 'queremos' per la 1ª persona plurale.")
                )
            ),
            pronunciationDrills = listOf(
                PronunciationDrill(
                    id = "fallback_es_spk",
                    cefr = CefrLevel.A1,
                    targetSentence = "El perro corre rápido.",
                    fullIpa = "/el ˈpero ˈkore ˈrapiðo/",
                    translation = LocalizedText("The dog runs fast.", "Il cane corre veloce."),
                    criticalPhonemes = emptyList(),
                    articulatoryTip = LocalizedText("Trill the double rr against the alveolar ridge.", "Fai vibrare la doppia rr sugli alveoli.")
                )
            ),
            scriptCards = emptyList()
        )
    }
}
