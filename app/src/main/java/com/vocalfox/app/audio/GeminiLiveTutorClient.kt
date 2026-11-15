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

/**
 * Direct REST client for Google Gemini Live AI Conversation Tutor.
 * Uses `models/gemini-3.8-flash` primarily, with automatic fallback to `models/gemini-2.5-flash` on 404.
 */
object GeminiLiveTutorClient {

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
            return@withContext Result.failure(IllegalArgumentException("API Key mancante"))
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

        val payload = JSONObject().apply {
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
        }

        val modelsToTry = listOf("gemini-3.8-flash", "gemini-2.5-flash")
        var lastError: Throwable? = null

        for (modelName in modelsToTry) {
            try {
                val endpoint = "https://generativelanguage.googleapis.com/v1beta/models/$modelName:generateContent?key=$cleanKey"
                val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = 15000
                    readTimeout = 20000
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                }

                OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { writer ->
                    writer.write(payload.toString())
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
                    return@withContext Result.success(
                        TutorChatMessage(
                            isUser = false,
                            text = parsed.optString("reply", "¡Muy bien! ¿Qué más me cuentas?"),
                            translation = parsed.optString("translation", ""),
                            grammarCorrection = parsed.optString("correction", "")
                        )
                    )
                } else {
                    lastError = RuntimeException("HTTP $code: $rawResponse")
                    // If 404 Not Found on primary model, loop continues to fallback model
                    if (code != 404) break
                }
            } catch (e: Throwable) {
                lastError = e
            }
        }

        Result.failure(lastError ?: RuntimeException("Errore di connessione a Gemini API"))
    }
}
