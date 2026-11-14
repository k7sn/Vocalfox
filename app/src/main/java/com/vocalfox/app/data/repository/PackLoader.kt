package com.vocalfox.app.data.repository

import android.content.Context
import com.vocalfox.app.domain.model.LanguagePack
import kotlinx.serialization.json.Json

/**
 * Dynamically scans `assets/packs/` for `*_pack.json` files.
 * Dropping a new language pack into `assets/packs/` automatically registers it with zero code changes.
 */
class PackLoader(private val context: Context) {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    fun loadAllLanguagePacks(): Map<String, LanguagePack> {
        val packs = linkedMapOf<String, LanguagePack>()
        val files = context.assets.list("packs").orEmpty().filter { it.endsWith("_pack.json") }.sorted()

        for (fileName in files) {
            val rawJson = context.assets.open("packs/$fileName").bufferedReader().use { it.readText() }
            val pack = json.decodeFromString<LanguagePack>(rawJson)
            packs[pack.languageCode] = pack
        }
        return packs
    }
}
