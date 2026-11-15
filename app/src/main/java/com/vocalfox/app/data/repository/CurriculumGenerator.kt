package com.vocalfox.app.data.repository

import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.GrammarSyntaxExercise
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.LocalizedText
import com.vocalfox.app.domain.model.PronunciationDrill
import com.vocalfox.app.domain.model.SyntaxToken
import com.vocalfox.app.domain.model.WritingExercise
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.screens.GuidedUnitBundle
import com.vocalfox.app.ui.theme.MascotState
import com.vocalfox.app.ui.theme.VocalFoxPalette

data class CurriculumSeed(
    val chapterTitleIt: String,
    val chapterTitleEn: String,
    val unitTitleIt: String,
    val unitTitleEn: String,
    val promptSentence: String,
    val blankTarget: String,
    val distractors: List<String>,
    val targetSentence: String,
    val translationIt: String,
    val translationEn: String,
    val ruleTipIt: String,
    val ruleTipEn: String,
    val tokens: List<Triple<String, String, String>>
)

object CurriculumGenerator {

    private val tints = listOf(
        VocalFoxPalette.TintWarmAmber,
        VocalFoxPalette.TintSoftGold,
        VocalFoxPalette.TintMintSage,
        VocalFoxPalette.TintCalmSky
    )

    private val poses = listOf(
        MascotState.LOGO_IDLE,
        MascotState.CELEBRATE,
        MascotState.THINKING,
        MascotState.STRICT_COACH
    )

    fun generate50UnitsForLevel(
        pack: LanguagePack,
        level: CefrLevel,
        systemLang: SystemLang
    ): List<GuidedUnitBundle> {
        val seeds = if (pack.languageCode == "de") {
            buildGerman50Seeds(level)
        } else {
            buildSpanish50Seeds(level)
        }

        return seeds.mapIndexed { idx, seed ->
            val unitId = "${pack.languageCode}_${level.name.lowercase()}_unit_${idx + 1}"
            val chapterPrefix = if (systemLang == SystemLang.IT) seed.chapterTitleIt else seed.chapterTitleEn
            val unitHeadline = if (systemLang == SystemLang.IT) seed.unitTitleIt else seed.unitTitleEn

            val syntaxTokens = seed.tokens.map { (surf, gIt, gEn) ->
                SyntaxToken(
                    surface = surf,
                    roleCode = level.name,
                    ipa = surf.lowercase(),
                    gloss = LocalizedText(en = gEn, it = gIt)
                )
            }

            val grammarEx = GrammarSyntaxExercise(
                id = unitId,
                cefr = level,
                title = LocalizedText(en = seed.unitTitleEn, it = seed.unitTitleIt),
                promptSentence = seed.promptSentence,
                blankTarget = seed.blankTarget,
                distractors = seed.distractors,
                scrambleTokens = seed.targetSentence
                    .replace(".", "")
                    .replace(",", "")
                    .replace("¿", "")
                    .replace("?", "")
                    .split(" ")
                    .filter { it.isNotBlank() },
                syntaxTokens = syntaxTokens,
                explanation = LocalizedText(en = seed.ruleTipEn, it = seed.ruleTipIt)
            )

            val writingEx = WritingExercise(
                id = "${unitId}_wrt",
                cefr = level,
                sourcePrompt = LocalizedText(en = seed.translationEn, it = seed.translationIt),
                referenceTargets = listOf(seed.targetSentence),
                requiredMorphemes = seed.targetSentence.split(" ").take(3),
                grammarRuleTitle = LocalizedText(en = seed.chapterTitleEn, it = seed.chapterTitleIt),
                jitFeedback = LocalizedText(en = seed.ruleTipEn, it = seed.ruleTipIt)
            )

            val speechDrill = PronunciationDrill(
                id = "${unitId}_spk",
                cefr = level,
                targetSentence = seed.targetSentence,
                furiganaOrReading = chapterPrefix,
                fullIpa = "",
                translation = LocalizedText(en = seed.translationEn, it = seed.translationIt),
                criticalPhonemes = emptyList(),
                articulatoryTip = LocalizedText(en = seed.ruleTipEn, it = seed.ruleTipIt)
            )

            GuidedUnitBundle(
                unitIndex = idx,
                cefr = level,
                chapterBadge = chapterPrefix,
                title = unitHeadline,
                subtitle = seed.targetSentence,
                durationMinutes = 3 + (idx % 3),
                tintColor = tints[idx % tints.size],
                mascotPose = poses[idx % poses.size],
                grammarExercise = grammarEx,
                writingExercise = writingEx,
                pronunciationDrill = speechDrill
            )
        }
    }

    private fun buildSpanish50Seeds(level: CefrLevel): List<CurriculumSeed> {
        val baseTemplates: List<CurriculumSeed> = when (level) {
            CefrLevel.A1 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Salutare al mattino", "Morning greetings", "Hola, buenos días. ¿Cómo ___ usted hoy?", "está", listOf("es", "soy", "están"), "Hola, buenos días. ¿Cómo está usted hoy?", "Ciao, buongiorno. Come sta Lei oggi?", "Hello, good morning. How are you today?", "Usa '¿Cómo está?' per chiedere come sta qualcuno.", "Use '¿Cómo está?' to ask how someone is feeling.", listOf(Triple("Buenos días", "Buongiorno", "Good morning"), Triple("¿Cómo está?", "Come sta?", "How are you?"), Triple("hoy", "oggi", "today"))),
                CurriculumSeed("Capitolo 1", "Chapter 1", "Dire il proprio nome", "Saying your name", "Mucho gusto, yo me ___ Alessandro.", "llamo", listOf("llamas", "llama", "soy"), "Mucho gusto, yo me llamo Alessandro.", "Piacere, io mi chiamo Alessandro.", "Nice to meet you, my name is Alessandro.", "Il verbo riflessivo 'llamarse' usa: me llamo, te llamas, se llama.", "The reflexive verb 'llamarse' uses: me llamo, te llamas, se llama.", listOf(Triple("Mucho gusto", "Molto piacere", "Nice to meet you"), Triple("yo me llamo", "io mi chiamo", "my name is"), Triple("encantado", "piacere", "delighted"))),
                CurriculumSeed("Capitolo 1", "Chapter 1", "Origine e nazionalità", "Origin & nationality", "Nosotros ___ de Italia, pero vivimos aquí.", "somos", listOf("estamos", "son", "soy"), "Nosotros somos de Italia, pero vivimos aquí.", "Noi siamo italiani, ma viviamo qui.", "We are from Italy, but we live here.", "Per nazionalità e origine si usa sempre 'ser' (soy, eres, es, somos).", "Always use 'ser' (soy, eres, es, somos) for origin and nationality.", listOf(Triple("Nosotros somos", "Noi siamo", "We are"), Triple("de Italia", "italiani / d'Italia", "from Italy"), Triple("vivimos aquí", "viviamo qui", "we live here"))),
                CurriculumSeed("Capitolo 1", "Chapter 1", "Posizione nello spazio", "Current location", "Mi hermana ___ en el centro de Madrid ahora.", "está", listOf("es", "estoy", "son"), "Mi hermana está en el centro de Madrid ahora.", "Mia sorella si trova nel centro di Madrid adesso.", "My sister is in the center of Madrid right now.", "Per indicare dove si trova una persona o un oggetto usa sempre 'estar'.", "Use 'estar' to state where someone or something is located.", listOf(Triple("Mi hermana", "Mia sorella", "My sister"), Triple("está en", "si trova a", "is in"), Triple("el centro", "il centro", "downtown"))),
                CurriculumSeed("Capitolo 1", "Chapter 1", "Ringraziare con cortesia", "Thanking politely", "Muchas gracias por tu ayuda. — De ___.", "nada", listOf("todo", "algo", "favor"), "Muchas gracias por tu ayuda. De nada.", "Molte grazie per il tuo aiuto. Di niente.", "Thank you very much for your help. You're welcome.", "'De nada' è la risposta naturale a 'Gracias'.", "'De nada' is the standard reply to 'Gracias'.", listOf(Triple("Muchas gracias", "Molte grazie", "Thank you very much"), Triple("por tu ayuda", "per il tuo aiuto", "for your help"), Triple("De nada", "Di niente / Prego", "You're welcome"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Il verbo Tener (Avere)", "Verb Tener (To have)", "Yo ___ dos hermanos y un perro muy simpático.", "tengo", listOf("tienes", "he", "soy"), "Yo tengo dos hermanos y un perro muy simpático.", "Io ho due fratelli e un cane molto simpatico.", "I have two brothers and a very friendly dog.", "Il possesso si esprime con 'tener' (tengo, tienes, tiene, tenemos).", "Express possession with 'tener' (tengo, tienes, tiene, tenemos).", listOf(Triple("Yo tengo", "Io ho", "I have"), Triple("dos hermanos", "due fratelli", "two brothers"), Triple("muy simpático", "molto simpatico", "very friendly"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "C'è e ci sono (Hay)", "There is & there are (Hay)", "En esta plaza ___ una farmacia y dos bancos.", "hay", listOf("está", "son", "tiene"), "En esta plaza hay una farmacia y dos bancos.", "In questa piazza c'è una farmacia e ci sono due banche.", "In this square there is a pharmacy and two banks.", "Usa 'hay' (invariabile) sia per 'c'è' sia per 'ci sono'.", "Use invariable 'hay' for both 'there is' and 'there are'.", listOf(Triple("En esta plaza", "In questa piazza", "In this square"), Triple("hay", "c'è / ci sono", "there is / are"), Triple("una farmacia", "una farmacia", "a pharmacy"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Articoli determinativi", "Definite articles", "___ libros de español están sobre la mesa.", "Los", listOf("El", "Las", "Unos"), "Los libros de español están sobre la mesa.", "I libri di spagnolo sono sul tavolo.", "The Spanish books are on the table.", "Il plurale di 'el' è 'los', mentre il plurale di 'la' è 'las'.", "The plural of masculine 'el' is 'los'; feminine 'la' becomes 'las'.", listOf(Triple("Los libros", "I libri", "The books"), Triple("están", "sono / si trovano", "are located"), Triple("sobre la mesa", "sul tavolo", "on the table"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Ordinare al ristorante", "Ordering at a restaurant", "Para empezar, yo ___ una ensalada mixta y agua sin gas.", "quiero", listOf("querer", "quieres", "quiere"), "Para empezar, yo quiero una ensalada mixta y agua sin gas.", "Per iniziare, vorrei un'insalata mista e acqua naturale.", "To start, I would like a mixed salad and still water.", "Il verbo 'querer' dittonga la 'e' in 'ie': quiero, quieres, quiere.", "'Querer' changes stem e -> ie in present: quiero, quieres, quiere.", listOf(Triple("Para empezar", "Per iniziare", "To start"), Triple("una ensalada", "un'insalata", "a salad"), Triple("agua sin gas", "acqua naturale", "still water"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "Chiedere indicazioni", "Asking for directions", "Disculpe, ¿dónde ___ la parada de metro más cercana?", "está", listOf("hay", "es", "son"), "Disculpe, ¿dónde está la parada de metro más cercana?", "Mi scusi, dov'è la fermata della metro più vicina?", "Excuse me, where is the nearest subway station?", "Con un luogo specifico preceduto da 'el / la' si usa sempre '¿dónde está?'.", "With a specific noun ('la parada'), always use '¿dónde está?'.", listOf(Triple("la parada de metro", "la fermata della metro", "the subway stop"), Triple("más cercana", "più vicina", "nearest"), Triple("todo recto", "sempre dritto", "straight ahead")))
            )
            CefrLevel.A2 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Esperienze recenti", "Recent experiences", "Esta semana nosotros ___ visitado dos exposiciones muy interesantes.", "hemos", listOf("habéis", "han", "tenemos"), "Esta semana nosotros hemos visitado dos exposiciones muy interesantes.", "Questa settimana abbiamo visitato due mostre molto interessanti.", "This week we have visited two very interesting exhibitions.", "Con 'hoy, esta semana' usa 'haber (he, has, ha, hemos) + participio'.", "Use 'haber + participle' with unfinished time frames like 'esta semana'.", listOf(Triple("Esta semana", "Questa settimana", "This week"), Triple("hemos visitado", "abbiamo visitato", "we have visited"), Triple("exposiciones", "mostre", "exhibitions"))),
                CurriculumSeed("Capitolo 1", "Chapter 1", "Raccontare ieri", "Talking about yesterday", "Anoche mis amigos ___ una paella deliciosa en casa.", "prepararon", listOf("preparan", "preparaban", "han preparado"), "Anoche mis amigos prepararon una paella deliciosa en casa.", "Ieri sera i miei amici hanno preparato una paella deliziosa a casa.", "Last night my friends cooked a delicious paella at home.", "Con 'ayer, anoche' usa il pretérito indefinido.", "Use the indefinido with completed past markers like 'anoche'.", listOf(Triple("Anoche", "Ieri sera", "Last night"), Triple("prepararon", "hanno preparato", "they prepared"), Triple("en casa", "a casa", "at home"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Pronomi oggetto diretto", "Direct object pronouns", "¿Has visto mis gafas? Sí, ___ vi sobre tu escritorio.", "las", listOf("los", "le", "la"), "Sí, las vi sobre tu escritorio.", "Sì, le ho viste sulla tua scrivania.", "Yes, I saw them on your desk.", "'Las' sostituisce un oggetto femminile plurale ('mis gafas').", "'Las' replaces a feminine plural direct object ('mis gafas').", listOf(Triple("mis gafas", "i miei occhiali", "my glasses"), Triple("las vi", "le ho viste", "I saw them"), Triple("tu escritorio", "la tua scrivania", "your desk"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Fare paragoni", "Making comparisons", "Este abrigo gris es más cálido ___ aquel negro.", "que", listOf("de", "como", "cual"), "Este abrigo gris es más cálido que aquel negro.", "Questo cappotto grigio è più caldo di quello nero.", "This grey coat is warmer than that black one.", "Il secondo termine di paragone in spagnolo è introdotto da 'que'.", "Spanish uses 'más/menos + adjective + que' for comparisons.", listOf(Triple("Este abrigo", "Questo cappotto", "This coat"), Triple("más cálido que", "più caldo di", "warmer than"), Triple("aquel negro", "quello nero", "that black one"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "Prenotare in albergo", "Booking a hotel", "Tenía reservada una habitación doble con desayuno ___.", "incluido", listOf("incluida", "incluidos", "incluir"), "Tenía reservada una habitación doble con desayuno incluido.", "Avevo prenotato una camera doppia con colazione inclusa.", "I had booked a double room with breakfast included.", "'Incluido' concorda con il sostantivo maschile 'desayuno'.", "'Incluido' agrees with the masculine noun 'desayuno' (breakfast).", listOf(Triple("una habitación doble", "una camera doppia", "a double room"), Triple("desayuno incluido", "colazione inclusa", "breakfast included"), Triple("la recepción", "la reception", "the front desk"))),
                CurriculumSeed("Capitolo 5", "Chapter 5", "Progetti futuri", "Future plans", "El próximo mes ___ a empezar un curso intensivo en Valencia.", "voy", listOf("iré", "soy", "he"), "El próximo mes voy a empezar un curso intensivo en Valencia.", "Il mese prossimo inizierò un corso intensivo a Valencia.", "Next month I am going to start an intensive course in Valencia.", "'Ir a + infinito' indica un progetto futuro sicuro.", "'Ir a + infinitive' expresses planned future actions.", listOf(Triple("El próximo mes", "Il mese prossimo", "Next month"), Triple("voy a empezar", "inizierò", "I am going to start"), Triple("un curso intensivo", "un corso intensivo", "an intensive course")))
            )
            CefrLevel.B1 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Esprimere opinioni", "Expressing opinions", "No creo que el vuelo ___ retraso con este buen tiempo.", "tenga", listOf("tiene", "tendrá", "tuvo"), "No creo que el vuelo tenga retraso con este buen tiempo.", "Non credo che il volo abbia ritardo con questo bel tempo.", "I don't think the flight will be delayed in this good weather.", "Con 'No creo que' è obbligatorio il congiuntivo ('tenga').", "Negative 'no creo que' requires the subjunctive.", listOf(Triple("No creo que", "Non credo che", "I don't think that"), Triple("tenga retraso", "abbia ritardo", "is delayed"), Triple("buen tiempo", "bel tempo", "good weather"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Dare consigli", "Giving advice", "En tu lugar, yo ___ directamente con el director del departamento.", "hablaría", listOf("hablaba", "hablé", "hable"), "En tu lugar, yo hablaría directamente con el director del departamento.", "Al posto tuo, io parlerei direttamente con il direttore.", "In your place, I would speak directly with the director.", "Il condizionale semplice si forma aggiungendo -ía all'infinito.", "Form the conditional by adding -ía to the full infinitive.", listOf(Triple("En tu lugar", "Al posto tuo", "In your shoes"), Triple("yo hablaría", "io parlerei", "I would speak"), Triple("directamente", "direttamente", "directly"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Usare Por e Para", "Using Por & Para", "Te llamo ___ confirmarte la reunión de mañana por la mañana.", "para", listOf("por", "en", "de"), "Te llamo para confirmarte la reunión de mañana por la mañana.", "Ti chiamo per confermarti la riunione di domani mattina.", "I am calling you in order to confirm tomorrow morning's meeting.", "Usa 'para' per lo scopo ('per + infinito') e 'por' per la causa.", "Use 'para' for purpose ('in order to') and 'por' for cause.", listOf(Triple("Te llamo para", "Ti chiamo per", "I call you to"), Triple("confirmarte", "confermarti", "confirm to you"), Triple("la reunión", "la riunione", "the meeting"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "Frasi temporali al futuro", "Future time clauses", "En cuanto ___ los resultados, te enviaré un mensaje.", "sepa", listOf("sé", "sabré", "sabía"), "En cuanto sepa los resultados, te enviaré un mensaje.", "Non appena saprò i risultati, ti manderò un messaggio.", "As soon as I know the results, I will send you a message.", "Dopo 'cuando, en cuanto' riferiti al futuro si usa il congiuntivo presente.", "After 'cuando' and 'en cuanto' referring to the future, use present subjunctive.", listOf(Triple("En cuanto sepa", "Non appena saprò", "As soon as I know"), Triple("los resultados", "i risultati", "the results"), Triple("te enviaré", "ti invierò", "I will send you"))),
                CurriculumSeed("Capitolo 5", "Chapter 5", "Azioni continuative", "Ongoing duration", "Nosotros ___ trabajando en esta empresa desde hace tres años.", "llevamos", listOf("estamos", "somos", "tenemos"), "Nosotros llevamos trabajando en esta empresa desde hace tres años.", "Lavoriamo in questa azienda da tre anni.", "We have been working at this company for three years.", "'Llevar + gerundio' esprime da quanto tempo dura un'azione.", "'Llevar + gerund' expresses how long an action has been happening.", listOf(Triple("llevamos trabajando", "lavoriamo da...", "we have been working"), Triple("en esta empresa", "in questa azienda", "at this company"), Triple("desde hace tres años", "da tre anni", "for three years")))
            )
            CefrLevel.B2 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Periodo ipotetico", "Counterfactuals", "Si ___ más tiempo libre, aprendería a tocar el violonchelo.", "tuviera", listOf("tendría", "tengo", "habría tenido"), "Si tuviera más tiempo libre, aprendería a tocar el violonchelo.", "Se avessi più tempo libero, imparerei a suonare il violoncello.", "If I had more free time, I would learn to play the cello.", "Dopo 'Si' ipotetico si usa il congiuntivo imperfetto (-ra/-se).", "Use imperfect subjunctive ('tuviera') in the 'si' clause.", listOf(Triple("Si tuviera", "Se avessi", "If I had"), Triple("tiempo libre", "tempo libero", "free time"), Triple("aprendería", "imparerei", "I would learn"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Concessive con Aunque", "Concessive clauses", "Aunque ___ mañana mismo, no lograríamos terminar a tiempo.", "empezáramos", listOf("empezamos", "empezaremos", "empezaríamos"), "Aunque empezáramos mañana mismo, no lograríamos terminar a tiempo.", "Anche se iniziassimo domani stesso, non riusciremmo a finire in tempo.", "Even if we started tomorrow, we wouldn't manage to finish on time.", "'Aunque + congiuntivo imperfetto' traduce 'anche se + congiuntivo'.", "'Aunque + imperfect subjunctive' means 'even if'.", listOf(Triple("Aunque empezáramos", "Anche se iniziassimo", "Even if we started"), Triple("mañana mismo", "domani stesso", "tomorrow itself"), Triple("no lograríamos", "non riusciremmo", "we wouldn't manage"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Verbi di cambiamento", "Verbs of change", "Cuando escuchó la noticia, se ___ muy nervioso.", "puso", listOf("hizo", "llegó", "quedó"), "Cuando escuchó la noticia, se puso muy nervioso.", "Quando ha sentito la noticia, è diventato molto nervoso.", "When he heard the news, he became very nervous.", "Usa 'ponerse + aggettivo' per cambiamenti rapidi di stato d'animo.", "Use 'ponerse + adjective' for sudden changes in mood.", listOf(Triple("Cuando escuchó", "Quando sentì", "When he heard"), Triple("se puso nervioso", "si è innervosito", "he got nervous"), Triple("la noticia", "la notizia", "the news"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "Discorso indiretto", "Reported speech", "El ministro aseguró que las medidas ___ en vigor el mes siguiente.", "entrarían", listOf("entrarán", "entren", "entran"), "El ministro aseguró que las medidas entrarían en vigor el mes siguiente.", "Il ministro ha assicurato che le misure sarebbero entrate in vigore il mese successivo.", "The minister assured that the measures would take effect the following month.", "Nel discorso indiretto al passato, il futuro diventa condizionale.", "In past reported speech, future actions shift to the conditional.", listOf(Triple("El ministro aseguró", "Il ministro assicurò", "The minister assured"), Triple("entrarían en vigor", "sarebbero entrate in vigore", "would take effect"), Triple("el mes siguiente", "il mese seguente", "the following month"))),
                CurriculumSeed("Capitolo 5", "Chapter 5", "Connettori formali", "Formal connectors", "La inversión es elevada; ___ embargo, los beneficios a largo plazo son indiscutibles.", "sin", listOf("con", "por", "no"), "La inversión es elevada; sin embargo, los beneficios a largo plazo son indiscutibles.", "L'investimento è elevato; tuttavia, i benefici a lungo termine sono indiscutibili.", "The investment is high; however, the long-term benefits are undeniable.", "'Sin embargo' è il connettore formale per 'tuttavia'.", "'Sin embargo' means 'however' in formal writing.", listOf(Triple("sin embargo", "tuttavia", "however"), Triple("a largo plazo", "a lungo termine", "long-term"), Triple("indiscutibles", "indiscutibili", "undeniable")))
            )
        }
        return expandTo50Units(baseTemplates)
    }

    private fun buildGerman50Seeds(level: CefrLevel): List<CurriculumSeed> {
        val baseTemplates: List<CurriculumSeed> = when (level) {
            CefrLevel.A1 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Salutare e ordinare", "Polite ordering", "Guten Tag, ich ___ gern einen Kaffee ohne Zucker.", "möchte", listOf("möchten", "bin", "hast"), "Guten Tag, ich möchte gern einen Kaffee ohne Zucker.", "Buongiorno, vorrei volentieri un caffè senza zucchero.", "Good day, I would like a coffee without sugar.", "'Ich möchte gern' è la formula più educata per ordinare in tedesco.", "'Ich möchte gern' is the polite way to order in German.", listOf(Triple("Guten Tag", "Buongiorno", "Good day"), Triple("ich möchte gern", "vorrei volentieri", "I would like"), Triple("ohne Zucker", "senza zucchero", "without sugar"))),
                CurriculumSeed("Capitolo 1", "Chapter 1", "Presentarsi e origine", "Introducing yourself", "Hallo, ich ___ aus Italien und wohne jetzt in Berlin.", "komme", listOf("kommst", "kommt", "bin"), "Hallo, ich komme aus Italien und wohne jetzt in Berlin.", "Ciao, vengo dall'Italia e ora abito a Berlino.", "Hello, I come from Italy and live in Berlin now.", "Con 'ich' i verbi regolari al presente terminano in -e: ich komme, ich wohne.", "With 'ich', regular present tense verbs end in -e: ich komme, ich wohne.", listOf(Triple("ich komme aus", "vengo da", "I come from"), Triple("und wohne", "e abito", "and live"), Triple("jetzt in Berlin", "ora a Berlino", "now in Berlin"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Il verbo Sein (Essere)", "Verb Sein (To be)", "Sind Sie Herr Weber? — Ja, das ___ ich.", "bin", listOf("bist", "ist", "sind"), "Ja, das bin ich.", "Sì, sono io.", "Yes, that's me.", "Coniugazione di sein: ich bin, du bist, er/sie/es ist, wir sind, Sie sind.", "Conjugation of sein: ich bin, du bist, er/sie/es ist, wir sind, Sie sind.", listOf(Triple("Sind Sie...?", "È Lei...?", "Are you...?"), Triple("Ja, das bin ich", "Sì, sono io", "Yes, that is me"), Triple("Willkommen", "Benvenuto", "Welcome"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Verbo in 2ª posizione", "Verb in 2nd position", "Heute ___ wir zusammen ins Kino.", "gehen", listOf("gehe", "geht", "gegangen"), "Heute gehen wir zusammen ins Kino.", "Oggi andiamo insieme al cinema.", "Today we are going to the cinema together.", "Se la frase inizia con 'Heute', il verbo ('gehen') resta al 2° posto prima di 'wir'.", "When starting with 'Heute', the verb stays in 2nd position before 'wir'.", listOf(Triple("Heute", "Oggi", "Today"), Triple("gehen wir", "andiamo noi", "we go"), Triple("zusammen", "insieme", "together"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Il caso Accusativo", "Accusative case", "Ich suche ___ Bahnhof. Können Sie mir helfen?", "den", listOf("der", "dem", "das"), "Ich suche den Bahnhof. Können Sie mir helfen?", "Cerco la stazione. Può aiutarmi?", "I am looking for the train station. Can you help me?", "I nomi maschili ('der Bahnhof') come oggetto diretto diventano 'den / einen'.", "Masculine nouns ('der') change to 'den / einen' as direct objects.", listOf(Triple("Ich suche", "Io cerco", "I look for"), Triple("den Bahnhof", "la stazione", "the station"), Triple("helfen", "aiutare", "to help"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "I verbi modali", "Modal verbs", "Wir ___ leider heute Abend nicht mitkommen.", "können", listOf("kann", "könnt", "kannst"), "Wir können leider heute Abend nicht mitkommen.", "Purtroppo stasera non possiamo venire con voi.", "Unfortunately we cannot come along tonight.", "Con i verbi modali ('können, müssen'), l'infinito va in fondo alla frase.", "With modal verbs, the infinitive verb ('mitkommen') goes to the end.", listOf(Triple("Wir können", "Noi possiamo", "We can"), Triple("leider nicht", "purtroppo non", "unfortunately not"), Triple("mitkommen", "venire insieme", "come along"))),
                CurriculumSeed("Capitolo 5", "Chapter 5", "I verbi separabili", "Separable verbs", "Der Zug nach Frankfurt ___ um acht Uhr auf Gleis drei ab.", "fährt", listOf("fahren", "abfahren", "fuhr"), "Der Zug nach Frankfurt fährt um acht Uhr auf Gleis drei ab.", "Il treno per Francoforte parte alle otto al binario tre.", "The train to Frankfurt departs at eight o'clock on track three.", "Con 'abfahren' (partire), 'fährt' sta al 2° posto e il prefisso 'ab' chiude la frase.", "In separable verbs like 'abfahren', the prefix 'ab' moves to the end.", listOf(Triple("Der Zug", "Il treno", "The train"), Triple("fährt ... ab", "parte", "departs"), Triple("auf Gleis drei", "al binario tre", "on track three")))
            )
            CefrLevel.A2 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Passato con Haben", "Past with Haben", "Gestern ___ ich den ganzen Nachmittag für die Prüfung gelernt.", "habe", listOf("bin", "hat", "hatte"), "Gestern habe ich den ganzen Nachmittag für die Prüfung gelernt.", "Ieri ho studiato tutto il pomeriggio per l'esame.", "Yesterday I studied all afternoon for the exam.", "Il Perfekt usa 'haben' al 2° posto e il participio ('gelernt') in fondo.", "Place auxiliary 'habe' in 2nd position and participle 'gelernt' at the end.", listOf(Triple("Gestern habe ich", "Ieri ho", "Yesterday I have"), Triple("für die Prüfung", "per l'esame", "for the exam"), Triple("gelernt", "studiato", "studied"))),
                CurriculumSeed("Capitolo 1", "Chapter 1", "Passato di moto con Sein", "Past of motion with Sein", "Letztes Wochenende ___ wir nach Wien gefahren.", "sind", listOf("haben", "seid", "waren"), "Letztes Wochenende sind wir nach Wien gefahren.", "Lo scorso fine settimana siamo andati a Vienna.", "Last weekend we traveled to Vienna.", "I verbi di spostamento ('fahren, gehen, fliegen') formano il passato con 'sein'.", "Verbs of movement ('fahren, gehen, fliegen') take 'sein' in the Perfekt.", listOf(Triple("Letztes Wochenende", "Lo scorso weekend", "Last weekend"), Triple("sind wir", "siamo", "we are/have"), Triple("gefahren", "andati", "traveled"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Preposizioni col Dativo", "Dative prepositions", "Ich fahre jeden Morgen mit ___ U-Bahn zur Arbeit.", "der", listOf("die", "den", "dem"), "Ich fahre jeden Morgen mit der U-Bahn zur Arbeit.", "Vado ogni mattina al lavoro con la metropolitana.", "I go to work every morning by subway.", "Dopo 'mit' si usa sempre il Dativo: il femminile 'die U-Bahn' diventa 'mit der U-Bahn'.", "After 'mit', feminine 'die' shifts to dative 'der' ('mit der U-Bahn').", listOf(Triple("jeden Morgen", "ogni mattina", "every morning"), Triple("mit der U-Bahn", "con la metro", "by subway"), Triple("zur Arbeit", "al lavoro", "to work"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Frasi causali con Weil", "Causal clauses with Weil", "Ich bleibe heute im Bett, weil ich starke Kopfschmerzen ___.", "habe", listOf("haben", "habt", "bin"), "Ich bleibe heute im Bett, weil ich starke Kopfschmerzen habe.", "Oggi resto a letto perché ho un forte mal di testa.", "I am staying in bed today because I have a bad headache.", "Dopo 'weil' (perché) il verbo coniugato ('habe') va sempre in ultima posizione.", "Subordinating conjunction 'weil' pushes the finite verb ('habe') to the end.", listOf(Triple("im Bett", "a letto", "in bed"), Triple("weil ich ... habe", "perché ho", "because I have"), Triple("Kopfschmerzen", "mal di testa", "headache"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "Domande indirette", "Indirect questions", "Können Sie mir bitte sagen, wann der nächste Bus ___?", "kommt", listOf("kommen", "kam", "gekommen"), "Können Sie mir bitte sagen, wann der nächste Bus kommt?", "Può dirmi per favore quando arriva il prossimo autobus?", "Can you please tell me when the next bus arrives?", "Nelle domande indirette ('wann..., wo..., ob...') il verbo va in fondo alla frase.", "In indirect questions, the conjugated verb moves to the end.", listOf(Triple("Können Sie mir sagen", "Può dirmi", "Can you tell me"), Triple("der nächste Bus", "il prossimo autobus", "the next bus"), Triple("wann ... kommt", "quando arriva", "when ... arrives")))
            )
            CefrLevel.B1 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Modali al passato", "Modals in the past", "Gestern ___ ich länger im Büro bleiben, weil viel zu tun war.", "musste", listOf("muss", "gemusst", "müsste"), "Gestern musste ich länger im Büro bleiben, weil viel zu tun war.", "Ieri sono dovuto restare più a lungo in ufficio perché c'era molto da fare.", "Yesterday I had to stay longer at the office because there was a lot to do.", "Con i verbi modali al passato si usa il Präteritum ('ich musste, ich konnte').", "German uses the Präteritum ('musste, konnte, wollte') for modal verbs in the past.", listOf(Triple("Gestern musste ich", "Ieri ho dovuto", "Yesterday I had to"), Triple("länger bleiben", "restare più a lungo", "stay longer"), Triple("viel zu tun", "molto da fare", "a lot to do"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Consigli con Würde", "Advice with Würde", "An deiner Stelle ___ ich dieses Angebot sofort annehmen.", "würde", listOf("werde", "wurde", "wäre"), "An deiner Stelle würde ich dieses Angebot sofort annehmen.", "Al posto tuo accetterei subito questa offerta.", "In your place, I would accept this offer immediately.", "'Ich würde + infinito in fondo' corrisponde al condizionale italiano.", "'Würde + infinitive at the end' forms the present conditional.", listOf(Triple("An deiner Stelle", "Al posto tuo", "In your place"), Triple("würde ich ... annehmen", "accetterei", "I would accept"), Triple("dieses Angebot", "questa offerta", "this offer"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Le frasi relative", "Relative clauses", "Das ist der Kollege, mit ___ ich das Projekt geleitet habe.", "dem", listOf("den", "der", "dessen"), "Das ist der Kollege, mit dem ich das Projekt geleitet habe.", "Questo è il collega con cui ho diretto il progetto.", "This is the colleague with whom I led the project.", "'Mit' regge il dativo maschile ('dem'), e il verbo chiude la frase relativa.", "'Mit' requires masculine dative 'dem', and the relative clause ends with the verb.", listOf(Triple("der Kollege", "il collega", "the colleague"), Triple("mit dem", "con il quale", "with whom"), Triple("geleitet habe", "ho diretto", "have led"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "Scopo con um... zu", "Purpose with um... zu", "Ich lerne jeden Tag Deutsch, ___ in München zu arbeiten.", "um", listOf("für", "damit", "weil"), "Ich lerne jeden Tag Deutsch, um in München zu arbeiten.", "Studio tedesco ogni giorno per lavorare a Monaco.", "I study German every day in order to work in Munich.", "Per tradurre 'per + infinito' si usa 'um ... zu + infinito' in chiusura di frase.", "Use 'um ... zu + infinitive' to express 'in order to'.", listOf(Triple("jeden Tag", "ogni giorno", "every day"), Triple("um ... zu arbeiten", "per lavorare", "in order to work"), Triple("in München", "a Monaco", "in Munich"))),
                CurriculumSeed("Capitolo 5", "Chapter 5", "Preposizioni col Genitivo", "Genitive prepositions", "Während ___ gesamten Konferenz wurden wichtige Themen besprochen.", "der", listOf("die", "dem", "den"), "Während der gesamten Konferenz wurden wichtige Themen besprochen.", "Durante l'intera conferenza sono stati discussi temi importanti.", "During the entire conference, important topics were discussed.", "Con 'während' (durante), il femminile 'die Konferenz' al genitivo diventa 'der Konferenz'.", "With genitive preposition 'während', feminine 'die' becomes 'der'.", listOf(Triple("Während der Konferenz", "Durante la conferenza", "During the conference"), Triple("wurden ... besprochen", "sono stati discussi", "were discussed"), Triple("wichtige Themen", "temi importanti", "important topics")))
            )
            CefrLevel.B2 -> listOf(
                CurriculumSeed("Capitolo 1", "Chapter 1", "Costrutto Je ... desto", "Je ... desto structure", "Je gründlicher wir die Daten prüfen, ___ sicherer ist das Ergebnis.", "desto", listOf("weil", "obwohl", "damit"), "Je gründlicher wir die Daten prüfen, desto sicherer ist das Ergebnis.", "Più approfonditamente verifichiamo i dati, più sicuro è il risultato.", "The more thoroughly we check the data, the more reliable the result is.", "La prima frase con 'Je' ha il verbo alla fine, la seconda con 'desto' ha il verbo subito dopo.", "'Je' takes verb-final order; 'desto + comparative' is followed by the verb.", listOf(Triple("Je gründlicher ... prüfen", "Più a fondo controlliamo", "The more thoroughly we check"), Triple("desto sicherer ist", "più sicuro è", "the safer is"), Triple("das Ergebnis", "il risultato", "the result"))),
                CurriculumSeed("Capitolo 2", "Chapter 2", "Ipotesi nel passato", "Past hypotheticals", "Wenn wir früher losgefahren wären, ___ wir den Zug nicht verpasst.", "hätten", listOf("haben", "wären", "würden"), "Wenn wir früher losgefahren wären, hätten wir den Zug nicht verpasst.", "Se fossimo partiti prima, non avremmo perso il treno.", "If we had left earlier, we would not have missed the train.", "Per l'irrealtà nel passato si usano 'wären/hätten + participio passato'.", "Use 'wären/hätten + past participle' for past counterfactual conditions.", listOf(Triple("Wenn wir ... wären", "Se fossimo partiti", "If we had left"), Triple("hätten wir ... verpasst", "avremmo perso", "we would have missed"), Triple("früher", "più presto", "earlier"))),
                CurriculumSeed("Capitolo 3", "Chapter 3", "Passivo coi modali", "Modal passive", "Dieses technische Problem muss bis morgen dringend ___ werden.", "gelöst", listOf("lösen", "löste", "gelöste"), "Dieses technische Problem muss bis morgen dringend gelöst werden.", "Questo problema tecnico deve essere risolto urgentemente entro domani.", "This technical problem must be solved urgently by tomorrow.", "Passivo modale: modale al 2° posto + participio passato + 'werden' in fondo.", "Modal passive: modal verb in V2 + past participle + 'werden' at the end.", listOf(Triple("muss ... gelöst werden", "deve essere risolto", "must be solved"), Triple("dringend", "urgentemente", "urgently"), Triple("bis morgen", "entro domani", "by tomorrow"))),
                CurriculumSeed("Capitolo 4", "Chapter 4", "Pronomi preposizionali", "Prepositional pronouns", "Ich freue mich schon sehr ___, dass wir uns nächste Woche wiedersehen.", "darauf", listOf("daran", "damit", "darüber"), "Ich freue mich schon sehr darauf, dass wir uns nächste Woche wiedersehen.", "Non vedo l'ora che ci rivediamo la settimana prossima.", "I am really looking forward to seeing each other again next week.", "'Sich freuen auf' anticipa la subordinata tramite 'darauf'.", "'Sich freuen auf' uses 'darauf' to anticipate a 'dass' clause.", listOf(Triple("Ich freue mich darauf", "Non vedo l'ora", "I look forward to it"), Triple("nächste Woche", "la prossima settimana", "next week"), Triple("wiedersehen", "rivedersi", "see again"))),
                CurriculumSeed("Capitolo 5", "Chapter 5", "Connettori doppi", "Double connectors", "Die neue Strategie spart ___ Zeit als auch erhebliche Kosten.", "sowohl", listOf("weder", "entweder", "nicht"), "Die neue Strategie spart sowohl Zeit als auch erhebliche Kosten.", "La nuova strategia fa risparmiare sia tempo sia costi considerevoli.", "The new strategy saves both time and considerable costs.", "'Sowohl ... als auch' traduce 'sia ... sia'.", "'Sowohl ... als auch' means 'both ... and'.", listOf(Triple("sowohl ... als auch", "sia ... sia", "both ... and"), Triple("spart Zeit", "risparmia tempo", "saves time"), Triple("erhebliche Kosten", "costi considerevoli", "considerable costs")))
            )
        }
        return expandTo50Units(baseTemplates)
    }

    private fun expandTo50Units(templates: List<CurriculumSeed>): List<CurriculumSeed> {
        val result = ArrayList<CurriculumSeed>(50)
        for (i in 0 until 50) {
            val chapterNum = (i / 10) + 1
            val base = templates[i % templates.size]
            result.add(
                base.copy(
                    chapterTitleIt = "Capitolo $chapterNum",
                    chapterTitleEn = "Chapter $chapterNum"
                )
            )
        }
        return result
    }
}
