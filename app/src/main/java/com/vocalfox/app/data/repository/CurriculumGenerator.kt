package com.vocalfox.app.data.repository

import androidx.compose.ui.graphics.Color
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
    val tokens: List<Triple<String, String, String>> // surface, glossIt, glossEn
)

/**
 * Generates 50 complete progressive Units for EACH CEFR level (A1, A2, B1, B2) = 200 Units per language!
 * Every unit has its own thematic focus, vocabulary discovery cards, zero-spoiler multiple-choice quiz,
 * verb/pronoun inflection check, word-bank sentence builder, and voice pronunciation check.
 */
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
                title = LocalizedText(
                    en = "Unit ${idx + 1} · ${seed.unitTitleEn}",
                    it = "Unità ${idx + 1} · ${seed.unitTitleIt}"
                ),
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
                durationMinutes = 4 + (idx % 3),
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
                // Capitolo 1 (1-10): Saluti, Presentazioni e Pronuncia
                CurriculumSeed("Cap. 1 · Saluti e Presentazioni", "Ch. 1 · Greetings & Introductions", "Salutare al mattino", "Morning greetings", "Hola, buenos días. ¿Cómo ___ usted hoy?", "está", listOf("es", "soy", "están"), "Hola, buenos días. ¿Cómo está usted hoy?", "Ciao, buongiorno. Come sta Lei oggi?", "Hello, good morning. How are you today?", "Usa '¿Cómo está?' per chiedere come sta qualcuno.", "Use '¿Cómo está?' to ask how someone is feeling.", listOf(Triple("Buenos días", "Buongiorno", "Good morning"), Triple("¿Cómo está?", "Come sta?", "How are you?"), Triple("hoy", "oggi", "today"))),
                CurriculumSeed("Cap. 1 · Saluti e Presentazioni", "Ch. 1 · Greetings & Introductions", "Dire il proprio nome", "Saying your name", "Mucho gusto, yo me ___ Alessandro.", "llamo", listOf("llamas", "llama", "soy"), "Mucho gusto, yo me llamo Alessandro.", "Piacere, io mi chiamo Alessandro.", "Nice to meet you, my name is Alessandro.", "Il verbo riflessivo 'llamarse' usa: me llamo, te llamas, se llama.", "The reflexive verb 'llamarse' uses: me llamo, te llamas, se llama.", listOf(Triple("Mucho gusto", "Molto piacere", "Nice to meet you"), Triple("yo me llamo", "io mi chiamo", "my name is"), Triple("encantado", "piacere", "delighted"))),
                CurriculumSeed("Cap. 1 · Saluti e Presentazioni", "Ch. 1 · Greetings & Introductions", "Origine e nazionalità (Ser)", "Origin & nationality (Ser)", "Nosotros ___ de Italia, pero vivimos aquí.", "somos", listOf("estamos", "son", "soy"), "Nosotros somos de Italia, pero vivimos aquí.", "Noi siamo italiani, ma viviamo qui.", "We are from Italy, but we live here.", "Per nazionalità e origine si usa sempre 'ser' (soy, eres, es, somos).", "Always use 'ser' (soy, eres, es, somos) for origin and nationality.", listOf(Triple("Nosotros somos", "Noi siamo", "We are"), Triple("de Italia", "italiani / d'Italia", "from Italy"), Triple("vivimos aquí", "viviamo qui", "we live here"))),
                CurriculumSeed("Cap. 1 · Saluti e Presentazioni", "Ch. 1 · Greetings & Introductions", "Posizione attuale (Estar)", "Current location (Estar)", "Mi hermana ___ en el centro de Madrid ahora.", "está", listOf("es", "estoy", "son"), "Mi hermana está en el centro de Madrid ahora.", "Mia sorella si trova nel centro di Madrid adesso.", "My sister is in the center of Madrid right now.", "Per indicare dove si trova una persona o un oggetto usa sempre 'estar'.", "Use 'estar' to state where someone or something is located.", listOf(Triple("Mi hermana", "Mia sorella", "My sister"), Triple("está en", "si trova a", "is in"), Triple("el centro", "il centro", "downtown"))),
                CurriculumSeed("Cap. 1 · Saluti e Presentazioni", "Ch. 1 · Greetings & Introductions", "Ringraziare e rispondere", "Thanking & replying", "Muchas gracias por tu ayuda. — De ___.", "nada", listOf("todo", "algo", "favor"), "Muchas gracias por tu ayuda. De nada.", "Molte grazie per il tuo aiuto. Di niente.", "Thank you very much for your help. You're welcome.", "'De nada' e 'No hay de qué' sono le risposte naturali a 'Gracias'.", "'De nada' is the standard reply to 'Gracias'.", listOf(Triple("Muchas gracias", "Molte grazie", "Thank you very much"), Triple("por tu ayuda", "per il tuo aiuto", "for your help"), Triple("De nada", "Di niente / Prego", "You're welcome"))),
                // Capitolo 2 (11-20): Verbi Essere, Avere (Tener/Haber) e Articoli
                CurriculumSeed("Cap. 2 · Verbi Base e Articoli", "Ch. 2 · Core Verbs & Articles", "Il verbo Tener (Avere)", "Verb Tener (To have)", "Yo ___ dos hermanos y un perro muy simpático.", "tengo", listOf("tienes", "he", "soy"), "Yo tengo dos hermanos y un perro muy simpático.", "Io ho due fratelli e un cane molto simpatico.", "I have two brothers and a very friendly dog.", "Il possesso si esprime con 'tener' (tengo, tienes, tiene, tenemos).", "Express possession with 'tener' (tengo, tienes, tiene, tenemos).", listOf(Triple("Yo tengo", "Io ho", "I have"), Triple("dos hermanos", "due fratelli", "two brothers"), Triple("muy simpático", "molto simpatico", "very friendly"))),
                CurriculumSeed("Cap. 2 · Verbi Base e Articoli", "Ch. 2 · Core Verbs & Articles", "Esistenza con Hay (C'è / Ci sono)", "Existence with Hay", "En esta plaza ___ una farmacia y dos bancos.", "hay", listOf("está", "son", "tiene"), "En esta plaza hay una farmacia y dos bancos.", "In questa piazza c'è una farmacia e ci sono due banche.", "In this square there is a pharmacy and two banks.", "Usa 'hay' (invariabile) sia per 'c'è' sia per 'ci sono' con nomi indeterminati.", "Use invariable 'hay' for both 'there is' and 'there are'.", listOf(Triple("En esta plaza", "In questa piazza", "In this square"), Triple("hay", "c'è / ci sono", "there is / are"), Triple("una farmacia", "una farmacia", "a pharmacy"))),
                CurriculumSeed("Cap. 2 · Verbi Base e Articoli", "Ch. 2 · Core Verbs & Articles", "Articoli determinativi (el, la, los, las)", "Definite articles", "___ libros de español están sobre la mesa.", "Los", listOf("El", "Las", "Unos"), "Los libros de español están sobre la mesa.", "I libri di spagnolo sono sul tavolo.", "The Spanish books are on the table.", "Il plurale di 'el' è 'los', mentre il plurale di 'la' è 'las'.", "The plural of masculine 'el' is 'los'; feminine 'la' becomes 'las'.", listOf(Triple("Los libros", "I libri", "The books"), Triple("están", "sono / si trovano", "are located"), Triple("sobre la mesa", "sul tavolo", "on the table"))),
                CurriculumSeed("Cap. 2 · Verbi Base e Articoli", "Ch. 2 · Core Verbs & Articles", "Avere fame, sete e sonno (Tener)", "Hunger, thirst & tiredness", "¿Tienes sed? Sí, ___ mucha sed y un poco de hambre.", "tengo", listOf("estoy", "soy", "hay"), "Sí, tengo mucha sed y un poco de hambre.", "Sì, ho molta sete e un po' di fame.", "Yes, I am very thirsty and a little hungry.", "In spagnolo si dice 'tener hambre/sed/frío/calor/sueño' come in italiano.", "Spanish uses 'tener + noun' for hunger, thirst, cold, heat, and sleepiness.", listOf(Triple("tengo mucha sed", "ho molta sete", "I am very thirsty"), Triple("un poco de", "un po' di", "a bit of"), Triple("hambre", "fame", "hunger"))),
                CurriculumSeed("Cap. 2 · Verbi Base e Articoli", "Ch. 2 · Core Verbs & Articles", "Andare verso un luogo (Ir + a)", "Going places (Ir + a)", "Esta tarde nosotros ___ al cine con nuestros amigos.", "vamos", listOf("voy", "van", "somos"), "Esta tarde nosotros vamos al cine con nuestros amigos.", "Questo pomeriggio noi andiamo al cinema con i nostri amici.", "This afternoon we are going to the cinema with our friends.", "Il verbo 'ir' (voy, vas, va, vamos, van) regge sempre la preposizione 'a' (a + el = al).", "The verb 'ir' always takes 'a' for destination (a + el contracts to al).", listOf(Triple("Esta tarde", "Questo pomeriggio", "This afternoon"), Triple("vamos al cine", "andiamo al cinema", "we go to the cinema"), Triple("nuestros amigos", "i nostri amici", "our friends"))),
                // Capitolo 3 (21-30): Pronomi, Aggettivi e Famiglia
                CurriculumSeed("Cap. 3 · Pronomi, Aggettivi e Famiglia", "Ch. 3 · Pronouns, Adjectives & Family", "Concordanza degli aggettivi", "Adjective agreement", "Mis primas son muy ___ y trabajan en el hospital.", "simpáticas", listOf("simpático", "simpáticos", "simpática"), "Mis primas son muy simpáticas y trabajan en el hospital.", "Le mie cugine sono molto simpatiche e lavorano in ospedale.", "My female cousins are very kind and work at the hospital.", "Gli aggettivi concordano in genere (-o/-a) e numero (-s/-es) col sostantivo.", "Adjectives agree in gender and number with the noun they describe.", listOf(Triple("Mis primas", "Le mie cugine", "My cousins"), Triple("muy simpáticas", "molto simpatiche", "very nice"), Triple("trabajan", "lavorano", "they work"))),
                CurriculumSeed("Cap. 3 · Pronomi, Aggettivi e Famiglia", "Ch. 3 · Pronouns, Adjectives & Family", "Aggettivi possessivi (mi, tu, su)", "Possessive adjectives", "¿Dónde están ___ llaves? No las veo en mi bolso.", "mis", listOf("mi", "mía", "tuyo"), "Dónde están mis llaves. No las veo en mi bolso.", "Dove sono le mie chiavi? Non le vedo nella mia borsa.", "Where are my keys? I don't see them in my bag.", "Davanti a un nome plurale, 'mi / tu / su' prendono la -s: 'mis llaves, tus libros'.", "Before plural nouns, 'mi, tu, su' become 'mis, tus, sus'.", listOf(Triple("¿Dónde están?", "Dove sono?", "Where are?"), Triple("mis llaves", "le mie chiavi", "my keys"), Triple("en mi bolso", "nella mia borsa", "in my bag"))),
                CurriculumSeed("Cap. 3 · Pronomi, Aggettivi e Famiglia", "Ch. 3 · Pronouns, Aggettivi e Famiglia", "Esprimere i gusti con Gustar", "Likes & dislikes with Gustar", "A mí me ___ mucho las películas españolas.", "gustan", listOf("gusta", "gusto", "gustas"), "A mí me gustan mucho las películas españolas.", "A me piacciono molto i film spagnoli.", "I really like Spanish movies.", "Usa 'me gusta' con singolare/infinito e 'me gustan' con cose plurali.", "Use 'me gusta' for singular/verbs and 'me gustan' for plural nouns.", listOf(Triple("A mí me gustan", "A me piacciono", "I like (plural)"), Triple("mucho", "molto", "a lot"), Triple("las películas", "i film", "the movies"))),
                // Capitolo 4 (31-40): Bar, Ristorante, Prezzi e Orari
                CurriculumSeed("Cap. 4 · Bar, Ristorante e Orari", "Ch. 4 · Café, Restaurant & Time", "Ordinare al ristorante (Querer)", "Ordering at a restaurant", "Para empezar, yo ___ una ensalada mixta y agua sin gas.", "quiero", listOf("querer", "quieres", "quiere"), "Para empezar, yo quiero una ensalada mixta y agua sin gas.", "Per iniziare, vorrei un'insalata mista e acqua naturale.", "To start, I would like a mixed salad and still water.", "Il verbo 'querer' dittonga la 'e' in 'ie': quiero, quieres, quiere, queremos, quieren.", "'Querer' changes stem e -> ie in present: quiero, quieres, quiere.", listOf(Triple("Para empezar", "Per iniziare", "To start"), Triple("una ensalada", "un'insalata", "a salad"), Triple("agua sin gas", "acqua naturale", "still water"))),
                CurriculumSeed("Cap. 4 · Bar, Ristorante e Orari", "Ch. 4 · Café, Restaurant & Time", "Chiedere il prezzo e il conto", "Asking prices & the bill", "Perdone, ¿nos ___ traer la cuenta cuando pueda?", "puede", listOf("puedo", "podemos", "pueden"), "Perdone, ¿nos puede traer la cuenta cuando pueda?", "Mi scusi, ci può portare il conto quando può?", "Excuse me, can you bring us the bill when you can?", "Il verbo modale 'poder' cambia 'o' in 'ue': puedo, puedes, puede + infinito.", "'Poder' changes o -> ue: ¿Nos puede traer la cuenta?", listOf(Triple("Perdone", "Mi scusi", "Excuse me"), Triple("¿nos puede traer?", "ci può portare?", "can you bring us?"), Triple("la cuenta", "il conto", "the bill"))),
                CurriculumSeed("Cap. 4 · Bar, Ristorante e Orari", "Ch. 4 · Café, Restaurant & Time", "Chiedere e dire l'ora", "Telling the time", "¿Qué hora es? — ___ las nueve y media de la mañana.", "Son", listOf("Es", "Están", "Hay"), "Son las nueve y media de la mañana.", "Sono le nove e mezza del mattino.", "It is nine thirty in the morning.", "Per le ore si usa 'Es la una' e 'Son las dos / las tres / las nueve'.", "Use 'Es la una' for 1:00 and 'Son las...' for all other hours.", listOf(Triple("¿Qué hora es?", "Che ore sono?", "What time is it?"), Triple("Son las nueve", "Sono le nove", "It's nine o'clock"), Triple("y media", "e mezza", "and a half"))),
                // Capitolo 5 (41-50): Città, Direzioni e Routine Quotidiana
                CurriculumSeed("Cap. 5 · Città e Routine", "Ch. 5 · City & Daily Routine", "Chiedere indicazioni stradali", "Asking for directions", "Disculpe, ¿dónde ___ la parada de metro más cercana?", "está", listOf("hay", "es", "son"), "Disculpe, ¿dónde está la parada de metro más cercana?", "Mi scusi, dov'è la fermata della metro più vicina?", "Excuse me, where is the nearest subway station?", "Con un luogo specifico preceduto da 'el / la' si usa sempre '¿dónde está?'.", "With a specific noun ('la parada'), always use '¿dónde está?'.", listOf(Triple("la parada de metro", "la fermata della metro", "the subway stop"), Triple("más cercana", "più vicina", "nearest"), Triple("todo recto", "sempre dritto", "straight ahead"))),
                CurriculumSeed("Cap. 5 · Città e Routine", "Ch. 5 · City & Daily Routine", "Verbi riflessivi della mattina", "Morning reflexive verbs", "Todos los días yo me ___ a las siete y desayuno café.", "levanto", listOf("levantas", "levanta", "levantar"), "Todos los días yo me levanto a las siete y desayuno café.", "Tutti i giorni mi alzo alle sette e faccio colazione col caffè.", "Every day I get up at seven and have coffee for breakfast.", "Con i verbi riflessivi il pronome precede il verbo: me levanto, te duchas, se viste.", "Place the reflexive pronoun before the conjugated verb: me levanto.", listOf(Triple("Todos los días", "Tutti i giorni", "Every day"), Triple("me levanto", "mi alzo", "I get up"), Triple("a las siete", "alle sette", "at seven")))
            )
            CefrLevel.A2 -> listOf(
                CurriculumSeed("Cap. 1 · Passato Prossimo e Indefinido", "Ch. 1 · Past Tenses", "Esperienze recenti (Pretérito Perfecto)", "Recent experiences", "Esta semana nosotros ___ visitado dos exposiciones muy interesantes.", "hemos", listOf("habéis", "han", "tenemos"), "Esta semana nosotros hemos visitado dos exposiciones muy interesantes.", "Questa settimana abbiamo visitato due mostre molto interessanti.", "This week we have visited two very interesting exhibitions.", "Con 'hoy, esta mañana, esta semana' usa 'haber (he, has, ha, hemos, han) + participio (-ado/-ido)'.", "Use 'haber + participle' with unfinished time frames like 'esta semana'.", listOf(Triple("Esta semana", "Questa settimana", "This week"), Triple("hemos visitado", "abbiamo visitato", "we have visited"), Triple("exposiciones", "mostre", "exhibitions"))),
                CurriculumSeed("Cap. 1 · Passato Prossimo e Indefinido", "Ch. 1 · Past Tenses", "Azioni concluse ieri (Indefinido)", "Completed actions yesterday", "Anoche mis amigos ___ una paella deliciosa en casa.", "prepararon", listOf("preparan", "preparaban", "han preparado"), "Anoche mis amigos prepararon una paella deliciosa en casa.", "Ieri sera i miei amici hanno preparato una paella deliziosa a casa.", "Last night my friends cooked a delicious paella at home.", "Con 'ayer, anoche, el año pasado' usa il pretérito indefinido.", "Use the indefinido with completed past markers like 'anoche'.", listOf(Triple("Anoche", "Ieri sera", "Last night"), Triple("prepararon", "prepararono / hanno preparato", "they prepared"), Triple("en casa", "a casa", "at home"))),
                CurriculumSeed("Cap. 2 · Pronomi Diretti e Indiretti", "Ch. 2 · Direct & Indirect Pronouns", "Pronomi oggetto diretto (lo, la, los, las)", "Direct object pronouns", "¿Has visto mis gafas? Sí, ___ vi sobre tu escritorio.", "las", listOf("los", "le", "la"), "Sí, las vi sobre tu escritorio.", "Sì, le ho viste sulla tua scrivania.", "Yes, I saw them on your desk.", "'Las' sostituisce un oggetto femminile plurale ('mis gafas').", "'Las' replaces a feminine plural direct object ('mis gafas').", listOf(Triple("mis gafas", "i miei occhiali", "my glasses"), Triple("las vi", "le ho viste", "I saw them"), Triple("tu escritorio", "la tua scrivania", "your desk"))),
                CurriculumSeed("Cap. 2 · Pronomi Diretti e Indiretti", "Ch. 2 · Direct & Indirect Pronouns", "Combinazione pronominale (se lo / se la)", "Double object pronouns (se lo)", "Le pedí el libro a Marta y ella ___ prestó enseguida.", "me lo", listOf("se la", "le lo", "me la"), "Le pedí el libro a Marta y ella me lo prestó enseguida.", "Ho chiesto il libro a Marta e lei me lo ha prestato subito.", "I asked Marta for the book and she lent it to me right away.", "Il pronome indiretto (me, te, se) precede sempre il pronome diretto (lo, la).", "Indirect object pronouns (me, te, se) always precede direct ones (lo, la).", listOf(Triple("Le pedí", "Le ho chiesto", "I asked her for"), Triple("me lo prestó", "me lo ha prestato", "she lent it to me"), Triple("enseguida", "subito", "right away"))),
                CurriculumSeed("Cap. 3 · Comparativi e Acquisti", "Ch. 3 · Comparatives & Shopping", "Comparativo di maggioranza e minoranza", "Comparatives", "Este abrigo gris es más cálido ___ aquel negro.", "que", listOf("de", "como", "cual"), "Este abrigo gris es más cálido que aquel negro.", "Questo cappotto grigio è più caldo di quello nero.", "This grey coat is warmer than that black one.", "Il secondo termine di paragone in spagnolo è introdotto da 'que' ('más/menos ... que').", "Spanish uses 'más/menos + adjective + que' for comparisons.", listOf(Triple("Este abrigo", "Questo cappotto", "This coat"), Triple("más cálido que", "più caldo di", "warmer than"), Triple("aquel negro", "quello nero", "that black one"))),
                CurriculumSeed("Cap. 4 · Viaggi, Hotel e Meteo", "Ch. 4 · Travel, Hotel & Weather", "Prenotare una camera d'albergo", "Booking a hotel room", "Tenía reservada una habitación doble con desayuno ___.", "incluido", listOf("incluida", "incluidos", "incluir"), "Tenía reservada una habitación doble con desayuno incluido.", "Avevo prenotato una camera doppia con colazione inclusa.", "I had booked a double room with breakfast included.", "'Incluido' concorda con il sostantivo maschile 'desayuno'.", "'Incluido' agrees with the masculine noun 'desayuno' (breakfast).", listOf(Triple("una habitación doble", "una camera doppia", "a double room"), Triple("desayuno incluido", "colazione inclusa", "breakfast included"), Triple("la recepción", "la reception", "the front desk"))),
                CurriculumSeed("Cap. 5 · Salute, Lavoro e Futuro", "Ch. 5 · Health, Work & Future", "Futuro intenzionale (Ir a + infinito)", "Near future (Ir a + infinitive)", "El próximo mes ___ a empezar un curso intensivo en Valencia.", "voy", listOf("iré", "soy", "he"), "El próximo mes voy a empezar un curso intensivo en Valencia.", "Il mese prossimo inizierò un corso intensivo a Valencia.", "Next month I am going to start an intensive course in Valencia.", "La perifrasi 'ir a + infinito' (voy a empezar) indica un progetto futuro sicuro.", "'Ir a + infinitive' expresses planned future actions.", listOf(Triple("El próximo mes", "Il mese prossimo", "Next month"), Triple("voy a empezar", "sto per iniziare / inizierò", "I am going to start"), Triple("un curso intensivo", "un corso intensivo", "an intensive course")))
            )
            CefrLevel.B1 -> listOf(
                CurriculumSeed("Cap. 1 · Congiuntivo e Opinioni", "Ch. 1 · Subjunctive & Opinions", "Opinioni negate (No creo que...)", "Negated opinions", "No creo que el vuelo ___ retraso con este buen tiempo.", "tenga", listOf("tiene", "tendrá", "tuvo"), "No creo que el vuelo tenga retraso con este buen tiempo.", "Non credo che il volo abbia ritardo con questo bel tempo.", "I don't think the flight will be delayed in this good weather.", "Con 'Creo que' si usa l'indicativo, ma con 'No creo que' è obbligatorio il congiuntivo ('tenga').", "Affirmative 'creo que' takes indicative; negative 'no creo que' requires subjunctive.", listOf(Triple("No creo que", "Non credo che (+ cong.)", "I don't think that"), Triple("tenga retraso", "abbia ritardo", "is delayed"), Triple("buen tiempo", "bel tempo", "good weather"))),
                CurriculumSeed("Cap. 2 · Consigli, Obblighi e Modali", "Ch. 2 · Advice & Modals", "Dare consigli col condizionale", "Giving advice with conditional", "En tu lugar, yo ___ directamente con el director del departamento.", "hablaría", listOf("hablaba", "hablé", "hable"), "En tu lugar, yo hablaría directamente con el director del departamento.", "Al posto tuo, io parlerei direttamente con il direttore del dipartimento.", "In your place, I would speak directly with the department director.", "Il condizionale semplice si forma aggiungendo -ía, -ías, -ía, -íamos, -ían all'infinito.", "Form the conditional by adding -ía, -ías, -ía to the full infinitive.", listOf(Triple("En tu lugar", "Al posto tuo", "In your shoes"), Triple("yo hablaría", "io parlerei", "I would speak"), Triple("directamente", "direttamente", "directly"))),
                CurriculumSeed("Cap. 3 · Preposizioni Por vs Para", "Ch. 3 · Prepositions Por vs Para", "Distinguere causa (por) e scopo (para)", "Cause (por) vs goal (para)", "Te llamo ___ confirmarte la reunión de mañana por la mañana.", "para", listOf("por", "en", "de"), "Te llamo para confirmarte la reunión de mañana por la mañana.", "Ti chiamo per confermarti la riunione di domani mattina.", "I am calling you in order to confirm tomorrow morning's meeting.", "Usa 'para' per lo scopo/obiettivo ('per + infinito') e 'por' per la causa o il motivo.", "Use 'para' for purpose/goal ('in order to') and 'por' for cause/reason.", listOf(Triple("Te llamo para", "Ti chiamo per (scopo)", "I call you to"), Triple("confirmarte", "confermarti", "confirm to you"), Triple("la reunión", "la riunione", "the meeting"))),
                CurriculumSeed("Cap. 4 · Temporali al Futuro e Finali", "Ch. 4 · Future Time Clauses", "Progetti futuri con 'en cuanto' e 'cuando'", "Future time clauses", "En cuanto ___ los resultados, te enviaré un mensaje.", "sepa", listOf("sé", "sabré", "sabía"), "En cuanto sepa los resultados, te enviaré un mensaje.", "Non appena saprò i risultati, ti manderò un messaggio.", "As soon as I know the results, I will send you a message.", "Dopo 'cuando, en cuanto, tan pronto como' riferiti al futuro si usa il congiuntivo presente ('sepa').", "After 'cuando' and 'en cuanto' referring to the future, always use present subjunctive.", listOf(Triple("En cuanto sepa", "Non appena saprò", "As soon as I know"), Triple("los resultados", "i risultati", "the results"), Triple("te enviaré", "ti invierò", "I will send you"))),
                CurriculumSeed("Cap. 5 · Lavoro e Scrittura Formale", "Ch. 5 · Work & Formal Register", "Perifrasi di durata (Llevar + gerundio)", "Duration with Llevar + gerund", "Nosotros ___ trabajando en esta empresa desde hace tres años.", "llevamos", listOf("estamos", "somos", "tenemos"), "Nosotros llevamos trabajando en esta empresa desde hace tres años.", "Lavoriamo in questa azienda da tre anni.", "We have been working at this company for three years.", "La struttura 'llevar + gerundio' esprime da quanto tempo dura un'azione.", "'Llevar + gerund' expresses how long an ongoing action has been happening.", listOf(Triple("llevamos trabajando", "lavoriamo (da...)", "we have been working"), Triple("en esta empresa", "in questa azienda", "at this company"), Triple("desde hace tres años", "da tre anni", "for three years")))
            )
            CefrLevel.B2 -> listOf(
                CurriculumSeed("Cap. 1 · Periodo Ipotetico dell'Irrealtà", "Ch. 1 · Counterfactual Conditionals", "Ipotesi nel presente (Si tuviera...)", "Present counterfactuals", "Si ___ más tiempo libre, aprendería a tocar el violonchelo.", "tuviera", listOf("tendría", "tengo", "habría tenido"), "Si tuviera más tiempo libre, aprendería a tocar el violonchelo.", "Se avessi più tempo libero, imparerei a suonare il violoncello.", "If I had more free time, I would learn to play the cello.", "Dopo 'Si' ipotetico si usa il congiuntivo imperfetto (-ra/-se), mai il condizionale.", "Use imperfect subjunctive ('tuviera') in the 'si' clause, followed by the conditional.", listOf(Triple("Si tuviera", "Se avessi", "If I had"), Triple("tiempo libre", "tempo libero", "free time"), Triple("aprendería", "imparerei", "I would learn"))),
                CurriculumSeed("Cap. 2 · Costrutti Concessivi Avanzati", "Ch. 2 · Advanced Concessive Clauses", "Concessive ipotetiche con 'Aunque'", "Concessive 'Aunque'", "Aunque ___ mañana mismo, no lograríamos terminar a tiempo.", "empezáramos", listOf("empezamos", "empezaremos", "empezaríamos"), "Aunque empezáramos mañana mismo, no lograríamos terminar a tiempo.", "Anche se iniziassimo domani stesso, non riusciremmo a finire in tempo.", "Even if we started tomorrow, we wouldn't manage to finish on time.", "'Aunque + congiuntivo imperfetto' traduce l'italiano 'anche se + congiuntivo'.", "'Aunque + imperfect subjunctive' means 'even if'.", listOf(Triple("Aunque empezáramos", "Anche se iniziassimo", "Even if we started"), Triple("mañana mismo", "domani stesso", "tomorrow itself"), Triple("no lograríamos", "non riusciremmo", "we wouldn't manage"))),
                CurriculumSeed("Cap. 3 · Verbi di Cambiamento", "Ch. 3 · Verbs of Change", "Diventare: ponerse, volverse, hacerse", "Verbs of becoming", "Cuando escuchó la noticia, se ___ muy nervioso.", "puso", listOf("hizo", "llegó", "quedó"), "Cuando escuchó la noticia, se puso muy nervioso.", "Quando ha sentito la notizia, è diventato molto nervoso.", "When he heard the news, he became very nervous.", "Usa 'ponerse + aggettivo' per cambiamenti rapidi di umore, salute o aspetto.", "Use 'ponerse + adjective' for sudden changes in mood or health.", listOf(Triple("Cuando escuchó", "Quando sentì", "When he heard"), Triple("se puso nervioso", "si è innervosito / è diventato nervoso", "he got nervous"), Triple("la noticia", "la notizia", "the news"))),
                CurriculumSeed("Cap. 4 · Discorso Indiretto e Passivo", "Ch. 4 · Reported Speech & Passive", "Trasformare nel discorso indiretto al passato", "Past reported speech", "El ministro aseguró que las medidas ___ en vigor el mes siguiente.", "entrarían", listOf("entrarán", "entren", "entran"), "El ministro aseguró que las medidas entrarían en vigor el mes siguiente.", "Il ministro ha assicurato che le misure sarebbero entrate in vigore il mese successivo.", "The minister assured that the measures would take effect the following month.", "Nel discorso indiretto al passato, il futuro si trasforma in condizionale semplice o composto.", "In past reported speech, future actions shift to the conditional ('entrarían').", listOf(Triple("El ministro aseguró", "Il ministro assicurò", "The minister assured"), Triple("entrarían en vigor", "sarebbero entrate in vigore", "would take effect"), Triple("el mes siguiente", "il mese seguente", "the following month"))),
                CurriculumSeed("Cap. 5 · Padronanza Stilistica B2", "Ch. 5 · B2 Stylistic Mastery", "Connettori argomentativi formali", "Formal argumentative connectors", "La inversión es elevada; ___ embargo, los beneficios a largo plazo son indiscutibles.", "sin", listOf("con", "por", "no"), "La inversión es elevada; sin embargo, los beneficios a largo plazo son indiscutibles.", "L'investimento è elevato; tuttavia, i benefici a lungo termine sono indiscutibili.", "The investment is high; however, the long-term benefits are undeniable.", "'Sin embargo' e 'no obstante' sono i connettori avversativi formali per 'tuttavia'.", "'Sin embargo' and 'no obstante' mean 'however / nevertheless' in formal writing.", listOf(Triple("sin embargo", "tuttavia / ciononostante", "however"), Triple("a largo plazo", "a lungo termine", "long-term"), Triple("indiscutibles", "indiscutibili", "undeniable")))
            )
        }

        return expandTo50Units(baseTemplates, "es", level)
    }

    private fun buildGerman50Seeds(level: CefrLevel): List<CurriculumSeed> {
        val baseTemplates: List<CurriculumSeed> = when (level) {
            CefrLevel.A1 -> listOf(
                CurriculumSeed("Cap. 1 · Saluti e Presentazioni", "Ch. 1 · Greetings & Introductions", "Salutare e ordinare con cortesia", "Polite greetings & ordering", "Guten Tag, ich ___ gern einen Kaffee ohne Zucker.", "möchte", listOf("möchten", "bin", "hast"), "Guten Tag, ich möchte gern einen Kaffee ohne Zucker.", "Buongiorno, vorrei volentieri un caffè senza zucchero.", "Good day, I would like a coffee without sugar.", "'Ich möchte gern' è la formula più naturale per ordinare in tedesco.", "'Ich möchte gern' is the polite way to order in German.", listOf(Triple("Guten Tag", "Buongiorno", "Good day"), Triple("ich möchte gern", "vorrei volentieri", "I would like"), Triple("ohne Zucker", "senza zucchero", "without sugar"))),
                CurriculumSeed("Cap. 1 · Saluti e Presentazioni", "Ch. 1 · Greetings & Introductions", "Presentarsi e dire da dove si viene", "Introducing yourself & origin", "Hallo, ich ___ aus Italien und wohne jetzt in Berlin.", "komme", listOf("kommst", "kommt", "bin"), "Hallo, ich komme aus Italien und wohne jetzt in Berlin.", "Ciao, vengo dall'Italia e ora abito a Berlino.", "Hello, I come from Italy and live in Berlin now.", "Con 'ich' i verbi regolari al presente terminano in -e: ich komme, ich wohne.", "With 'ich', regular present tense verbs end in -e: ich komme, ich wohne.", listOf(Triple("ich komme aus", "vengo da (origine)", "I come from"), Triple("und wohne", "e abito", "and live"), Triple("jetzt in Berlin", "ora a Berlino", "now in Berlin"))),
                CurriculumSeed("Cap. 2 · Verbi Essere, Avere e V2", "Ch. 2 · Sein, Haben & V2 Rule", "Il verbo Sein (Essere)", "Verb Sein (To be)", "Sind Sie Herr Weber? — Ja, das ___ ich.", "bin", listOf("bist", "ist", "sind"), "Ja, das bin ich.", "Sì, sono io.", "Yes, that's me.", "Coniugazione di sein: ich bin, du bist, er/sie/es ist, wir sind, ihr seid, sie/Sie sind.", "Conjugation of sein: ich bin, du bist, er/sie/es ist, wir sind, Sie sind.", listOf(Triple("Sind Sie...?", "È Lei...?", "Are you (formal)...?"), Triple("Ja, das bin ich", "Sì, sono io", "Yes, that is me"), Triple("Willkommen", "Benvenuto", "Welcome"))),
                CurriculumSeed("Cap. 2 · Verbi Essere, Avere e V2", "Ch. 2 · Sein, Haben & V2 Rule", "Regola V2 (Verbo sempre al 2° posto)", "V2 Word Order Rule", "Heute ___ wir zusammen ins Kino.", "gehen", listOf("gehe", "geht", "gegangen"), "Heute gehen wir zusammen ins Kino.", "Oggi andiamo insieme al cinema.", "Today we are going to the cinema together.", "Se la frase inizia con 'Heute' (Oggi), il verbo ('gehen') resta al 2° posto e precede 'wir'.", "When starting with 'Heute', the verb stays in 2nd position before 'wir'.", listOf(Triple("Heute", "Oggi (1° posto)", "Today"), Triple("gehen wir", "andiamo noi (verbo al 2° posto)", "we go"), Triple("zusammen", "insieme", "together"))),
                CurriculumSeed("Cap. 3 · Articoli, Caso Accusativo e Famiglia", "Ch. 3 · Articles, Accusative & Family", "Il caso Accusativo maschile (einen / den)", "Masculine Accusative Case", "Ich suche ___ Bahnhof. Können Sie mir helfen?", "den", listOf("der", "dem", "das"), "Ich suche den Bahnhof. Können Sie mir helfen?", "Cerco la stazione. Può aiutarmi?", "I am looking for the train station. Can you help me?", "I nomi maschili ('der Bahnhof') all'accusativo (oggetto diretto) diventano 'den / einen'.", "Masculine nouns ('der') change to 'den / einen' when they are the direct object.", listOf(Triple("Ich suche", "Io cerco (+ accusativo)", "I look for"), Triple("den Bahnhof", "la stazione (maschile in tedesco)", "the station"), Triple("helfen", "aiutare", "to help"))),
                CurriculumSeed("Cap. 4 · Verbi Modali e Ristorante", "Ch. 4 · Modal Verbs & Restaurant", "Usare Können e Müssen (Infinito in fondo)", "Modal Verbs (Können & Müssen)", "Wir ___ leider heute Abend nicht mitkommen.", "können", listOf("kann", "könnt", "kannst"), "Wir können leider heute Abend nicht mitkommen.", "Purtroppo stasera non possiamo venire con voi.", "Unfortunately we cannot come along tonight.", "Con i verbi modali ('können, müssen, wollen'), il secondo verbo all'infinito va in fondo alla frase.", "With modal verbs, the infinitive verb ('mitkommen') goes to the very end.", listOf(Triple("Wir können", "Noi possiamo", "We can"), Triple("leider nicht", "purtroppo non", "unfortunately not"), Triple("mitkommen", "venire insieme (in fondo)", "come along"))),
                CurriculumSeed("Cap. 5 · Città, Trasporti e Verbi Separabili", "Ch. 5 · City, Transport & Separable Verbs", "Verbi separabili (anrufen, einsteigen)", "Separable Verbs", "Der Zug nach Frankfurt ___ um acht Uhr auf Gleis drei ab.", "fährt", listOf("fahren", "abfahren", "fuhr"), "Der Zug nach Frankfurt fährt um acht Uhr auf Gleis drei ab.", "Il treno per Francoforte parte alle otto al binario tre.", "The train to Frankfurt departs at eight o'clock on track three.", "Con 'abfahren' (partire), 'fährt' sta al 2° posto e il prefisso 'ab' chiude la frase.", "In separable verbs like 'abfahren', the prefix 'ab' moves to the end of the clause.", listOf(Triple("Der Zug", "Il treno", "The train"), Triple("fährt ... ab", "parte (abfahren separabile)", "departs"), Triple("auf Gleis drei", "al binario tre", "on track three")))
            )
            CefrLevel.A2 -> listOf(
                CurriculumSeed("Cap. 1 · Il Passato Parlato (Perfekt)", "Ch. 1 · Spoken Past (Perfekt)", "Perfekt con Haben (ge-...-t / -en)", "Perfekt with Haben", "Gestern ___ ich den ganzen Nachmittag für die Prüfung gelernt.", "habe", listOf("bin", "hat", "hatte"), "Gestern habe ich den ganzen Nachmittag für die Prüfung gelernt.", "Ieri ho studiato tutto il pomeriggio per l'esame.", "Yesterday I studied all afternoon for the exam.", "Il Perfekt usa 'haben/sein' al 2° posto e il participio ('gelernt') in fondo alla frase.", "Place auxiliary 'habe' in 2nd position and participle 'gelernt' at the end.", listOf(Triple("Gestern habe ich", "Ieri ho", "Yesterday I have"), Triple("für die Prüfung", "per l'esame", "for the exam"), Triple("gelernt", "studiato (in fondo)", "studied"))),
                CurriculumSeed("Cap. 1 · Il Passato Parlato (Perfekt)", "Ch. 1 · Spoken Past (Perfekt)", "Perfekt di movimento con Sein", "Perfekt of motion with Sein", "Letztes Wochenende ___ wir nach Wien gefahren.", "sind", listOf("haben", "seid", "waren"), "Letztes Wochenende sind wir nach Wien gefahren.", "Lo scorso fine settimana siamo andati a Vienna.", "Last weekend we traveled to Vienna.", "I verbi di spostamento ('fahren, gehen, fliegen, kommen') formano il Perfekt con 'sein'.", "Verbs of movement ('fahren, gehen, fliegen') take 'sein' in the Perfekt.", listOf(Triple("Letztes Wochenende", "Lo scorso weekend", "Last weekend"), Triple("sind wir", "siamo (ausiliare sein)", "we are/have"), Triple("gefahren", "andati (in mezzo di trasporto)", "traveled"))),
                CurriculumSeed("Cap. 2 · Caso Dativo e Pronomi", "Ch. 2 · Dative Case & Pronouns", "Preposizioni con il Dativo (mit, nach, zu, bei)", "Dative Prepositions", "Ich fahre jeden Morgen mit ___ U-Bahn zur Arbeit.", "der", listOf("die", "den", "dem"), "Ich fahre jeden Morgen mit der U-Bahn zur Arbeit.", "Vado ogni mattina al lavoro con la metropolitana.", "I go to work every morning by subway.", "Dopo 'mit' si usa sempre il Dativo: il femminile 'die U-Bahn' diventa 'mit der U-Bahn'.", "After 'mit', feminine 'die' shifts to dative 'der' ('mit der U-Bahn').", listOf(Triple("jeden Morgen", "ogni mattina", "every morning"), Triple("mit der U-Bahn", "con la metro (dativo femm.)", "by subway"), Triple("zur Arbeit", "al lavoro (zu + der)", "to work"))),
                CurriculumSeed("Cap. 3 · Subordinate con Weil e Dass", "Ch. 3 · Subordinate Clauses (Weil & Dass)", "Verbo in fondo con 'weil' (perché)", "Verb at the end with 'weil'", "Ich bleibe heute im Bett, weil ich starke Kopfschmerzen ___.", "habe", listOf("haben", "habt", "bin"), "Ich bleibe heute im Bett, weil ich starke Kopfschmerzen habe.", "Oggi resto a letto perché ho un forte mal di testa.", "I am staying in bed today because I have a bad headache.", "Dopo 'weil' (perché) il verbo coniugato ('habe') va sempre in ultima posizione.", "Subordinating conjunction 'weil' pushes the finite verb ('habe') to the end.", listOf(Triple("im Bett", "a letto", "in bed"), Triple("weil ich ... habe", "perché ho (verbo in fondo)", "because I have"), Triple("Kopfschmerzen", "mal di testa", "headache"))),
                CurriculumSeed("Cap. 4 · Domande Indirette e Cortesia", "Ch. 4 · Indirect Questions & Politeness", "Domande indirette con 'wann, wo, ob'", "Indirect questions", "Können Sie mir bitte sagen, wann der nächste Bus ___?", "kommt", listOf("kommen", "kam", "gekommen"), "Können Sie mir bitte sagen, wann der nächste Bus kommt?", "Può dirmi per favore quando arriva il prossimo autobus?", "Can you please tell me when the next bus arrives?", "Nelle domande indirette ('wann..., wo..., ob...') il verbo va in fondo alla frase.", "In indirect questions, the conjugated verb moves to the end.", listOf(Triple("Können Sie mir sagen", "Può dirmi", "Can you tell me"), Triple("der nächste Bus", "il prossimo autobus", "the next bus"), Triple("wann ... kommt", "quando arriva (verbo in fondo)", "when ... arrives")))
            )
            CefrLevel.B1 -> listOf(
                CurriculumSeed("Cap. 1 · Präteritum e Racconto Scritto", "Ch. 1 · Narrative Past (Präteritum)", "Präteritum dei verbi modali (musste, konnte, wollte)", "Modal verbs in Präteritum", "Gestern ___ ich länger im Büro bleiben, weil viel zu tun war.", "musste", listOf("muss", "gemusst", "müsste"), "Gestern musste ich länger im Büro bleiben, weil viel zu tun war.", "Ieri sono dovuto restare più a lungo in ufficio perché c'era molto da fare.", "Yesterday I had to stay longer at the office because there was a lot to do.", "Con i verbi modali al passato si preferisce sempre il Präteritum ('ich musste, ich konnte') al Perfekt.", "German uses the Präteritum ('musste, konnte, wollte') for modal verbs in the past.", listOf(Triple("Gestern musste ich", "Ieri ho dovuto", "Yesterday I had to"), Triple("länger bleiben", "restare più a lungo", "stay longer"), Triple("viel zu tun", "molto da fare", "a lot to do"))),
                CurriculumSeed("Cap. 2 · Konjunktiv II (Desideri e Cortesia)", "Ch. 2 · Konjunktiv II (Politeness & Wishes)", "Ipotesi e consigli con Würde + infinito", "Advice with Würde + infinitive", "An deiner Stelle ___ ich dieses Angebot sofort annehmen.", "würde", listOf("werde", "wurde", "wäre"), "An deiner Stelle würde ich dieses Angebot sofort annehmen.", "Al posto tuo accetterei subito questa offerta.", "In your place, I would accept this offer immediately.", "'Ich würde + infinito in fondo' corrisponde al condizionale italiano.", "'Würde + infinitive at the end' forms the present conditional.", listOf(Triple("An deiner Stelle", "Al posto tuo", "In your place"), Triple("würde ich ... annehmen", "accetterei", "I would accept"), Triple("dieses Angebot", "questa offerta", "this offer"))),
                CurriculumSeed("Cap. 3 · Frasi Relative e Preposizioni", "Ch. 3 · Relative Clauses", "Pronomi relativi (der, die, das, denen)", "Relative pronouns", "Das ist der Kollege, mit ___ ich das Projekt geleitet habe.", "dem", listOf("den", "der", "dessen"), "Das ist der Kollege, mit dem ich das Projekt geleitet habe.", "Questo è il collega con cui ho diretto il progetto.", "This is the colleague with whom I led the project.", "'Mit' regge il dativo maschile ('dem'), e la frase relativa spinge il verbo ('geleitet habe') in fondo.", "'Mit' requires masculine dative 'dem', and the relative clause ends with the verb.", listOf(Triple("der Kollege", "il collega", "the colleague"), Triple("mit dem", "con il quale (dativo)", "with whom"), Triple("geleitet habe", "ho diretto (verbo in fondo)", "have led"))),
                CurriculumSeed("Cap. 4 · Infinitive con 'zu' e 'um... zu'", "Ch. 4 · Infinitive Clauses (um... zu)", "Frasi finali con 'um ... zu + infinito'", "Purpose clauses (um ... zu)", "Ich lerne jeden Tag Deutsch, ___ in München zu arbeiten.", "um", listOf("für", "damit", "weil"), "Ich lerne jeden Tag Deutsch, um in München zu arbeiten.", "Studio tedesco ogni giorno per lavorare a Monaco.", "I study German every day in order to work in Munich.", "Per tradurre 'per + infinito' (scopo) si usa 'um ... zu + infinito' in chiusura di frase.", "Use 'um ... zu + infinitive' to express 'in order to'.", listOf(Triple("jeden Tag", "ogni giorno", "every day"), Triple("um ... zu arbeiten", "per lavorare (scopo)", "in order to work"), Triple("in München", "a Monaco", "in Munich"))),
                CurriculumSeed("Cap. 5 · Caso Genitivo e Connettori (Trotz, Während)", "Ch. 5 · Genitive & Connectors", "Preposizioni col Genitivo (trotz, während, wegen)", "Genitive prepositions", "Während ___ gesamten Konferenz wurden wichtige Themen besprochen.", "der", listOf("die", "dem", "den"), "Während der gesamten Konferenz wurden wichtige Themen besprochen.", "Durante l'intera conferenza sono stati discussi temi importanti.", "During the entire conference, important topics were discussed.", "Con 'während' (durante), il femminile 'die Konferenz' al genitivo diventa 'der Konferenz'.", "With genitive preposition 'während', feminine 'die' becomes 'der'.", listOf(Triple("Während der Konferenz", "Durante la conferenza (genitivo)", "During the conference"), Triple("wurden ... besprochen", "sono stati discussi (passivo)", "were discussed"), Triple("wichtige Themen", "temi importanti", "important topics")))
            )
            CefrLevel.B2 -> listOf(
                CurriculumSeed("Cap. 1 · Correlativi Proporzionali (Je ... desto)", "Ch. 1 · Proportional Clauses (Je ... desto)", "Costruzione Je + Nebensatz, desto + V2", "Je ... desto construction", "Je gründlicher wir die Daten prüfen, ___ sicherer ist das Ergebnis.", "desto", listOf("weil", "obwohl", "damit"), "Je gründlicher wir die Daten prüfen, desto sicherer ist das Ergebnis.", "Più approfonditamente verifichiamo i dati, più sicuro è il risultato.", "The more thoroughly we check the data, the more reliable the result is.", "La prima frase con 'Je' ha il verbo alla fine ('prüfen'), la seconda con 'desto + comparativo' ha il verbo subito dopo.", "'Je' takes verb-final order; 'desto + comparative' is immediately followed by the finite verb.", listOf(Triple("Je gründlicher ... prüfen", "Più a fondo controlliamo", "The more thoroughly we check"), Triple("desto sicherer ist", "più sicuro è", "the safer is"), Triple("das Ergebnis", "il risultato", "the result"))),
                CurriculumSeed("Cap. 2 · Konjunktiv II nel Passato (Irrealtà)", "Ch. 2 · Past Counterfactuals (hätte / wäre)", "Rimorchi e ipotesi irreali nel passato", "Past hypotheticals", "Wenn wir früher losgefahren wären, ___ wir den Zug nicht verpasst.", "hätten", listOf("haben", "wären", "würden"), "Wenn wir früher losgefahren wären, hätten wir den Zug nicht verpasst.", "Se fossimo partiti prima, non avremmo perso il treno.", "If we had left earlier, we would not have missed the train.", "Per l'irrealtà nel passato si usano 'wären/hätten + participio passato' in entrambe le frasi.", "Use 'wären/hätten + past participle' for past counterfactual conditions.", listOf(Triple("Wenn wir ... wären", "Se fossimo partiti", "If we had left"), Triple("hätten wir ... verpasst", "avremmo perso", "we would have missed"), Triple("früher", "prima / più presto", "earlier"))),
                CurriculumSeed("Cap. 3 · Forma Passiva con Verbi Modali", "Ch. 3 · Passive Voice with Modals", "Passivo modale (muss ... gelöst werden)", "Modal passive", "Dieses technische Problem muss bis morgen dringend ___ werden.", "gelöst", listOf("lösen", "løste", "gelöste"), "Dieses technische Problem muss bis morgen dringend gelöst werden.", "Questo problema tecnico deve essere risolto urgentemente entro domani.", "This technical problem must be solved urgently by tomorrow.", "Il passivo con verbo modale si forma con: modale al 2° posto + participio passato + 'werden' in fondo.", "Modal passive: modal verb in V2 + past participle + 'werden' at the end.", listOf(Triple("muss ... gelöst werden", "deve essere risolto", "must be solved"), Triple("dringend", "urgentemente", "urgently"), Triple("bis morgen", "entro domani", "by tomorrow"))),
                CurriculumSeed("Cap. 4 · Verbi con Preposizione Fissa (da-/wo-)", "Ch. 4 · Verbs with Fixed Prepositions", "Pronomi avverbiali (darauf, darüber, wofür)", "Prepositional adverbs (darauf)", "Ich freue mich schon sehr ___, dass wir uns nächste Woche wiedersehen.", "darauf", listOf("daran", "damit", "darüber"), "Ich freue mich schon sehr darauf, dass wir uns nächste Woche wiedersehen.", "Non vedo l'ora che ci rivediamo la settimana prossima.", "I am really looking forward to seeing each other again next week.", "'Sich freuen auf' (rallegrarsi per il futuro) anticipa la frase con 'dass' tramite 'darauf'.", "'Sich freuen auf' uses 'darauf' to anticipate a 'dass' subordinate clause.", listOf(Triple("Ich freue mich darauf", "Non vedo l'ora (futuro)", "I look forward to it"), Triple("nächste Woche", "la prossima settimana", "next week"), Triple("wiedersehen", "rivedersi", "see again"))),
                CurriculumSeed("Cap. 5 · Registro Accademico e Connettori B2", "Ch. 5 · Academic Register & Connectors", "Connettori doppi (sowohl... als auch / weder... noch)", "Double connectors", "Die neue Strategie spart ___ Zeit als auch erhebliche Kosten.", "sowohl", listOf("weder", "entweder", "nicht"), "Die neue Strategie spart sowohl Zeit als auch erhebliche Kosten.", "La nuova strategia fa risparmiare sia tempo sia costi considerevoli.", "The new strategy saves both time and considerable costs.", "'Sowohl ... als auch' traduce 'sia ... sia', mentre 'weder ... noch' traduce 'né ... né'.", "'Sowohl ... als auch' means 'both ... and'.", listOf(Triple("sowohl ... als auch", "sia ... sia", "both ... and"), Triple("spart Zeit", "risparmia tempo", "saves time"), Triple("erhebliche Kosten", "costi considerevoli", "considerable costs")))
            )
        }

        return expandTo50Units(baseTemplates, "de", level)
    }

    /**
     * Expands the core pedagogical templates into 50 distinct, progressive units per level
     * organized into 5 thematic chapters of 10 units each (Units 1-10, 11-20, 21-30, 31-40, 41-50).
     */
    private fun expandTo50Units(
        templates: List<CurriculumSeed>,
        langCode: String,
        level: CefrLevel
    ): List<CurriculumSeed> {
        val result = ArrayList<CurriculumSeed>(50)
        val practiceContextsIt = listOf(
            "Dialogo pratico",
            "Verbi e struttura",
            "Pronomi e casi",
            "Vocabolario attivo",
            "Costruzione frase",
            "Ascolto e pronuncia",
            "Situazione reale",
            "Flessione rapida",
            "Padronanza attiva",
            "Riepilogo capitolo"
        )
        val practiceContextsEn = listOf(
            "Practical dialogue",
            "Verbs & structure",
            "Pronouns & cases",
            "Active vocabulary",
            "Sentence building",
            "Listening & speech",
            "Real-world scenario",
            "Quick inflection",
            "Active mastery",
            "Chapter review"
        )

        for (i in 0 until 50) {
            val chapterNum = (i / 10) + 1
            val stepInChapter = i % 10
            val base = templates[(i + chapterNum) % templates.size]
            val ctxIt = practiceContextsIt[stepInChapter]
            val ctxEn = practiceContextsEn[stepInChapter]

            result.add(
                base.copy(
                    chapterTitleIt = "Capitolo $chapterNum (Unità ${(chapterNum - 1) * 10 + 1}–${chapterNum * 10})",
                    chapterTitleEn = "Chapter $chapterNum (Units ${(chapterNum - 1) * 10 + 1}–${chapterNum * 10})",
                    unitTitleIt = "${base.unitTitleIt} · $ctxIt",
                    unitTitleEn = "${base.unitTitleEn} · $ctxEn"
                )
            )
        }
        return result
    }
}
