package com.vocalfox.app.ui.screens

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
import com.vocalfox.app.ui.theme.VocalFoxPalette
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType

data class GrammarStudyCard(
    val category: String,
    val title: String,
    val levelBadge: String,
    val whenToUse: String,
    val tableRows: List<Pair<String, String>>,
    val exampleSentence: String,
    val exampleTranslation: String,
    val quizPrompt: String,
    val quizCorrect: String,
    val quizOptions: List<String>
)

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
        "ADJECTIVES" to (if (isItalian) "Aggettivi e Casi" else "Adjectives & Cases"),
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
        Spacer(modifier = Modifier.height(10.dp))
        Text(
            text = if (isItalian) "Accademia · ${currentPack.languageName.get(systemLang)}" else "Academy · ${currentPack.languageName.get(systemLang)}",
            style = VocalFoxType.PageTitle,
            color = colors.primaryText
        )
        Text(
            text = if (isItalian) "Tocca qualsiasi voce per ascoltare la pronuncia corretta" else "Tap any item to hear its pronunciation",
            style = VocalFoxType.SecondaryCaption,
            color = colors.secondaryText
        )

        Spacer(modifier = Modifier.height(12.dp))

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
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (active) colors.accent else colors.card)
                        .border(1.dp, if (active) colors.accent else colors.hairline, RoundedCornerShape(12.dp))
                        .clickable {
                            selectedTab = code
                            activeQuizCard = null
                        }
                        .padding(horizontal = 16.dp, vertical = 10.dp)
                ) {
                    Text(
                        text = label,
                        style = VocalFoxType.BodyMedium,
                        color = if (active) colors.onAccent else colors.primaryText,
                        maxLines = 1
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        val quiz = activeQuizCard
        if (quiz != null) {
            var pickedAnswer by remember(quiz.title) { mutableStateOf<String?>(null) }
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.card)
                    .border(2.dp, colors.accent, RoundedCornerShape(16.dp))
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = quiz.title,
                        style = VocalFoxType.SectionTitle,
                        color = colors.accent,
                        modifier = Modifier.weight(1f)
                    )
                    Text(
                        text = if (isItalian) "Chiudi" else "Close",
                        style = VocalFoxType.BodyMedium,
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

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(filteredCards) { card ->
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.card)
                        .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                        .padding(16.dp),
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
                        Spacer(modifier = Modifier.width(8.dp))
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

                    Text(
                        text = card.whenToUse,
                        style = VocalFoxType.Body,
                        color = colors.secondaryText
                    )

                    // TABELLA IMPAGINATA A LARGHEZZA PIENA (Zero testo verticale!)
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.raised)
                            .padding(10.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        card.tableRows.forEach { (targetForm, meaning) ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(colors.card)
                                    .clickable { onPlayAudio(targetForm.substringBefore("->").trim(), 1.0f) }
                                    .padding(horizontal = 14.dp, vertical = 10.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(
                                    modifier = Modifier.weight(1f),
                                    verticalArrangement = Arrangement.spacedBy(2.dp)
                                ) {
                                    Text(
                                        text = targetForm,
                                        style = VocalFoxType.BodyMedium,
                                        color = colors.primaryText
                                    )
                                    Text(
                                        text = meaning,
                                        style = VocalFoxType.SecondaryCaption,
                                        color = colors.secondaryText
                                    )
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Icon(
                                    imageVector = Icons.Outlined.VolumeUp,
                                    contentDescription = null,
                                    tint = colors.accent,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }
                    }

                    // Frase d'esempio con audio normale e lento
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
                        Spacer(modifier = Modifier.width(8.dp))
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

                    // Pulsante Test Rapido
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(10.dp))
                            .background(colors.accent.copy(alpha = 0.12f))
                            .clickable { activeQuizCard = card }
                            .padding(vertical = 10.dp),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Outlined.Quiz, null, tint = colors.accent, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = if (isItalian) "Fai un test rapido" else "Take a quick quiz",
                            style = VocalFoxType.BodyMedium,
                            color = colors.accent
                        )
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(24.dp)) }
        }
    }
}

private fun buildStudyCardsForLanguage(langCode: String, isIt: Boolean): List<GrammarStudyCard> {
    return if (langCode == "de") {
        listOf(
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Sein (Essere) e Haben (Avere)" else "Sein (To be) & Haben (To have)",
                levelBadge = "A1",
                whenToUse = if (isIt) "I due verbi cardine del tedesco. Si usano da soli al presente e come ausiliari per formare il passato." else "The two core German verbs, used standalone and as auxiliaries in the past tense.",
                tableRows = listOf(
                    "ich bin · ich habe" to (if (isIt) "io sono · io ho" else "I am · I have"),
                    "du bist · du hast" to (if (isIt) "tu sei · tu hai" else "you are · you have"),
                    "er/sie/es ist · hat" to (if (isIt) "lui/lei è · ha" else "he/she/it is · has"),
                    "wir sind · wir haben" to (if (isIt) "noi siamo · noi abbiamo" else "we are · we have"),
                    "ihr seid · ihr habt" to (if (isIt) "voi siete · voi avete" else "you all are · have"),
                    "sie/Sie sind · haben" to (if (isIt) "loro sono / Lei è · hanno / ha" else "they/You are · have")
                ),
                exampleSentence = "Ich bin aus Italien und habe zwei Brüder.",
                exampleTranslation = if (isIt) "Sono italiano e ho due fratelli." else "I am from Italy and have two brothers.",
                quizPrompt = "Wir ___ heute sehr glücklich und ___ viel Zeit.",
                quizCorrect = "sind / haben",
                quizOptions = listOf("sind / haben", "seid / habt", "ist / hat")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Verbi Modali (Können, Müssen, Möchten, Wollen)" else "Modal Verbs",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "Il verbo modale occupa il 2° posto nella frase, mentre il verbo all'infinito va sempre in fondo." else "Place the modal verb in 2nd position and the infinitive verb at the very end.",
                tableRows = listOf(
                    "ich kann · wir können" to (if (isIt) "posso · possiamo (capacità o possibilità)" else "I can · we can"),
                    "ich muss · wir müssen" to (if (isIt) "devo · dobbiamo (obbligo o necessità)" else "I must · we must"),
                    "ich möchte · wir möchten" to (if (isIt) "vorrei · vorremmo (desiderio cortese)" else "I would like · we would like"),
                    "ich will · wir wollen" to (if (isIt) "voglio · vogliamo (intenzione decisa)" else "I want · we want")
                ),
                exampleSentence = "Ich möchte gern einen Kaffee trinken.",
                exampleTranslation = if (isIt) "Vorrei bere volentieri un caffè." else "I would like to drink a coffee.",
                quizPrompt = "Morgen ___ ich früh aufstehen.",
                quizCorrect = "muss",
                quizOptions = listOf("muss", "müssen", "musst")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Passato Parlato (Perfekt) e Präteritum" else "Past Tenses (Perfekt & Präteritum)",
                levelBadge = "A2–B1",
                whenToUse = if (isIt) "Nel parlato si usa il Perfekt (haben/sein + participio in fondo). Con sein, haben e i modali si usa il Präteritum (war, hatte, musste, konnte)." else "Use Perfekt for spoken German, and Präteritum for auxiliaries and modals.",
                tableRows = listOf(
                    "ich habe gelernt · gemacht" to (if (isIt) "ho studiato · ho fatto" else "I studied · I made"),
                    "ich bin gefahren · gegangen" to (if (isIt) "sono andato (verbi di moto -> sein)" else "I traveled · I went"),
                    "ich war · ich hatte" to (if (isIt) "ero / sono stato · avevo / ho avuto" else "I was · I had"),
                    "ich musste · ich konnte" to (if (isIt) "ho dovuto · ho potuto" else "I had to · I could")
                ),
                exampleSentence = "Gestern bin ich mit dem Zug nach München gefahren.",
                exampleTranslation = if (isIt) "Ieri sono andato a Monaco in treno." else "Yesterday I traveled to Munich by train.",
                quizPrompt = "Letzte Woche ___ wir ins Theater gegangen.",
                quizCorrect = "sind",
                quizOptions = listOf("sind", "haben", "waren")
            ),
            GrammarStudyCard(
                category = "PRONOUNS",
                title = if (isIt) "Pronomi Personali (Nominativo, Accusativo, Dativo)" else "Personal Pronouns",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Nominativo per il soggetto, Accusativo per l'oggetto diretto e Dativo per il destinatario ('a chi?') o dopo mit, zu, helfen." else "Nominative for subject, Accusative for direct object, Dative for recipient.",
                tableRows = listOf(
                    "ich -> mich (Akk.) -> mir (Dat.)" to (if (isIt) "io -> mi (oggetto) -> a me" else "I -> me -> to me"),
                    "du -> dich (Akk.) -> dir (Dat.)" to (if (isIt) "tu -> ti (oggetto) -> a te" else "you -> you -> to you"),
                    "er -> ihn (Akk.) -> ihm (Dat.)" to (if (isIt) "lui -> lo -> a lui (gli)" else "he -> him -> to him"),
                    "sie -> sie (Akk.) -> ihr (Dat.)" to (if (isIt) "lei -> la -> a lei (le)" else "she -> her -> to her"),
                    "wir -> uns · Sie -> Ihnen (Dat.)" to (if (isIt) "noi -> ci · Lei -> a Lei" else "we -> us · You -> to You")
                ),
                exampleSentence = "Kannst du mir bitte sagen, wo ich ihn finde?",
                exampleTranslation = if (isIt) "Puoi dirmi per favore dove lo trovo?" else "Can you tell me where I can find him?",
                quizPrompt = "Wie geht es ___ heute? Danke, es geht mir gut.",
                quizCorrect = "dir",
                quizOptions = listOf("dir", "dich", "du")
            ),
            GrammarStudyCard(
                category = "ADJECTIVES",
                title = if (isIt) "Articoli e Casi (der, die, das)" else "Articles & Cases",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Nell'Accusativo cambia solo il maschile (der -> den). Nel Dativo diventano dem (maschile/neutro), der (femminile), den (plurale)." else "In Accusative only masculine changes (der -> den). In Dative: dem, der, den.",
                tableRows = listOf(
                    "Nominativ: der (m) · die (f) · das (n)" to (if (isIt) "Soggetto della frase" else "Subject"),
                    "Akkusativ: den (m) · die (f) · das (n)" to (if (isIt) "Oggetto diretto" else "Direct object"),
                    "Dativ: dem (m) · der (f) · dem (n)" to (if (isIt) "Termine / stato in luogo / dopo mit, zu" else "Indirect object / after mit, zu"),
                    "Genitiv: des (m/n) · der (f/pl)" to (if (isIt) "Possesso / dopo trotz, während" else "Possession / during, despite")
                ),
                exampleSentence = "Ich gebe dem Kellner den Schlüssel für das Zimmer.",
                exampleTranslation = if (isIt) "Do al cameriere la chiave per la stanza." else "I give the waiter the key for the room.",
                quizPrompt = "Ich trinke gern einen Kaffee mit ___ warmen Milch (die Milch, femm.).",
                quizCorrect = "der",
                quizOptions = listOf("der", "die", "dem")
            ),
            GrammarStudyCard(
                category = "PHRASES",
                title = if (isIt) "Regole di Pronuncia Tedesca" else "German Pronunciation Rules",
                levelBadge = "A1–B2",
                whenToUse = if (isIt) "Ecco le combinazioni chiave per leggere qualsiasi parola tedesca senza esitazioni." else "Core letter combinations to read any German word accurately.",
                tableRows = listOf(
                    "ei = [ai] · ie = [ii lunga]" to (if (isIt) "mein (main) · sieben (ziiben)" else "mein · sieben"),
                    "eu / äu = [oi]" to (if (isIt) "heute (hoite) · Häuser (hoiser)" else "heute · Häuser"),
                    "sch = [sc] · sp / st = [shp / sht]" to (if (isIt) "Schule · sprechen · Straße" else "Schule · sprechen · Straße"),
                    "ch dopo i/e/ä/ö/ü = dolce [ç]" to (if (isIt) "ich · möchte · Bücher" else "ich · möchte · Bücher")
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
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Ser vs Estar (I due verbi 'Essere')" else "Ser vs Estar",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "Usa SER per identità, origine, professione e ora. Usa ESTAR per posizione nello spazio e stati temporanei." else "Use SER for identity, origin, and time. Use ESTAR for location and temporary states.",
                tableRows = listOf(
                    "yo soy · yo estoy" to (if (isIt) "io sono (identità) · io mi trovo / sto" else "I am (identity) · I am (location)"),
                    "tú eres · tú estás" to (if (isIt) "tu sei · tu stai" else "you are"),
                    "él/ella es · está" to (if (isIt) "lui/lei è · si trova / sta" else "he/she is"),
                    "nosotros somos · estamos" to (if (isIt) "noi siamo · noi ci troviamo / stiamo" else "we are"),
                    "ellos son · están" to (if (isIt) "loro sono · loro si trovano / stanno" else "they are")
                ),
                exampleSentence = "Soy de Milán, pero hoy estoy en Barcelona por trabajo.",
                exampleTranslation = if (isIt) "Sono di Milano, ma oggi mi trovo a Barcellona per lavoro." else "I am from Milan, but today I am in Barcelona for work.",
                quizPrompt = "La farmacia ___ al final de esta calle, pero ahora ___ cerrada.",
                quizCorrect = "está / está",
                quizOptions = listOf("está / está", "es / está", "es / es")
            ),
            GrammarStudyCard(
                category = "VERBS",
                title = if (isIt) "Tener (Avere) vs Haber (Ausiliare e Hay)" else "Tener vs Haber & Hay",
                levelBadge = "A1–A2",
                whenToUse = if (isIt) "TENER indica possesso o fame/sete/età. HABER (he, has, ha, hemos) forma il passato prossimo, mentre HAY significa 'c'è / ci sono'." else "TENER for possession; HABER as auxiliary; HAY for 'there is / are'.",
                tableRows = listOf(
                    "tengo, tienes, tiene, tenemos" to (if (isIt) "ho, hai, ha, abbiamo (possesso)" else "I have, you have"),
                    "he, has, ha, hemos + participio" to (if (isIt) "ho parlato (he hablado), abbiamo mangiato" else "have spoken, have eaten"),
                    "hay (invariabile)" to (if (isIt) "c'è / ci sono (Hay dos mesas libres)" else "there is / there are"),
                    "tener que + infinito" to (if (isIt) "dover fare qualcosa (Tengo que salir)" else "have to do something")
                ),
                exampleSentence = "Hoy he tenido mucho trabajo y ahora tengo hambre.",
                exampleTranslation = if (isIt) "Oggi ho avuto molto lavoro e ora ho fame." else "Today I have had a lot of work and now I am hungry.",
                quizPrompt = "Esta mañana nosotros ___ desayunado en el bar porque ___ prisa.",
                quizCorrect = "hemos / teníamos",
                quizOptions = listOf("hemos / teníamos", "tenemos / hemos", "hay / tenemos")
            ),
            GrammarStudyCard(
                category = "PRONOUNS",
                title = if (isIt) "Pronomi Oggetto Diretto (lo/la) e Indiretto (le/se)" else "Direct & Indirect Object Pronouns",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "I pronomi vanno prima del verbo coniugato. Quando 'le' incontra 'lo/la', si trasforma in 'se' (Se lo doy = Glielo do)." else "Place pronouns before the verb. 'Le' becomes 'se' before 'lo/la'.",
                tableRows = listOf(
                    "me · te · nos" to (if (isIt) "mi · ti · ci (diretto, indiretto e riflessivo)" else "me · you · us"),
                    "lo, la, los, las" to (if (isIt) "lo, la, li, le (oggetto diretto)" else "him, her, it, them"),
                    "le, les (-> se lo / se la)" to (if (isIt) "gli, le, a loro (diventa 'se' davanti a lo/la)" else "to him/her/them"),
                    "conmigo · contigo" to (if (isIt) "con me · con te" else "with me · with you")
                ),
                exampleSentence = "Me pidió las llaves y se las entregué inmediatamente.",
                exampleTranslation = if (isIt) "Mi ha chiesto le chiavi e gliele ho consegnate subito." else "He asked me for the keys and I handed them to him immediately.",
                quizPrompt = "¿Le has enviado el correo a Ana? — Sí, ya ___ he enviado.",
                quizCorrect = "se lo",
                quizOptions = listOf("se lo", "le lo", "la lo")
            ),
            GrammarStudyCard(
                category = "ADJECTIVES",
                title = if (isIt) "Aggettivi, Possessivi e Muy vs Mucho" else "Adjectives, Possessives & Muy vs Mucho",
                levelBadge = "A1–B1",
                whenToUse = if (isIt) "Usa MUY davanti ad aggettivi e avverbi (muy bueno), e MUCHO/A/OS/AS davanti ai nomi o dopo i verbi (mucho tiempo)." else "Use MUY before adjectives/adverbs and MUCHO with nouns/verbs.",
                tableRows = listOf(
                    "mi/mis · tu/tus · su/sus" to (if (isIt) "mio/miei · tuo/tuoi · suo/suoi (senza articolo)" else "my · your · his/her"),
                    "muy + aggettivo / avverbio" to (if (isIt) "muy fácil, muy bien, muy tarde" else "very easy, very well"),
                    "mucho/a/os/as + sostantivo" to (if (isIt) "mucha agua, muchos amigos" else "a lot of water, many friends"),
                    "más ... que · mejor que" to (if (isIt) "più ... di · migliore di" else "more ... than · better than")
                ),
                exampleSentence = "Lo más importante es que este proyecto es mejor que el anterior.",
                exampleTranslation = if (isIt) "La cosa più importante è che questo progetto è migliore del precedente." else "The most important thing is that this project is better than the previous one.",
                quizPrompt = "Hoy estoy ___ cansado porque ayer tuvimos ___ reuniones.",
                quizCorrect = "muy / muchas",
                quizOptions = listOf("muy / muchas", "mucho / muy", "muy / muchos")
            ),
            GrammarStudyCard(
                category = "PHRASES",
                title = if (isIt) "Pronuncia Spagnola e Por vs Para" else "Pronunciation & Por vs Para",
                levelBadge = "A1–B2",
                whenToUse = if (isIt) "Usa PARA per scopo, destinatario e scadenza; usa POR per causa, mezzo e durata." else "Use PARA for goal/recipient/deadline; use POR for cause/means.",
                tableRows = listOf(
                    "PARA: scopo, destinatario, destinazione" to (if (isIt) "Estudio para aprender · Es para ti" else "in order to · for you"),
                    "POR: causa, mezzo, prezzo, parte del giorno" to (if (isIt) "Por la lluvia · Por teléfono · Por la mañana" else "because of · by phone"),
                    "que / qui = [che / chi] · gue / gui = [ghe / ghi]" to (if (isIt) "quiero, queso, guitarra" else "quiero, queso, guitarra"),
                    "ll = [gl / y] · ñ = [gn] · j = [kh]" to (if (isIt) "llave, mañana, viaje" else "llave, mañana, viaje")
                ),
                exampleSentence = "Te envío el contrato por correo electrónico para que lo firmes.",
                exampleTranslation = if (isIt) "Ti invio il contratto per email affinché tu lo firmi." else "I am sending you the contract by email so that you sign it.",
                quizPrompt = "He comprado este regalo ___ tu cumpleaños y pagué treinta euros ___ él.",
                quizCorrect = "para / por",
                quizOptions = listOf("para / por", "por / para", "para / para")
            )
        )
    }
}
