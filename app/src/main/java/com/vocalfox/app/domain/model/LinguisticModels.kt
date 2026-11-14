package com.vocalfox.app.domain.model

import com.vocalfox.app.ui.i18n.SystemLang
import kotlinx.serialization.Serializable

@Serializable
enum class CefrLevel {
    A1, A2, B1, B2
}

@Serializable
data class LocalizedText(
    val en: String,
    val it: String
) {
    fun get(lang: SystemLang): String = when (lang) {
        SystemLang.EN -> en
        SystemLang.IT -> it
    }
}

@Serializable
data class SyntaxToken(
    val surface: String,
    val roleCode: String, // e.g. "SUBJ", "V2", "V-END", "PART", "SUBJUNCTIVE", "OBJ", "CONN"
    val ipa: String,
    val gloss: LocalizedText
)

@Serializable
data class GrammarSyntaxExercise(
    val id: String,
    val cefr: CefrLevel,
    val title: LocalizedText,
    val promptSentence: String,
    val blankTarget: String,
    val distractors: List<String>,
    val scrambleTokens: List<String>,
    val syntaxTokens: List<SyntaxToken>,
    val explanation: LocalizedText
)

@Serializable
data class WritingExercise(
    val id: String,
    val cefr: CefrLevel,
    val sourcePrompt: LocalizedText,
    val referenceTargets: List<String>,
    val requiredMorphemes: List<String>,
    val grammarRuleTitle: LocalizedText,
    val jitFeedback: LocalizedText
)

@Serializable
data class PhonemeTarget(
    val grapheme: String,
    val ipa: String,
    val trapDescription: LocalizedText
)

@Serializable
data class PronunciationDrill(
    val id: String,
    val cefr: CefrLevel,
    val targetSentence: String,
    val furiganaOrReading: String = "",
    val fullIpa: String,
    val translation: LocalizedText,
    val criticalPhonemes: List<PhonemeTarget>,
    val articulatoryTip: LocalizedText
)

@Serializable
data class ScriptCardItem(
    val symbol: String,
    val scriptCategory: String, // "Hiragana", "Katakana", "Kanji N5-N2", "Phonetics"
    val readingOrFurigana: String,
    val romajiOrIpa: String,
    val meaning: LocalizedText,
    val exampleWord: String,
    val exampleReading: String,
    val strokeCount: Int
)

@Serializable
data class VoicePreset(
    val voiceId: String,
    val displayName: String,
    val gender: String,
    val timbre: String,
    val onnxFileName: String,
    val sampleRateHz: Int = 22050
)

@Serializable
data class LanguagePack(
    val languageCode: String,
    val languageName: LocalizedText,
    val availableVoices: List<VoicePreset>,
    val grammarExercises: List<GrammarSyntaxExercise>,
    val writingExercises: List<WritingExercise>,
    val pronunciationDrills: List<PronunciationDrill>,
    val scriptCards: List<ScriptCardItem>
)
