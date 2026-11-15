package com.vocalfox.app.audio

import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.ui.i18n.SystemLang
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

data class TutorChatMessage(
    val isUser: Boolean,
    val text: String,
    val translation: String = "",
    val grammarCorrection: String = ""
)

object GeminiLiveTutorClient {

    private const val CONNECT_TIMEOUT_MS = 2500
    private const val READ_TIMEOUT_MS = 12000

    @Volatile
    private var stickyModel: String? = null

    @Volatile
    private var resolvedHydrogenModel: String = "gemini-4-hydrogen"

    @Volatile
    private var hasResolvedModelsList: Boolean = false

    suspend fun preCheckHydrogenModelAsync(apiKey: String) = withContext(Dispatchers.IO) {
        val cleanKey = apiKey.trim()
        if (cleanKey.isBlank() || hasResolvedModelsList) return@withContext

        try {
            val endpoint = "https://generativelanguage.googleapis.com/v1beta/models?key=$cleanKey"
            val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = 4000
            }
            if (conn.responseCode in 200..299) {
                val raw = BufferedReader(InputStreamReader(conn.inputStream, Charsets.UTF_8)).use { it.readText() }
                val root = JSONObject(raw)
                val modelsArr = root.optJSONArray("models")
                if (modelsArr != null) {
                    hasResolvedModelsList = true
                    for (i in 0 until modelsArr.length()) {
                        val mObj = modelsArr.optJSONObject(i) ?: continue
                        val rawName = mObj.optString("name", "").removePrefix("models/")
                        if (rawName.contains("hydrogen", ignoreCase = true)) {
                            resolvedHydrogenModel = rawName
                            break
                        }
                    }
                }
            }
        } catch (_: Throwable) {}
    }

    private fun buildOrderedModelChain(): List<String> {
        val baseChain = listOf(
            "gemini-3.8-flash",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            resolvedHydrogenModel
        )
        val currentSticky = stickyModel
        return if (!currentSticky.isNullOrBlank()) {
            listOf(currentSticky) + baseChain.filterNot { it.equals(currentSticky, ignoreCase = true) }
        } else {
            baseChain.distinct()
        }
    }

    suspend fun sendMessageToTutor(
        apiKey: String,
        targetLanguageCode: String,
        cefrLevel: CefrLevel,
        systemLang: SystemLang,
        scenarioTitle: String,
        history: List<TutorChatMessage>,
        userMessage: String
    ): Result<TutorChatMessage> = withContext(Dispatchers.IO) {
        val cleanKey = apiKey.trim()
        if (cleanKey.isBlank()) {
            val msg = if (systemLang == SystemLang.IT) {
                "Inserisci la tua chiave API Gemini nella scheda Profilo o usa il pulsante ✨ in alto."
            } else {
                "Enter your Gemini API Key in the Profile tab or tap the ✨ button above."
            }
            return@withContext Result.failure(IllegalArgumentException(msg))
        }

        val targetLangName = if (targetLanguageCode == "de") "German (Deutsch)" else "Spanish (Español)"
        val uiLangName = if (systemLang == SystemLang.IT) "Italian" else "English"

        val systemInstruction = """
            You are Vocalfox, a warm, encouraging native $targetLangName language tutor.
            The student is currently at CEFR level ${cefrLevel.name}.
            Current roleplay scenario: "$scenarioTitle".
            Respond ONLY with a valid JSON object with exactly three string fields:
            {
              "reply": "Your natural conversational response in $targetLangName (2-3 sentences max, adapted to ${cefrLevel.name}, ending with an engaging follow-up question in $targetLangName)",
              "translation": "Accurate translation of your reply into $uiLangName",
              "correction": "Brief, friendly feedback in $uiLangName on the student's grammar/vocabulary (if their message was correct, praise it and suggest one idiomatic ${cefrLevel.name} expression)"
            }
        """.trimIndent()

        val contentsArray = JSONArray()
        history.takeLast(8).forEach { msg ->
            val role = if (msg.isUser) "user" else "model"
            val part = JSONObject().put("text", msg.text)
            val contentObj = JSONObject()
                .put("role", role)
                .put("parts", JSONArray().put(part))
            contentsArray.put(contentObj)
        }

        val userPart = JSONObject().put("text", userMessage)
        contentsArray.put(
            JSONObject()
                .put("role", "user")
                .put("parts", JSONArray().put(userPart))
        )

        val payloadString = JSONObject().apply {
            put(
                "system_instruction",
                JSONObject().put("parts", JSONArray().put(JSONObject().put("text", systemInstruction)))
            )
            put("contents", contentsArray)
            put(
                "generationConfig",
                JSONObject()
                    .put("temperature", 0.7)
                    .put("responseMimeType", "application/json")
            )
        }.toString()

        val modelsChain = buildOrderedModelChain()
        var encounteredAuthKeyError = false

        for (modelName in modelsChain) {
            try {
                val endpoint = "https://generativelanguage.googleapis.com/v1beta/models/$modelName:generateContent?key=$cleanKey"
                val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = CONNECT_TIMEOUT_MS
                    readTimeout = READ_TIMEOUT_MS
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                }

                OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { writer ->
                    writer.write(payloadString)
                }

                val code = conn.responseCode
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val rawResponse = if (stream != null) {
                    BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { it.readText() }
                } else {
                    ""
                }

                if (code in 200..299) {
                    val root = JSONObject(rawResponse)
                    val textOut = root.getJSONArray("candidates")
                        .getJSONObject(0)
                        .getJSONObject("content")
                        .getJSONArray("parts")
                        .getJSONObject(0)
                        .getString("text")
                        .trim()
                        .removePrefix("```json")
                        .removePrefix("```")
                        .removeSuffix("```")
                        .trim()

                    val parsed = JSONObject(textOut)
                    stickyModel = modelName

                    return@withContext Result.success(
                        TutorChatMessage(
                            isUser = false,
                            text = parsed.optString("reply", "¡Muy bien! ¿Qué más me cuentas?"),
                            translation = parsed.optString("translation", ""),
                            grammarCorrection = parsed.optString("correction", "")
                        )
                    )
                } else {
                    if (stickyModel == modelName) {
                        stickyModel = null
                    }
                    if (code == 400 || code == 403) {
                        if (rawResponse.contains("API_KEY_INVALID", ignoreCase = true) ||
                            rawResponse.contains("API key not valid", ignoreCase = true)
                        ) {
                            encounteredAuthKeyError = true
                            break
                        }
                    }
                }
            } catch (_: Throwable) {
                if (stickyModel == modelName) {
                    stickyModel = null
                }
            }
        }

        val friendlyMessage = if (encounteredAuthKeyError) {
            if (systemLang == SystemLang.IT) {
                "La chiave API Gemini inserita nel Profilo non è valida. Controllala o usa il pulsante ✨ in alto."
            } else {
                "The Gemini API key in Profile is invalid. Please check it or tap the ✨ button above."
            }
        } else {
            if (systemLang == SystemLang.IT) {
                "Tutti i modelli AI sono momentaneamente occupati, riprova tra pochi secondi oppure tocca ✨ in alto per usare l'app Gemini."
            } else {
                "All AI models are currently busy, please try again in a few seconds or tap ✨ above to use the Gemini app."
            }
        }

        Result.failure(RuntimeException(friendlyMessage))
    }
}
