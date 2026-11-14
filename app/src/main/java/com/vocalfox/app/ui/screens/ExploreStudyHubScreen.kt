package com.vocalfox.app.ui.screens

import androidx.compose.animation.AnimatedContent
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Quiz
import androidx.compose.material.icons.outlined.SlowMotionVideo
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
import androidx.compose.ui.unit.dp
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.MascotPedagogicalBanner
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType

data class GrammarStudyCard(
    val category: String, // "VERBS", "PRONOUNS", "ADJECTIVES", "PHRASES"
    val title: String,
    val levelBadge: String,
    val whenToUse: String,
    val tableRows: List<Pair<String, String>>, // Target form (spoken on tap) -> Translation/Explanation
    val exampleSentence: String,
    val exampleTranslation: String,
    val quizPrompt: String,
    val quizCorrect: String,
    val quizOptions: List<String>
)

/**
 * Complete Grammar & Vocabulary Academy ("Esplora / Studio"):
 * 1. Verbi & Coniugazioni (Essere, Avere, Modali, Tempi verbali, Congiuntivo/Konjunktiv II)
 * 2. Pronomi (Soggetto, Oggetto Diretto/Indiretto, Riflessivi, Possessivi e posizione nella frase)
 * 3. Aggettivi, Articoli & Casi (Concordanza, Comparativi, Casi tedeschi Nominativ/Akkusativ/Dativ/Genitiv)
 * 4. Frasario & Suoni Speciali (Pronuncia, regole fonetiche e frasi chiave con audio 1.0x e 0.75x)
 */
@Composable
fun ExploreStudyHubScreen(
    currentPack: LanguagePack,
    systemLang: SystemLang,
    strings: UiStrings,
    onPlayAudio: (String, Float) -> Unit
) {
    val colors = VocalFoxTheme.colors
    val isItalian = systemLang == SystemLang.IT

    val tabs = listOf(
        "VERBS" to (if (isItalian) "Verbi" else "Verbs"),
        "PRONOUNS" to (if (isItalian) "Pronomi" else "Pronouns"),
        "ADJECTIVES" to (if (isItalian) "Aggettivi e Articoli" else "Adjectives & Cases"),
        "PHRASES" to (if (isItalian) "Frasario e Suoni" else "Phrases & Sounds")
    )

    var selectedTab by remember { mutableStateOf("VERBS") }
    var activeQuizCard by remember { mutableStateOf<GrammarStudyCard?>(null) }

    val allStudyCards = remember(currentPack.languageCode, systemLang) {
        buildStudyCardsForLanguage(currentPack.languageCode, isItalian)
    }
    val filteredCards = allStudyCards.filter { it.category == selectedTab }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp)
    ) {
        Spacer(modifier = Modifier.height(12.dp))
        Text(
            text = if (isItalian) "Accademia · ${currentPack.languageName.get(systemLang)}" else "Study Hub · ${currentPack.languageName.get(systemLang)}",
            style = VocalFoxType.PageTitle,
            color = colors.primaryText
        )
        Text(
            text = if (isItalian) "Verbi, pronomi, aggettivi, regole d'uso ed esempi vocali interattivi" else "Verbs, pronouns, adjectives, usage rules, and spoken examples",
            style = VocalFoxType.SecondaryCaption,
            color = colors.secondaryText
        )

        Spacer(modifier = Modifier.height(14.dp))

        // 4 Category Pill Tabs
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            tabs.forEach { (code, label) ->
                val active = selectedTab == code
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(14.dp))
                        .background(if (active) colors.accent else colors.card)
                        .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(14.dp))
                        .clickable {
                            selectedTab = code
                            activeQuizCard = null
                        }
                        .padding(horizontal = 16.dp, vertical = 10.dp)
                ) {
                    Text(
                        text = label,
                        style = VocalFoxType.BodyMedium,
                        color = if (active) colors.onAccent else colors.primaryText
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Interactive Quick-Quiz Modal Banner if user tapped "Fai un test su questo argomento"
        val quiz = activeQuizCard
        if (quiz != null) {
            var pickedAnswer by remember(quiz.title) { mutableStateOf<String?>(null) }
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(colors.card)
                    .border(2.dp, colors.accent, RoundedCornerShape(20.dp))
                    .padding(18.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Test rapido · ${quiz.title}",
                        style = VocalFoxType.SectionTitle,
                        color = colors.accent
                    )
                    Text(
                        text = if (isItalian) "Chiudi" else "Close",
                        style = VocalFoxType.MetaMono,
                        color = colors.secondaryText,
                        modifier = Modifier.clickable { activeQuizCard = null }
                    )
                }

                Text(
                    text = quiz.quizPrompt,
                    style = VocalFoxType.SentenceDisplay,
                    color = colors.primaryText
                )

                quiz.quizOptions.forEach { opt ->
                    val isSelected = pickedAnswer == opt
                    val isCorrect = opt == quiz.quizCorrect
                    val borderCol = when {
                        pickedAnswer != null && isCorrect -> colors.positive
                        isSelected && !isCorrect -> colors.negative
                        else -> colors.hairline
                    }
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isSelected) colors.raised else colors.background)
                            .border(1.5.dp, borderCol, RoundedCornerShape(12.dp))
                            .clickable {
                                pickedAnswer = opt
                                onPlayAudio(opt, 1.0f)
                            }
                            .padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(opt, style = VocalFoxType.BodyMedium, color = colors.primaryText)
                        if (pickedAnswer != null && isCorrect) {
                            Icon(Icons.Outlined.CheckCircle, null, tint = colors.positive, modifier = Modifier.size(18.dp))
                        }
                    }
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
        }

        // Scrollable Grammar & Vocabulary Cards
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(filteredCards) { card ->
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(20.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(20.dp))
                        .padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = card.title,
                            style = VocalFoxType.SectionTitle,
                            color = colors.primaryText,
                            modifier = Modifier.weight(1f)
                        )
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(VocalFoxPalette.TintWarmAmber)
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = card.levelBadge,
                                style = VocalFoxType.MetaMono,
                                color = VocalFoxPalette.FoxFurOrangeDark
                            )
                        }
                    }

                    // "Quando e come usarlo" explanation
                    Text(
                        text = card.whenToUse,
                        style = VocalFoxType.Body,
                        color = colors.secondaryText
                    )

                    // Conjugation / Pronoun / Case Table Rows (Each row speaks on tap!)
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(colors.raised)
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        card.tableRows.forEach { (targetForm, meaning) ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(colors.card)
                                    .clickable { onPlayAudio(targetForm, 1.0f) }
                                    .padding(horizontal = 12.dp, vertical = 10.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                    modifier = Modifier.weight(1f)
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.VolumeUp,
                                        contentDescription = null,
                                        tint = colors.accent,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Text(
                                        text = targetForm,
                                        style = VocalFoxType.BodyMedium,
                                        color = colors.primaryText
                                    )
                                }
                                Text(
                                    text = meaning,
                                    style = VocalFoxType.SecondaryCaption,
                                    color = colors.secondaryText
                                )
                            }
                        }
                    }

                    // Real Example Sentence with 1.0x and 0.75x Audio
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.background)
                            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(2.dp)
                        ) {
                            Text(
                                text = card.exampleSentence,
                                style = VocalFoxType.BodyMedium,
                                color = colors.primaryText
                            )
                            Text(
                                text = card.exampleTranslation,
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.secondaryText
                            )
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(CircleShape)
                                    .background(colors.raised)
                                    .clickable { onPlayAudio(card.exampleSentence, 1.0f) },
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Outlined.VolumeUp, null, tint = colors.primaryText, modifier = Modifier.size(18.dp))
                            }
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(CircleShape)
                                    .background(colors.raised)
                                    .clickable { onPlayAudio(card.exampleSentence, 0.75f) },
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Outlined.SlowMotionVideo, null, tint = colors.accent, modifier = Modifier.size(18.dp))
                            }
                        }
                    }

                    // Practice Quiz Button for this specific grammar card
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.accent.copy(alpha = 0.12f))
                            .clickable { activeQuizCard = card }
                            .padding(vertical = 10.dp),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Outlined.Quiz, null, tint = colors.accent, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = if (isItalian) "Fai un test rapido su questo argomento" else "Take a quick quiz on this topic",
                            style = VocalFoxType.BodyMedium,
                            color = colors.accent
                        )
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(110.dp)) }
        }
    }
}

private fun buildStudyCardsForLanguage(langCode: String, isIt: Boolean): List<GrammarStudyCard> {
    return if (langCode == "de") {
        listOf(
            // TEDESCO - VERBI
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Sein (Essere) e Haben (Avere)" else "Sein (To be) & Haben (To have)",
                levelBadge = "A1 · Base",
                whenToUse = if (isIt) "I due verbi fondamentali del tedesco. Servono sia da soli al presente sia come ausiliari per formare il passato (Perfekt)." else "The two core German verbs, used standalone and as auxiliaries in the past tense.",
                tableRows = listOf(
                    "ich bin / ich habe" to (if (isIt) "io sono / io ho" else "I am / I have"),
                    "du bist / du hast" to (if (isIt) "tu sei / tu hai" else "you are / you have"),
                    "er, sie, es ist / hat" to (if (isIt) "lui, lei è / ha" else "he, she, it is / has"),
                    "wir sind / wir haben" to (if (isIt) "noi siamo / noi abbiamo" else "we are / we have"),
                    "ihr seid / ihr habt" to (if (isIt) "voi siete / voi avete" else "you all are / have"),
                    "sie, Sie sind / haben" to (if (isIt) "loro sono, Lei è / hanno, ha" else "they, You are / have")
                ),
                exampleSentence = "Ich bin aus Italien und habe zwei Brüder.",
                exampleTranslation = if (isIt) "Sono italiano e ho due fratelli." else "I am from Italy and have two brothers.",
                quizPrompt = "Wir ___ heute sehr glücklich und ___ viel Zeit.",
                quizCorrect = "sind / haben",
                quizOptions = listOf("sind / haben", "seid / habt", "ist / hat")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Verbi Modali (Können, Müssen, Möchten, Wollen)" else "Modal Verbs (Können, Müssen, Möchten, Wollen)",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "Il verbo modale va sempre al 2° posto (V2), mentre il secondo verbo all'infinito va in fondo alla frase." else "Place the modal verb in 2nd position and the infinitive verb at the very end.",
                tableRows = listOf(
                    "ich kann / wir können" to (if (isIt) "posso / possiamo (capacità o possibilità)" else "I can / we can"),
                    "ich muss / wir müssen" to (if (isIt) "devo / dobbiamo (obbligo o necessità)" else "I must / we must"),
                    "ich möchte / wir möchten" to (if (isIt) "vorrei / vorremmo (desiderio cortese)" else "I would like / we would like"),
                    "ich will / wir wollen" to (if (isIt) "voglio / vogliamo (intenzione decisa)" else "I want / we want")
                ),
                exampleSentence = "Ich möchte gern einen Kaffee trinken.",
                exampleTranslation = if (isIt) "Vorrei bere volentieri un caffè." else "I would like to drink a coffee.",
                quizPrompt = "Morgen ___ ich früh aufstehen.",
                quizCorrect = "muss",
                quizOptions = listOf("muss", "müssen", "musst")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Passato Parlato (Perfekt) e Präteritum" else "Spoken Past (Perfekt) & Narrative Past",
                levelBadge = "A2–B1",
                whenToUse = if (isIt) "Nel parlato si usa il Perfekt (haben/sein + participio in fondo). Con sein, haben e i verbi modali si usa invece il Präteritum (war, hatte, musste, konnte)." else "Use Perfekt for spoken German, and Präteritum (war, hatte, musste, konnte) for auxiliaries and modals.",
                tableRows = listOf(
                    "ich habe gelernt / gemacht" to (if (isIt) "ho studiato / ho fatto" else "I studied / I made"),
                    "ich bin gefahren / gegangen" to (if (isIt) "sono andato (verbi di moto -> sein)" else "I traveled / I went"),
                    "ich war / ich hatte" to (if (isIt) "ero, sono stato / avevo, ho avuto" else "I was / I had"),
                    "ich musste / ich konnte" to (if (isIt) "ho dovuto / ho potuto" else "I had to / I was able to")
                ),
                exampleSentence = "Gestern bin ich mit dem Zug nach München gefahren.",
                exampleTranslation = if (isIt) "Ieri sono andato a Monaco in treno." else "Yesterday I traveled to Munich by train.",
                quizPrompt = "Letzte Woche ___ wir ins Theater gegangen.",
                quizCorrect = "sind",
                quizOptions = listOf("sind", "haben", "waren")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Konjunktiv II (Cortesia e Ipotesi Irreali)" else "Konjunktiv II (Politeness & Hypotheticals)",
                levelBadge = "B1–B2",
                whenToUse = if (isIt) "Si usa per richieste gentili (Könnten Sie...?), consigli (An deiner Stelle würde ich...) e periodi ipotetici (Wenn ich Zeit hätte...)." else "Used for polite requests, advice, and counterfactual conditions.",
                tableRows = listOf(
                    "ich wäre / wir wären" to (if (isIt) "sarei / saremmo" else "I would be / we would be"),
                    "ich hätte / wir hätten" to (if (isIt) "avrei / avremmo" else "I would have / we would have"),
                    "ich würde + infinito" to (if (isIt) "farei (condizionale presente)" else "I would do"),
                    "ich könnte / ich sollte" to (if (isIt) "potrei / dovrei (consiglio)" else "I could / I should")
                ),
                exampleSentence = "Wenn ich mehr Zeit hätte, würde ich jeden Tag Sport machen.",
                exampleTranslation = if (isIt) "Se avessi più tempo, farei sport ogni giorno." else "If I had more time, I would exercise every day.",
                quizPrompt = "___ Sie mir bitte kurz helfen?",
                quizCorrect = "Könnten",
                quizOptions = listOf("Könnten", "Konnten", "Kannst")
            ),

            // TEDESCO - PRONOMI
            GrammarStudyCard(
                category = "PRONOUNS",
                title = if (isIt) "Pronomi Personali: Nominativo, Accusativo e Dativo" else "Personal Pronouns: Nominative, Accusative & Dative",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Usa il Nominativo per il soggetto, l'Accusativo per l'oggetto diretto (chi/che cosa?) e il Dativo per il destinatario (a chi?) o dopo mit, bei, zu, helfen, danken." else "Nominative for subject, Accusative for direct object, Dative for recipient or after mit, zu, helfen.",
                tableRows = listOf(
                    "ich -> mich (Akk.) -> mir (Dat.)" to (if (isIt) "io -> mi (oggetto) -> a me" else "I -> me -> to me"),
                    "du -> dich (Akk.) -> dir (Dat.)" to (if (isIt) "tu -> ti (oggetto) -> a te" else "you -> you -> to you"),
                    "er -> ihn (Akk.) -> ihm (Dat.)" to (if (isIt) "lui -> lo -> a lui (gli)" else "he -> him -> to him"),
                    "sie -> sie (Akk.) -> ihr (Dat.)" to (if (isIt) "lei -> la -> a lei (le)" else "she -> her -> to her"),
                    "wir -> uns (Akk.) -> uns (Dat.)" to (if (isIt) "noi -> ci / a noi" else "we -> us / to us"),
                    "Sie -> Sie (Akk.) -> Ihnen (Dat.)" to (if (isIt) "Lei -> La -> a Lei (formale)" else "You -> You -> to You")
                ),
                exampleSentence = "Kannst du mir bitte sagen, wo ich ihn finde?",
                exampleTranslation = if (isIt) "Puoi dirmi (Dat.) per favore dove lo (Akk.) trovo?" else "Can you tell me where I can find him?",
                quizPrompt = "Wie geht es ___ heute? Danke, es geht mir gut.",
                quizCorrect = "dir",
                quizOptions = listOf("dir", "dich", "du")
            ),
            GrammarStudyCard(
                category = "PRONOUNS",
                title = if (isIt) "Pronomi Riflessivi e Possessivi (mein, dein, sein, ihr)" else "Reflexive & Possessive Pronouns",
                levelBadge = "A2–B1",
                whenToUse = if (isIt) "I possessivi (mein, dein, sein, ihr, unser) prendono le stesse desinenze di 'ein/eine/einen'. I riflessivi cambiano solo alla 1ª e 2ª persona (mich, dich, sich)." else "Possessives take the endings of 'ein/eine/einen'. Reflexives use mich, dich, sich.",
                tableRows = listOf(
                    "mein Vater / meine Mutter" to (if (isIt) "mio padre (masc.) / mia madre (femm.)" else "my father / my mother"),
                    "sein Buch / ihr Auto" to (if (isIt) "il libro di lui / l'auto di lei" else "his book / her car"),
                    "ich freue mich / du freust dich" to (if (isIt) "io mi rallegro / tu ti rallegri" else "I am glad / you are glad"),
                    "er, sie freut sich / wir freuen uns" to (if (isIt) "lui/lei si rallegra / noi ci rallegriamo" else "he/she is glad / we are glad")
                ),
                exampleSentence = "Wir treffen uns heute Abend mit unseren Freunden.",
                exampleTranslation = if (isIt) "Ci incontriamo stasera con i nostri amici." else "We are meeting tonight with our friends.",
                quizPrompt = "Er wäscht ___ vor dem Essen die Hände.",
                quizCorrect = "sich",
                quizOptions = listOf("sich", "ihn", "ihm")
            ),

            // TEDESCO - AGGETTIVI E ARTICOLI
            GrammarStudyCard(
                category = "ADJECTIVES",
                title = if (isIt) "Declinazione degli Articoli nei 4 Casi (der, die, das)" else "Article Declension across the 4 Cases",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "In tedesco l'articolo cambia per mostrare la funzione nella frase: nell'Accusativo cambia SOLO il maschile (der -> den). Nel Dativo diventano dem (m/n), der (f), den + n (pl)." else "In Accusative only masculine changes (der -> den). In Dative: dem (m/n), der (f), den+n (pl).",
                tableRows = listOf(
                    "Nominativ: der (m) · die (f) · das (n) · die (pl)" to (if (isIt) "Soggetto della frase" else "Subject"),
                    "Akkusativ: den (m) · die (f) · das (n) · die (pl)" to (if (isIt) "Oggetto diretto / moto a luogo" else "Direct object"),
                    "Dativ: dem (m) · der (f) · dem (n) · den -n (pl)" to (if (isIt) "Termine / stato in luogo / mit, zu" else "Indirect object / location"),
                    "Genitiv: des -s (m/n) · der (f/pl)" to (if (isIt) "Possesso (di...) / trotz, während" else "Possession / during, despite")
                ),
                exampleSentence = "Ich gebe dem Kellner den Schlüssel für das Zimmer.",
                exampleTranslation = if (isIt) "Do al cameriere (Dat.) la chiave (Akk.) per la stanza." else "I give the waiter (Dat.) the key (Acc.) for the room.",
                quizPrompt = "Ich trinke gern einen Kaffee mit ___ warmen Milch (die Milch, femm.).",
                quizCorrect = "der",
                quizOptions = listOf("der", "die", "dem")
            ),
            GrammarStudyCard(
                category = "ADJECTIVES",
                title = if (isIt) "Aggettivi, Comparativi (-er) e Superlativi (am ...-sten)" else "Adjectives, Comparatives & Superlatives",
                levelBadge = "A2–B2",
                whenToUse = if (isIt) "Il comparativo si forma sempre aggiungendo -er all'aggettivo (schnell -> schneller als). Molti aggettivi corti prendono anche l'Umlaut (alt -> älter, groß -> größer, gut -> besser)." else "Add -er + als for comparatives (schneller als) and am ...-sten for superlatives.",
                tableRows = listOf(
                    "schnell -> schneller als -> am schnellsten" to (if (isIt) "veloce -> più veloce di -> il più veloce" else "fast -> faster than -> fastest"),
                    "groß -> größer als -> am größten" to (if (isIt) "grande -> più grande di -> il più grande" else "big -> bigger than -> biggest"),
                    "gut -> besser als -> am besten" to (if (isIt) "buono/bene -> migliore di -> il migliore" else "good -> better than -> best"),
                    "viel -> mehr als -> am meisten" to (if (isIt) "molto -> più di -> il massimo" else "much -> more than -> most")
                ),
                exampleSentence = "Der Zug ist heute viel schneller und bequemer als das Auto.",
                exampleTranslation = if (isIt) "Il treno oggi è molto più veloce e comodo dell'auto." else "The train is much faster and more comfortable than the car today.",
                quizPrompt = "Dieser Wein schmeckt mir ___ als der andere.",
                quizCorrect = "besser",
                quizOptions = listOf("besser", "guter", "am besten")
            ),

            // TEDESCO - FRASARIO E SUONI
            GrammarStudyCard(
                category = "PHRASES",
                title = if (isIt) "Regole di Pronuncia Tedesca (ä, ö, ü, ch, sch, sp, st, z)" else "German Pronunciation Rules",
                levelBadge = "A1–B2",
                whenToUse = if (isIt) "La pronuncia tedesca è regolarissima: una volta imparate queste combinazioni saprai leggere ad alta voce qualsiasi parola." else "German spelling is completely regular once you know these core letter combinations.",
                tableRows = listOf(
                    "ei = [ai] · ie = [ii lunga]" to (if (isIt) "mein (main) vs sieben (ziiben)" else "mein vs sieben"),
                    "eu / äu = [oi]" to (if (isIt) "heute (hoite), Häuser (hoiser)" else "heute, Häuser"),
                    "sch = [sc] · sp / st = [shp / sht]" to (if (isIt) "schule, sprechen, Straße" else "Schule, sprechen, Straße"),
                    "ch dopo i/e/ä/ö/ü = dolce [ç]" to (if (isIt) "ich, möchte, Bücher" else "ich, möchte, Bücher"),
                    "ch dopo a/o/u/au = aspirata [x]" to (if (isIt) "nach, acht, Buch, auch" else "nach, acht, Buch, auch")
                ),
                exampleSentence = "Heute sprechen wir über fünf schöne Bücher.",
                exampleTranslation = if (isIt) "Oggi parliamo di cinque bei libri." else "Today we are talking about five nice books.",
                quizPrompt = "Come si legge il dittongo 'eu' nella parola 'heute' (oggi)?",
                quizCorrect = "Come 'oi' (hoite)",
                quizOptions = listOf("Come 'oi' (hoite)", "Come 'eu' italiana", "Come 'au'")
            )
        )
    } else {
        listOf(
            // SPAGNOLO - VERBI
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Ser vs Estar (I due verbi 'Essere')" else "Ser vs Estar (The two 'To be' verbs)",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "Usa SER per identità, origine, professione, ora e caratteristiche permanenti. Usa ESTAR per posizione geografica/fisica, stati d'animo e condizioni temporanee (está abierto/cerrado)." else "Use SER for identity, origin, time, and permanent traits. Use ESTAR for location and temporary states.",
                tableRows = listOf(
                    "yo soy / yo estoy" to (if (isIt) "io sono (identità) / io sono, sto (luogo/stato)" else "I am (identity) / I am (location/state)"),
                    "tú eres / tú estás" to (if (isIt) "tu sei / tu stai" else "you are"),
                    "él, ella, usted es / está" to (if (isIt) "lui, lei, Lei è / si trova, sta" else "he, she, you formal is"),
                    "nosotros somos / estamos" to (if (isIt) "noi siamo / noi ci troviamo, stiamo" else "we are"),
                    "ellos, ustedes son / están" to (if (isIt) "loro sono / loro si trovano, stanno" else "they, you plural are")
                ),
                exampleSentence = "Soy de Milán, pero hoy estoy en Barcelona por trabajo.",
                exampleTranslation = if (isIt) "Sono di Milano, ma oggi mi trovo a Barcellona per lavoro." else "I am from Milan, but today I am in Barcelona for work.",
                quizPrompt = "La farmacia ___ al final de esta calle, pero ahora ___ cerrada.",
                quizCorrect = "está / está",
                quizOptions = listOf("está / está", "es / está", "es / es")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Tener (Possesso) vs Haber (Ausiliare e 'Hay')" else "Tener (To have) vs Haber (Auxiliary & Hay)",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "TENER significa 'possedere' o 'avere fame/sete/anni'. HABER (he, has, ha, hemos, han) si usa SOLO davanti a un participio passato (-ado/-ido), più la forma speciale 'HAY' (c'è / ci sono)." else "Use TENER for possession and age/hunger. Use HABER only as auxiliary before participles, plus HAY (there is/are).",
                tableRows = listOf(
                    "tengo, tienes, tiene, tenemos, tienen" to (if (isIt) "possiedo, ho (un'auto, fame, 25 anni)" else "I have, you have (possession)"),
                    "he, has, ha, hemos, habéis, han + -ado/-ido" to (if (isIt) "ho parlato (he hablado), abbiamo mangiato (hemos comido)" else "have spoken, have eaten"),
                    "hay (invariabile singolare e plurale)" to (if (isIt) "c'è / ci sono (Hay un problema / Hay dos mesas)" else "there is / there are"),
                    "tener que + infinito" to (if (isIt) "dover fare qualcosa (Tengo que salir = Devo uscire)" else "have to do something")
                ),
                exampleSentence = "Hoy he tenido mucho trabajo y ahora tengo hambre.",
                exampleTranslation = if (isIt) "Oggi ho avuto (he tenido) molto lavoro e ora ho (tengo) fame." else "Today I have had a lot of work and now I am hungry.",
                quizPrompt = "Esta mañana nosotros ___ desayunado en el bar porque ___ mucha prisa.",
                quizCorrect = "hemos / teníamos",
                quizOptions = listOf("hemos / teníamos", "tenemos / hemos", "hay / tenemos")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Verbi Fondamentali Irregolari (Ir, Querer, Poder, Hacer, Decir)" else "Essential Irregular Verbs (Ir, Querer, Poder, Hacer, Decir)",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Questi 5 verbi coprono oltre il 60% delle conversazioni quotidiane in spagnolo. Nota i verbi che dittongano la vocale (e -> ie in querer, o -> ue in poder)." else "These 5 verbs cover over 60% of daily Spanish conversation.",
                tableRows = listOf(
                    "Ir (andare): voy, vas, va, vamos, van" to (if (isIt) "Passato: fui, fuiste, fue, fuimos, fueron" else "Past: fui, fuiste, fue, fuimos"),
                    "Querer (volere): quiero, quieres, quiere, queremos" to (if (isIt) "Passato: quise, quisiste, quiso" else "Past: quise, quisiste, quiso"),
                    "Poder (potere): puedo, puedes, puede, podemos" to (if (isIt) "Passato: pude, pudiste, pudo" else "Past: pude, pudiste, pudo"),
                    "Hacer (fare): hago, haces, hace, hacemos" to (if (isIt) "Passato: hice, hiciste, hizo, hicimos" else "Past: hice, hiciste, hizo"),
                    "Decir (dire): digo, dices, dice, decimos" to (if (isIt) "Passato: dije, dijiste, dijo, dijeron" else "Past: dije, dijiste, dijo")
                ),
                exampleSentence = "¿Puedes decirme qué quieres hacer este fin de semana?",
                exampleTranslation = if (isIt) "Puoi dirmi cosa vuoi fare questo fine settimana?" else "Can you tell me what you want to do this weekend?",
                quizPrompt = "Ayer yo ___ todo lo posible, pero no ___ llegar a tiempo.",
                quizCorrect = "hice / pude",
                quizOptions = listOf("hice / pude", "hago / puedo", "hacía / podía")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Congiuntivo (Subjuntivo) e Periodo Ipotetico" else "Subjunctive Mood & Conditionals",
                levelBadge = "B1–B2",
                whenToUse = if (isIt) "In spagnolo il congiuntivo si usa per desideri (quiero que...), opinioni negate (no creo que...), consigli e DOPO 'cuando' riferito al futuro (Cuando llegues, llámame). Per iverbi in -AR usa le vocali in -e, per -ER/-IR usa la -a." else "Swap the theme vowel (-AR takes -e; -ER/-IR takes -a). Used after 'cuando' for future events and 'no creo que'.",
                tableRows = listOf(
                    "Hablar -> hable, hables, hable, hablemos, hablen" to (if (isIt) "Verbi in -AR prendono la -E" else "-AR verbs take -E"),
                    "Comer / Vivir -> coma, comas / viva, vivas, vivan" to (if (isIt) "Verbi in -ER e -IR prendono la -A" else "-ER/-IR verbs take -A"),
                    "Irregolari: sea (ser), esté (estar), tenga (tener)" to (if (isIt) "vaya (ir), haga (hacer), pueda (poder), sepa (saber)" else "vaya, haga, pueda, sepa"),
                    "Imperfetto Cong. (B2): tuviera, fuera, pudiera" to (if (isIt) "Si usa dopo 'Si...' ipotetico (Si pudiera, iría)" else "Used in 'Si...' counterfactuals")
                ),
                exampleSentence = "Cuando tengas un minuto libre, avísame para que hablemos.",
                exampleTranslation = if (isIt) "Quando avrai (tengas) un minuto libero, avvisami affinché parliamo." else "When you have a free minute, let me know so we can talk.",
                quizPrompt = "Espero que ___ un buen viaje y que nos ___ pronto.",
                quizCorrect = "tengas / veamos",
                quizOptions = listOf("tengas / veamos", "tienes / vemos", "tendrás / veremos")
            ),

            // SPAGNOLO - PRONOMI
            GrammarStudyCard(
                category = "PRONOUNS",
                title = if (isIt) "Pronomi Soggetto, Oggetto Diretto (lo/la) e Indiretto (le/se)" else "Subject, Direct & Indirect Object Pronouns",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "I pronomi oggetto vanno PRIMA del verbo coniugato (Lo veo), ma si attaccano alla fine dell'infinito, gerundio e imperativo affermativo (Quiero verlo / ¡Dime!). Se 'le' incontra 'lo/la', diventa 'SE lo / SE la'." else "Place object pronouns before conjugated verbs, or attach them to infinitives and affirmative imperatives.",
                tableRows = listOf(
                    "yo -> me · tú -> te · nosotros -> nos" to (if (isIt) "Identici per oggetto diretto, indiretto e riflessivo" else "Same for direct, indirect & reflexive"),
                    "Oggetto Diretto (3ª p.): lo, la, los, las" to (if (isIt) "Lo compro (il libro) / Las invito (le amiche)" else "him, her, it, them"),
                    "Oggetto Indiretto (a chi?): le, les (-> se)" to (if (isIt) "Le doy el libro -> Se lo doy (Glielo do)" else "to him/her/them (shifts to 'se' before lo/la)"),
                    "Con preposizione: mí (conmigo), ti (contigo)" to (if (isIt) "Para mí, para ti,¿Vienes conmigo? (Vieni con me?)" else "for me, for you, with me, with you")
                ),
                exampleSentence = "Me pidió las llaves y se las entregué inmediatamente.",
                exampleTranslation = if (isIt) "Mi ha chiesto le chiavi e gliele (se las) ho consegnate subito." else "He asked me for the keys and I handed them to him immediately.",
                quizPrompt = "¿Le has enviado el correo a Ana? — Sí, ya ___ he enviado.",
                quizCorrect = "se lo",
                quizOptions = listOf("se lo", "le lo", "la lo")
            ),

            // SPAGNOLO - AGGETTIVI E ARTICOLI
            GrammarStudyCard(
                category = "ADJECTIVES",
                title = if (isIt) "Aggettivi, Possessivi, Dimostrativi e Comparativi" else "Adjectives, Possessives, Demonstratives & Comparatives",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "In spagnolo l'aggettivo qualificativo segue quasi sempre il sostantivo (un coche rápido). Attenzione all'articolo neutro 'LO + aggettivo' (lo importante = la cosa importante) e a 'muy' (molto + agg) vs 'mucho' (molto + nome/verbo)." else "Descriptive adjectives follow the noun. Use 'muy' before adjectives/adverbs and 'mucho/a/os/as' with nouns.",
                tableRows = listOf(
                    "Possessivi prima del nome: mi/mis, tu/tus, su/sus" to (if (isIt) "nuestro/a/os/as, vuestro/a/os/as (senza articolo!)" else "my, your, his/her, our (never use article)"),
                    "Dimostrativi: este (qui), ese (lì), aquel (laggiù)" to (if (isIt) "esta calle, ese edificio, aquellos años" else "this, that, that over there"),
                    "Molto: MUY + aggettivo/avverbio · MUCHO + nome" to (if (isIt) "Es muy fácil / Tengo mucha hambre / Trabaja mucho" else "muy fácil vs mucha hambre"),
                    "Comparativi: más ... que / menos ... que / tan ... como" to (if (isIt) "mejor que (migliore di), peor que, mayor/menor que" else "more...than, as...as, better/worse than")
                ),
                exampleSentence = "Lo más importante es que este proyecto es mejor que el anterior.",
                exampleTranslation = if (isIt) "La cosa più importante è che questo progetto è migliore del precedente." else "The most important thing is that this project is better than the previous one.",
                quizPrompt = "Hoy estoy ___ cansado porque ayer tuvimos ___ reuniones.",
                quizCorrect = "muy / muchas",
                quizOptions = listOf("muy / muchas", "mucho / muy", "muy / muchos")
            ),

            // SPAGNOLO - FRASARIO E SUONI
            GrammarStudyCard(
                category = "PHRASES",
                title = if (isIt) "Pronuncia Spagnola e Preposizioni Chiave (Por vs Para)" else "Spanish Pronunciation & Por vs Para",
                levelBadge = "A1–B2",
                whenToUse = if (isIt) "Ricorda: H è sempre muta; QU si legge 'ch' (quiero); GUE/GUI si leggono 'ghe/ghi'; CE/CI e Z hanno suono interdentale/sibilante; J e GE/GI sono aspirate di gola. Usa PARA per scopo/destinazione e POR per causa/mezzo/durata." else "H is silent; QU=[k]; J/GE/GI=[x]. Use PARA for goal/recipient/deadline and POR for cause/means/exchange.",
                tableRows = listOf(
                    "PARA: scopo, destinatario, destinazione, scadenza" to (if (isIt) "Estudio para aprender / Es para ti / Salgo para Madrid" else "in order to, for you, bound for"),
                    "POR: causa, motivo, mezzo, prezzo, parte del giorno" to (if (isIt) "Por la lluvia / Por teléfono / Por 20 euros / Por la mañana" else "because of, by phone, in the morning"),
                    "Suoni: que/qui = [ke/ki] · gue/gui = [ghe/ghi]" to (if (isIt) "queso, quiero, guitarra, guerra" else "queso, quiero, guitarra"),
                    "Suoni: ll = [gl/y] · ñ = [gn] · j/ge/gi = [kh]" to (if (isIt) "llave, mañana, viaje, gente" else "llave, mañana, viaje, gente")
                ),
                exampleSentence = "Te envío el contrato por correo electrónico para que lo firmes antes del viernes.",
                exampleTranslation = if (isIt) "Ti invio il contratto per email (mezzo -> por) affinché tu lo firmi (scopo -> para) entro venerdì." else "I am sending you the contract by email so that you sign it before Friday.",
                quizPrompt = "He comprado este regalo ___ tu cumpleaños y pagué treinta euros ___ él.",
                quizCorrect = "para / por",
                quizOptions = listOf("para / por", "por / para", "para / para")
            )
        )
    }
}
