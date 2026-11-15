#!/usr/bin/env python3
"""
update_vocalfox.py
Riprogettazione UI pulita (heydamir-unslop + Duolingo reference layout):
- Fix definitivo testi verticali ("I-n-i-z-i-a" e tabelle Accademia)
- Splash screen con riproduzione garantita del VIDEO animato (splash_screen.webp) + immagine grafica vocalfox
- Nome ufficiale dell'app: Vocalfox (con 'f' minuscola ovunque)
- Rimozione font Monospace fuori luogo e scritte ridondanti/troncate
- Barra di navigazione inferiore pulita che non copre mai le card
- Schermata Profilo in stile card statistiche (come negli screenshot di riferimento)
"""

import shutil
from pathlib import Path

FILES: dict[str, str] = {
    "settings.gradle.kts": """\
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "Vocalfox"
include(":app")
""",

    "app/src/main/AndroidManifest.xml": """\
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.INTERNET" />

    <queries>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
        <intent>
            <action android:name="android.speech.RecognitionService" />
        </intent>
    </queries>

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:label="Vocalfox"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
""",

    "app/src/main/java/com/vocalfox/app/ui/theme/Type.kt": """\
package com.vocalfox.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * Unslop Typography Scale
 * - Un'unica famiglia Sans-Serif pulita per tutta l'interfaccia (niente Monospace da terminale!)
 * - Pesi 400 (Normal), 500 (Medium) e 600 (SemiBold)
 * - Numeri tabulari (`tnum`) per contatori e statistiche
 */
object VocalFoxType {
    val Sans = FontFamily.SansSerif

    val PageTitle = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 30.sp,
        letterSpacing = (-0.3).sp
    )

    val SectionTitle = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.SemiBold,
        fontSize = 17.sp,
        lineHeight = 23.sp,
        letterSpacing = 0.sp
    )

    val CardFigure = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 28.sp,
        fontFeatureSettings = "tnum"
    )

    val SentenceDisplay = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 19.sp,
        lineHeight = 26.sp,
        letterSpacing = 0.sp
    )

    val Body = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        lineHeight = 21.sp,
        letterSpacing = 0.sp
    )

    val BodyMedium = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 15.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.sp
    )

    val SecondaryCaption = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Normal,
        fontSize = 13.sp,
        lineHeight = 18.sp,
        letterSpacing = 0.sp
    )

    val MetaMono = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.sp,
        fontFeatureSettings = "tnum"
    )
}

val VocalFoxMaterialTypography = Typography(
    headlineLarge = VocalFoxType.PageTitle,
    headlineMedium = VocalFoxType.SectionTitle,
    bodyLarge = VocalFoxType.Body,
    bodyMedium = VocalFoxType.BodyMedium,
    labelSmall = VocalFoxType.MetaMono
)
""",

    "app/src/main/java/com/vocalfox/app/ui/theme/VocalFoxMascot.kt": """\
package com.vocalfox.app.ui.theme

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageDecoder
import android.graphics.drawable.AnimatedImageDrawable
import android.os.Build
import android.widget.ImageView
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import java.util.ArrayDeque

enum class MascotState(val drawableName: String) {
    LOGO_IDLE("mascot_idle"),
    CELEBRATE("mascot_celebrate"),
    THINKING("mascot_thinking"),
    STRICT_COACH("mascot_strict"),
    ENCOURAGE_SAD("mascot_sad"),
    SLEEPING("mascot_sleeping")
}

object MascotBitmapCache {
    private val cache = mutableMapOf<String, ImageBitmap>()

    fun getTrimmedBitmap(
        context: Context,
        resourceName: String,
        stripBackground: Boolean = true
    ): ImageBitmap? {
        val cacheKey = "${resourceName}_$stripBackground"
        cache[cacheKey]?.let { return it }

        val resId = context.resources.getIdentifier(resourceName, "drawable", context.packageName)
        if (resId == 0) return null

        val options = BitmapFactory.Options().apply {
            inPreferredConfig = Bitmap.Config.ARGB_8888
        }
        val raw = BitmapFactory.decodeResource(context.resources, resId, options) ?: return null
        if (!stripBackground) {
            val img = raw.asImageBitmap()
            cache[cacheKey] = img
            return img
        }

        val processed = floodFillOuterBackgroundAndCrop(raw)
        val result = processed.asImageBitmap()
        cache[cacheKey] = result
        return result
    }

    private fun floodFillOuterBackgroundAndCrop(src: Bitmap): Bitmap {
        val w = src.width
        val h = src.height
        if (w <= 4 || h <= 4) return src

        val pixels = IntArray(w * h)
        src.getPixels(pixels, 0, w, 0, 0, w, h)

        val corners = intArrayOf(
            pixels[0],
            pixels[w - 1],
            pixels[(h - 1) * w],
            pixels[(h - 1) * w + (w - 1)]
        )

        var detectBlackBg = false
        var detectWhiteBg = false
        for (c in corners) {
            val a = (c ushr 24) and 0xFF
            val r = (c ushr 16) and 0xFF
            val g = (c ushr 8) and 0xFF
            val b = c and 0xFF
            if (a > 30 && r < 48 && g < 48 && b < 48) detectBlackBg = true
            if (a > 30 && r > 222 && g > 222 && b > 222) detectWhiteBg = true
        }

        if (detectBlackBg || detectWhiteBg) {
            val visited = BooleanArray(w * h)
            val queue = ArrayDeque<Int>(w * 2 + h * 2)

            fun matchesBg(color: Int): Boolean {
                val a = (color ushr 24) and 0xFF
                if (a < 25) return true
                val r = (color ushr 16) and 0xFF
                val g = (color ushr 8) and 0xFF
                val b = color and 0xFF
                if (detectBlackBg && r < 52 && g < 52 && b < 52) return true
                if (detectWhiteBg && r > 220 && g > 220 && b > 220) return true
                return false
            }

            fun enqueueIfBg(x: Int, y: Int) {
                val idx = y * w + x
                if (!visited[idx] && matchesBg(pixels[idx])) {
                    visited[idx] = true
                    queue.addLast(idx)
                }
            }

            for (x in 0 until w) {
                enqueueIfBg(x, 0)
                enqueueIfBg(x, h - 1)
            }
            for (y in 0 until h) {
                enqueueIfBg(0, y)
                enqueueIfBg(w - 1, y)
            }

            while (!queue.isEmpty()) {
                val idx = queue.removeFirst()
                pixels[idx] = 0x00000000
                val x = idx % w
                val y = idx / w
                if (x > 0) enqueueIfBg(x - 1, y)
                if (x < w - 1) enqueueIfBg(x + 1, y)
                if (y > 0) enqueueIfBg(x, y - 1)
                if (y < h - 1) enqueueIfBg(x, y + 1)
            }
        }

        var minX = w
        var minY = h
        var maxX = 0
        var maxY = 0

        for (y in 0 until h) {
            val rowOffset = y * w
            for (x in 0 until w) {
                val a = (pixels[rowOffset + x] ushr 24) and 0xFF
                if (a > 25) {
                    if (x < minX) minX = x
                    if (x > maxX) maxX = x
                    if (y < minY) minY = y
                    if (y > maxY) maxY = y
                }
            }
        }

        val cleaned = Bitmap.createBitmap(pixels, w, h, Bitmap.Config.ARGB_8888)
        if (maxX <= minX || maxY <= minY) return cleaned

        val padX = ((maxX - minX) * 0.02f).toInt().coerceAtLeast(2)
        val padY = ((maxY - minY) * 0.02f).toInt().coerceAtLeast(2)
        val cropLeft = (minX - padX).coerceAtLeast(0)
        val cropTop = (minY - padY).coerceAtLeast(0)
        val cropRight = (maxX + padX).coerceAtMost(w - 1)
        val cropBottom = (maxY + padY).coerceAtMost(h - 1)

        return Bitmap.createBitmap(
            cleaned,
            cropLeft,
            cropTop,
            (cropRight - cropLeft + 1).coerceAtLeast(1),
            (cropBottom - cropTop + 1).coerceAtLeast(1)
        )
    }
}

/**
 * Carica l'immagine grafica `vocalfox_text.png` (o `vocalfox.png`) da `res/drawable-nodpi/`
 * rimuovendo eventuale sfondo nero/bianco e mostrandola al posto del testo.
 */
@Composable
fun VocalFoxWordmark(
    height: Dp = 32.dp,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val wordmarkBitmap = remember {
        MascotBitmapCache.getTrimmedBitmap(context, "vocalfox_text", stripBackground = true)
            ?: MascotBitmapCache.getTrimmedBitmap(context, "vocalfox", stripBackground = true)
    }

    if (wordmarkBitmap != null) {
        Image(
            bitmap = wordmarkBitmap,
            contentDescription = "Vocalfox",
            contentScale = ContentScale.Fit,
            modifier = modifier.height(height)
        )
    } else {
        Text(
            text = "Vocalfox",
            style = VocalFoxType.PageTitle.copy(
                fontWeight = FontWeight.SemiBold,
                fontSize = (height.value * 0.78f).sp,
                color = VocalFoxPalette.FoxFurOrange
            ),
            modifier = modifier
        )
    }
}

@Composable
fun VocalFoxMascot(
    state: MascotState,
    modifier: Modifier = Modifier,
    size: Dp = 64.dp,
    useLogoEmblem: Boolean = false,
    tintBackground: Color? = null
) {
    val context = LocalContext.current

    val imageBitmap = remember(state, useLogoEmblem) {
        val resourceName = if (useLogoEmblem) "logo" else state.drawableName
        MascotBitmapCache.getTrimmedBitmap(
            context = context,
            resourceName = resourceName,
            stripBackground = !useLogoEmblem
        )
    }

    val containerBg = when {
        tintBackground != null -> tintBackground
        useLogoEmblem -> VocalFoxPalette.FoxLogoBrownBackdrop
        else -> Color.Transparent
    }

    Box(
        modifier = modifier
            .size(size)
            .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
            .background(containerBg),
        contentAlignment = Alignment.Center
    ) {
        if (imageBitmap != null) {
            Image(
                bitmap = imageBitmap,
                contentDescription = state.name,
                contentScale = ContentScale.Fit,
                modifier = Modifier.fillMaxSize(if (useLogoEmblem) 1f else 0.90f)
            )
        } else {
            VectorFoxFallback(state = state, size = size * 0.86f)
        }
    }
}

/**
 * Riproduce SEMPRE il VIDEO animato `splash_screen.webp` tramite `ImageDecoder` + `AnimatedImageDrawable`!
 * Non usa più l'immagine statica quando `splash_screen.webp` è presente.
 */
@Composable
fun AnimatedWebpSplashPlayer(
    modifier: Modifier = Modifier,
    size: Dp = 240.dp
) {
    val context = LocalContext.current
    val splashResId = remember {
        context.resources.getIdentifier("splash_screen", "drawable", context.packageName)
    }

    if (splashResId != 0 && Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
        AndroidView(
            modifier = modifier.size(size),
            factory = { ctx ->
                ImageView(ctx).apply {
                    setBackgroundColor(android.graphics.Color.TRANSPARENT)
                    scaleType = ImageView.ScaleType.FIT_CENTER
                    try {
                        val source = ImageDecoder.createSource(ctx.resources, splashResId)
                        val drawable = ImageDecoder.decodeDrawable(source)
                        setImageDrawable(drawable)
                        if (drawable is AnimatedImageDrawable) {
                            drawable.repeatCount = AnimatedImageDrawable.REPEAT_INFINITE
                            drawable.start()
                        }
                    } catch (_: Throwable) {}
                }
            },
            update = { imageView ->
                val d = imageView.drawable
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P && d is AnimatedImageDrawable && !d.isRunning) {
                    d.start()
                }
            }
        )
    } else {
        VocalFoxMascot(
            state = MascotState.CELEBRATE,
            size = size,
            modifier = modifier
        )
    }
}

@Composable
private fun VectorFoxFallback(state: MascotState, size: Dp) {
    Canvas(modifier = Modifier.size(size)) {
        val w = this.size.width
        val h = this.size.height

        val leftEar = Path().apply {
            moveTo(w * 0.18f, h * 0.42f)
            lineTo(w * 0.24f, h * 0.10f)
            lineTo(w * 0.44f, h * 0.28f)
            close()
        }
        val rightEar = Path().apply {
            moveTo(w * 0.82f, h * 0.42f)
            lineTo(w * 0.76f, h * 0.10f)
            lineTo(w * 0.56f, h * 0.28f)
            close()
        }
        drawPath(leftEar, VocalFoxPalette.FoxFurOrange)
        drawPath(rightEar, VocalFoxPalette.FoxFurOrange)

        val leftTip = Path().apply {
            moveTo(w * 0.21f, h * 0.24f)
            lineTo(w * 0.24f, h * 0.10f)
            lineTo(w * 0.34f, h * 0.19f)
            close()
        }
        val rightTip = Path().apply {
            moveTo(w * 0.79f, h * 0.24f)
            lineTo(w * 0.76f, h * 0.10f)
            lineTo(w * 0.66f, h * 0.19f)
            close()
        }
        drawPath(leftTip, VocalFoxPalette.FoxDeepInkBrown)
        drawPath(rightTip, VocalFoxPalette.FoxDeepInkBrown)

        drawRoundRect(
            color = VocalFoxPalette.FoxFurOrange,
            topLeft = Offset(w * 0.15f, h * 0.25f),
            size = Size(w * 0.70f, h * 0.58f),
            cornerRadius = CornerRadius(w * 0.28f, w * 0.28f)
        )

        drawRoundRect(
            color = VocalFoxPalette.FoxMuzzleTint,
            topLeft = Offset(w * 0.18f, h * 0.52f),
            size = Size(w * 0.64f, h * 0.30f),
            cornerRadius = CornerRadius(w * 0.22f, w * 0.22f)
        )

        val eyeY = h * 0.46f
        when (state) {
            MascotState.SLEEPING -> {
                drawLine(VocalFoxPalette.FoxDeepInkBrown, Offset(w * 0.28f, eyeY), Offset(w * 0.42f, eyeY), 4f)
                drawLine(VocalFoxPalette.FoxDeepInkBrown, Offset(w * 0.58f, eyeY), Offset(w * 0.72f, eyeY), 4f)
            }
            MascotState.CELEBRATE -> {
                drawArc(VocalFoxPalette.FoxDeepInkBrown, 180f, 180f, false, Offset(w * 0.28f, eyeY - 8f), Size(w * 0.14f, 16f), style = Stroke(4.5f))
                drawArc(VocalFoxPalette.FoxDeepInkBrown, 180f, 180f, false, Offset(w * 0.58f, eyeY - 8f), Size(w * 0.14f, 16f), style = Stroke(4.5f))
            }
            else -> {
                drawCircle(Color.White, radius = w * 0.09f, center = Offset(w * 0.35f, eyeY))
                drawCircle(Color.White, radius = w * 0.09f, center = Offset(w * 0.65f, eyeY))
                drawCircle(VocalFoxPalette.FoxDeepInkBrown, radius = w * 0.055f, center = Offset(w * 0.35f, eyeY))
                drawCircle(VocalFoxPalette.FoxDeepInkBrown, radius = w * 0.055f, center = Offset(w * 0.65f, eyeY))
                drawCircle(Color.White, radius = w * 0.02f, center = Offset(w * 0.33f, eyeY - 3f))
                drawCircle(Color.White, radius = w * 0.02f, center = Offset(w * 0.63f, eyeY - 3f))
            }
        }

        drawCircle(VocalFoxPalette.FoxDeepInkBrown, radius = w * 0.045f, center = Offset(w * 0.50f, h * 0.58f))

        val mouthStartAngle = if (state == MascotState.STRICT_COACH || state == MascotState.ENCOURAGE_SAD) 190f else 10f
        drawArc(
            color = VocalFoxPalette.FoxDeepInkBrown,
            startAngle = mouthStartAngle,
            sweepAngle = 160f,
            useCenter = false,
            topLeft = Offset(w * 0.42f, h * 0.63f),
            size = Size(w * 0.16f, h * 0.08f),
            style = Stroke(width = 4f)
        )
    }
}

@Composable
fun MascotPedagogicalBanner(
    state: MascotState,
    title: String,
    subtitle: String,
    modifier: Modifier = Modifier,
    metaBadge: String? = null
) {
    val colors = VocalFoxTheme.colors

    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
            .background(colors.card)
            .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
            .padding(16.dp),
        horizontalArrangement = Arrangement.spacedBy(14.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        VocalFoxMascot(
            state = state,
            size = 60.dp,
            tintBackground = if (colors.isDark) colors.raised else VocalFoxPalette.TintWarmAmber
        )

        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = title,
                    style = VocalFoxType.BodyMedium,
                    color = colors.primaryText
                )
                if (metaBadge != null) {
                    Text(
                        text = metaBadge,
                        style = VocalFoxType.MetaMono,
                        color = colors.accent,
                        modifier = Modifier
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                            .background(colors.raised)
                            .padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
            Text(
                text = subtitle,
                style = VocalFoxType.SecondaryCaption,
                color = colors.secondaryText
            )
        }
    }
}
""",

    "app/src/main/java/com/vocalfox/app/data/repository/CurriculumGenerator.kt": """\
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
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/HomeScreen.kt": """\
package com.vocalfox.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.LocalFireDepartment
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.vocalfox.app.data.local.UserProgressEntity
import com.vocalfox.app.data.repository.CurriculumGenerator
import com.vocalfox.app.domain.model.CefrLevel
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.VocalFoxMascot
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.theme.VocalFoxWordmark

@Composable
fun HomeScreen(
    allPacks: Map<String, LanguagePack>,
    currentPack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang,
    strings: UiStrings,
    progressList: List<UserProgressEntity>,
    onSelectLanguage: (String) -> Unit,
    onSelectCefr: (CefrLevel) -> Unit,
    onStartGuidedUnit: (GuidedUnitBundle) -> Unit,
    onOpenProfileSettings: () -> Unit
) {
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    val all50Units = remember(currentPack.languageCode, selectedCefr, systemLang) {
        CurriculumGenerator.generate50UnitsForLevel(currentPack, selectedCefr, systemLang)
    }

    var selectedChapterFilter by remember(selectedCefr) { mutableIntStateOf(0) }
    val displayedUnits = remember(all50Units, selectedChapterFilter) {
        if (selectedChapterFilter == 0) {
            all50Units
        } else {
            val startIdx = (selectedChapterFilter - 1) * 10
            all50Units.subList(startIdx, (startIdx + 10).coerceAtMost(all50Units.size))
        }
    }

    val completedCount = progressList.count { it.bestScore >= 70 }
    val realStreakDays = remember(progressList) {
        calculateConsecutiveDayStreak(progressList)
    }

    val dailyTarget = 4
    val completedToday = remember(progressList) {
        val todayDayIndex = System.currentTimeMillis() / 86_400_000L
        progressList.count { (it.completedAtEpochMs / 86_400_000L) == todayDayIndex && it.bestScore >= 70 }
    }
    val dailyProgressRatio = (completedToday.toFloat() / dailyTarget.toFloat()).coerceIn(0f, 1f)

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // TOP BAR: Immagine Vocalfox a sinistra + Badge Lingua e Streak a destra
        item {
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                VocalFoxWordmark(height = 32.dp)

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Badge corso attivo (cliccabile per cambiare lingua nel Profilo)
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                            .clickable(onClick = onOpenProfileSettings)
                            .padding(horizontal = 12.dp, vertical = 7.dp)
                    ) {
                        Text(
                            text = "${currentPack.languageName.get(systemLang)} · ${selectedCefr.name}",
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                    }

                    // Streak reale
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(12.dp))
                            .padding(horizontal = 10.dp, vertical = 7.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.LocalFireDepartment,
                            contentDescription = null,
                            tint = if (realStreakDays > 0) colors.accent else colors.mutedText,
                            modifier = Modifier.size(18.dp)
                        )
                        Text(
                            text = "$realStreakDays",
                            style = VocalFoxType.BodyMedium,
                            color = colors.primaryText
                        )
                    }
                }
            }
        }

        // SELETTORE LIVELLO PULITO (A1, A2, B1, B2)
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CefrLevel.entries.forEach { level ->
                    val isSelected = level == selectedCefr
                    val doneInLevel = progressList.count { it.cefrLevel == level.name && it.bestScore >= 70 }
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (isSelected) colors.accent else colors.card)
                            .border(
                                width = 1.dp,
                                color = if (isSelected) colors.accent else colors.hairline,
                                shape = RoundedCornerShape(14.dp)
                            )
                            .clickable { onSelectCefr(level) }
                            .padding(vertical = 10.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(2.dp)
                    ) {
                        Text(
                            text = level.name,
                            style = VocalFoxType.SectionTitle,
                            color = if (isSelected) colors.onAccent else colors.primaryText,
                            maxLines = 1
                        )
                        Text(
                            text = "$doneInLevel/50",
                            style = VocalFoxType.SecondaryCaption,
                            color = if (isSelected) colors.onAccent.copy(alpha = 0.85f) else colors.mutedText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        // OBIETTIVO GIORNALIERO COMPATTO
        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(16.dp))
                    .padding(16.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(68.dp),
                    contentAlignment = Alignment.Center
                ) {
                    val trackCol = colors.raised
                    val arcCol = colors.accent
                    Canvas(modifier = Modifier.fillMaxSize()) {
                        drawArc(
                            color = trackCol,
                            startAngle = 135f,
                            sweepAngle = 270f,
                            useCenter = false,
                            style = Stroke(width = 16f, cap = StrokeCap.Round)
                        )
                        if (dailyProgressRatio > 0f) {
                            drawArc(
                                color = arcCol,
                                startAngle = 135f,
                                sweepAngle = 270f * dailyProgressRatio,
                                useCenter = false,
                                style = Stroke(width = 16f, cap = StrokeCap.Round)
                            )
                        }
                    }
                    Text(
                        text = "$completedToday/$dailyTarget",
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )
                }

                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = strings.dailyGoalTitle,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    Text(
                        text = if (isIt) "$completedCount unità completate in totale" else "$completedCount total units completed",
                        style = VocalFoxType.SecondaryCaption,
                        color = colors.secondaryText
                    )
                }
            }
        }

        // FILTRO CAPITOLI (Tutte, 1-10, 11-20, 21-30, 31-40, 41-50)
        item {
            val chapterFilters = listOf(
                0 to (if (isIt) "Tutte" else "All"),
                1 to "1–10",
                2 to "11–20",
                3 to "21–30",
                4 to "31–40",
                5 to "41–50"
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                chapterFilters.forEach { (chapIdx, label) ->
                    val active = selectedChapterFilter == chapIdx
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(10.dp))
                            .background(if (active) colors.primaryText else colors.card)
                            .border(1.dp, colors.hairline, RoundedCornerShape(10.dp))
                            .clickable { selectedChapterFilter = chapIdx }
                            .padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = if (chapIdx == 0) label else (if (isIt) "Unità $label" else "Units $label"),
                            style = VocalFoxType.BodyMedium,
                            color = if (active) colors.background else colors.secondaryText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        // LISTA DELLE 50 UNITÀ (Card pulite, zero testo spezzato in verticale!)
        itemsIndexed(displayedUnits, key = { _, u -> u.grammarExercise.id }) { idx, unit ->
            val isCompleted = progressList.any { it.itemKey == unit.grammarExercise.id && it.bestScore >= 70 }
            val isNextActive = idx == 0 || !isCompleted

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier
                        .width(16.dp)
                        .fillMaxHeight()
                ) {
                    Spacer(modifier = Modifier.height(22.dp))
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                            .background(
                                when {
                                    isCompleted -> colors.positive
                                    idx == 0 -> colors.accent
                                    else -> colors.raised
                                }
                            )
                            .border(
                                width = 2.dp,
                                color = if (isNextActive) colors.accent else colors.mutedText.copy(alpha = 0.35f),
                                shape = CircleShape
                            )
                    )
                    if (idx < displayedUnits.lastIndex) {
                        Box(
                            modifier = Modifier
                                .width(2.dp)
                                .weight(1f)
                                .padding(vertical = 4.dp)
                                .background(colors.hairline)
                        )
                    }
                }

                // Card Unità Pulita
                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(16.dp))
                        .background(colors.card)
                        .border(
                            width = if (idx == 0) 1.5.dp else 1.dp,
                            color = if (idx == 0) colors.accent.copy(alpha = 0.5f) else colors.hairline,
                            shape = RoundedCornerShape(16.dp)
                        )
                        .clickable { onStartGuidedUnit(unit) }
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = if (isIt) "Unità ${unit.unitIndex + 1}" else "Unit ${unit.unitIndex + 1}",
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.accent,
                            maxLines = 1
                        )
                        Text(
                            text = unit.title,
                            style = VocalFoxType.SectionTitle,
                            color = colors.primaryText,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            text = unit.subtitle,
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )

                        Spacer(modifier = Modifier.height(2.dp))

                        // Bottone orizzontale pulito che non va MAI a capo lettera per lettera
                        Row(
                            modifier = Modifier
                                .clip(RoundedCornerShape(10.dp))
                                .background(if (isCompleted) colors.positive.copy(alpha = 0.12f) else colors.accent)
                                .padding(horizontal = 14.dp, vertical = 7.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = if (isCompleted) Icons.Outlined.Check else Icons.Outlined.PlayArrow,
                                contentDescription = null,
                                tint = if (isCompleted) colors.positive else colors.onAccent,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = if (isCompleted) (if (isIt) "Completata" else "Completed") else strings.startUnitAction,
                                style = VocalFoxType.BodyMedium,
                                color = if (isCompleted) colors.positive else colors.onAccent,
                                maxLines = 1
                            )
                        }
                    }

                    VocalFoxMascot(
                        state = unit.mascotPose,
                        size = 76.dp,
                        tintBackground = unit.tintColor
                    )
                }
            }
        }

        item { Spacer(modifier = Modifier.height(24.dp)) }
    }
}

private fun calculateConsecutiveDayStreak(progressList: List<UserProgressEntity>): Int {
    val completedDays = progressList
        .filter { it.bestScore >= 70 && it.completedAtEpochMs > 0L }
        .map { it.completedAtEpochMs / 86_400_000L }
        .distinct()
        .sortedDescending()

    if (completedDays.isEmpty()) return 0

    val today = System.currentTimeMillis() / 86_400_000L
    if (completedDays.first() < today - 1) return 0

    var streak = 1
    for (i in 0 until completedDays.lastIndex) {
        if (completedDays[i] - completedDays[i + 1] == 1L) {
            streak++
        } else {
            break
        }
    }
    return streak
}

fun buildGuidedUnitsForPack(
    pack: LanguagePack,
    selectedCefr: CefrLevel,
    systemLang: SystemLang
): List<GuidedUnitBundle> {
    return CurriculumGenerator.generate50UnitsForLevel(pack, selectedCefr, systemLang)
}
""",

    "app/src/main/java/com/vocalfox/app/ui/screens/ExploreStudyHubScreen.kt": """\
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
""",

    "app/src/main/java/com/vocalfox/app/MainActivity.kt": """\
package com.vocalfox.app

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Explore
import androidx.compose.material.icons.outlined.Forum
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModelProvider
import com.vocalfox.app.ui.i18n.AppStrings
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.screens.ExploreStudyHubScreen
import com.vocalfox.app.ui.screens.GuidedLessonScreen
import com.vocalfox.app.ui.screens.GuidedUnitBundle
import com.vocalfox.app.ui.screens.HomeScreen
import com.vocalfox.app.ui.screens.LiveConversationScreen
import com.vocalfox.app.ui.screens.OnboardingScreen
import com.vocalfox.app.ui.screens.SettingsVoiceScreen
import com.vocalfox.app.ui.screens.SplashScreenOverlay
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxType
import com.vocalfox.app.ui.viewmodel.VocalFoxViewModel
import kotlinx.coroutines.delay

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val vm = ViewModelProvider(
            this,
            ViewModelProvider.AndroidViewModelFactory.getInstance(application)
        )[VocalFoxViewModel::class.java]

        setContent {
            val isDark by vm.isDarkMode.collectAsState()
            VocalFoxTheme(darkTheme = isDark) {
                VocalFoxRootApp(viewModel = vm)
            }
        }
    }
}

private enum class MainTab {
    TODAY, EXPLORE, LIVE_AI, PROFILE
}

@Composable
private fun VocalFoxRootApp(viewModel: VocalFoxViewModel) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("vocalfox_prefs", Context.MODE_PRIVATE) }

    val colors = VocalFoxTheme.colors
    val systemLang by viewModel.systemLang.collectAsState()
    val isDarkMode by viewModel.isDarkMode.collectAsState()
    val currentPack by viewModel.currentPack.collectAsState()
    val selectedCefr by viewModel.selectedCefr.collectAsState()
    val progressList by viewModel.progressList.collectAsState()
    val voiceConfigs by viewModel.voiceConfigs.collectAsState()
    val isRecording by viewModel.isRecordingAudio.collectAsState()
    val pronunciationResult by viewModel.latestPronunciationResult.collectAsState()

    val strings = AppStrings.forLang(systemLang)

    var showSplash by rememberSaveable { mutableStateOf(true) }
    var hasCompletedOnboarding by rememberSaveable {
        mutableStateOf(prefs.getBoolean("onboarding_done", false))
    }
    var activeTab by rememberSaveable { mutableStateOf(MainTab.TODAY) }
    var activeGuidedUnit by remember { mutableStateOf<GuidedUnitBundle?>(null) }

    LaunchedEffect(Unit) {
        viewModel.setSystemLanguage(SystemLang.IT)
        delay(2200L)
        showSplash = false
    }

    if (showSplash) {
        SplashScreenOverlay(onFinished = { showSplash = false })
        return
    }

    if (!hasCompletedOnboarding) {
        OnboardingScreen(
            allPacks = viewModel.allPacks,
            selectedLangCode = currentPack.languageCode,
            systemLang = systemLang,
            strings = strings,
            onSelectSystemLang = viewModel::setSystemLanguage,
            onSelectTargetLang = viewModel::selectLanguage,
            onCompleteOnboarding = { chosenCefr ->
                viewModel.selectCefr(chosenCefr)
                prefs.edit().putBoolean("onboarding_done", true).apply()
                hasCompletedOnboarding = true
            }
        )
        return
    }

    val currentUnit = activeGuidedUnit
    if (currentUnit != null) {
        GuidedLessonScreen(
            bundle = currentUnit,
            systemLang = systemLang,
            strings = strings,
            isRecording = isRecording,
            pronunciationResult = pronunciationResult,
            onSpeakText = { text, speed -> viewModel.speakSentence(text, speed) },
            onStartRecording = viewModel::startRecordingPronunciation,
            onStopAndEvaluate = { drill -> viewModel.stopAndEvaluatePronunciation(drill, null) },
            onCompleteUnit = { bundle, _ ->
                viewModel.recordSyntaxCompletion(bundle.grammarExercise, true)
            },
            onClose = { activeGuidedUnit = null }
        )
        return
    }

    Scaffold(
        containerColor = colors.background,
        bottomBar = {
            CleanBottomNavigationBar(
                activeTab = activeTab,
                systemLang = systemLang,
                onSelectTab = { activeTab = it }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            when (activeTab) {
                MainTab.TODAY -> HomeScreen(
                    allPacks = viewModel.allPacks,
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    systemLang = systemLang,
                    strings = strings,
                    progressList = progressList,
                    onSelectLanguage = viewModel::selectLanguage,
                    onSelectCefr = viewModel::selectCefr,
                    onStartGuidedUnit = { unit -> activeGuidedUnit = unit },
                    onOpenProfileSettings = { activeTab = MainTab.PROFILE }
                )

                MainTab.EXPLORE -> ExploreStudyHubScreen(
                    currentPack = currentPack,
                    systemLang = systemLang,
                    strings = strings,
                    onPlayAudio = { text, speed -> viewModel.speakSentence(text, speed) }
                )

                MainTab.LIVE_AI -> LiveConversationScreen(
                    currentPack = currentPack,
                    selectedCefr = selectedCefr,
                    systemLang = systemLang,
                    onSpeakText = { text, speed -> viewModel.speakSentence(text, speed) },
                    onOpenSettingsForApiKey = { activeTab = MainTab.PROFILE }
                )

                MainTab.PROFILE -> Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .statusBarsPadding()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = strings.profileSettingsTitle,
                            style = VocalFoxType.PageTitle,
                            color = colors.primaryText
                        )
                        Row(
                            modifier = Modifier
                                .clip(RoundedCornerShape(10.dp))
                                .background(colors.raised)
                                .clickable {
                                    prefs.edit().putBoolean("onboarding_done", false).apply()
                                    hasCompletedOnboarding = false
                                }
                                .padding(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Text(
                                text = strings.retakePlacementAction,
                                style = VocalFoxType.SecondaryCaption,
                                color = colors.accent
                            )
                        }
                    }
                    SettingsVoiceScreen(
                        allPacks = viewModel.allPacks,
                        voiceConfigs = voiceConfigs,
                        systemLang = systemLang,
                        isDarkMode = isDarkMode,
                        strings = strings,
                        onSelectSystemLang = viewModel::setSystemLanguage,
                        onToggleDarkMode = viewModel::toggleDarkMode,
                        onSelectVoicePreset = viewModel::selectVoicePreset,
                        onPreviewVoice = { langCode, preset ->
                            val sampleText = viewModel.allPacks[langCode]
                                ?.pronunciationDrills
                                ?.firstOrNull()
                                ?.targetSentence
                                .orEmpty()
                            viewModel.ttsManager.speak(sampleText, langCode, preset, 1.0f)
                        },
                        selectedTargetLangCode = currentPack.languageCode,
                        onSelectTargetLang = viewModel::selectLanguage
                    )
                }
            }
        }
    }
}

/**
 * Barra inferiore pulita, allineata e piatta (stile Duolingo + heydamir-unslop)
 * Integrata nello Scaffold così non copre MAI il testo delle card sottostanti.
 */
@Composable
private fun CleanBottomNavigationBar(
    activeTab: MainTab,
    systemLang: SystemLang,
    onSelectTab: (MainTab) -> Unit
) {
    val colors = VocalFoxTheme.colors
    val isIt = systemLang == SystemLang.IT

    val tabs = listOf(
        Triple(MainTab.TODAY, if (isIt) "Percorso" else "Path", Icons.Outlined.Home),
        Triple(MainTab.EXPLORE, if (isIt) "Accademia" else "Academy", Icons.Outlined.Explore),
        Triple(MainTab.LIVE_AI, "Live AI", Icons.Outlined.Forum),
        Triple(MainTab.PROFILE, if (isIt) "Profilo" else "Profile", Icons.Outlined.Person)
    )

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(colors.card)
            .border(1.dp, colors.hairline)
            .navigationBarsPadding()
            .padding(horizontal = 12.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically
    ) {
        tabs.forEach { (tab, label, icon) ->
            val selected = activeTab == tab
            Column(
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .background(if (selected) colors.accent.copy(alpha = 0.12f) else Color.Transparent)
                    .clickable { onSelectTab(tab) }
                    .padding(horizontal = 16.dp, vertical = 6.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = label,
                    tint = if (selected) colors.accent else colors.mutedText,
                    modifier = Modifier.size(22.dp)
                )
                Text(
                    text = label,
                    style = VocalFoxType.SecondaryCaption,
                    color = if (selected) colors.accent else colors.mutedText,
                    maxLines = 1
                )
            }
        }
    }
}
"""
}


def find_project_root() -> Path | None:
    candidates = [
        Path(__file__).resolve().parent,
        Path.cwd(),
    ]
    for base in list(candidates):
        if base.exists():
            for child in base.iterdir():
                if child.is_dir():
                    candidates.append(child)

    for folder in candidates:
        if (folder / "settings.gradle.kts").exists():
            return folder
    return None


def main() -> None:
    root = find_project_root()
    if root is None:
        print("[ERRORE] Non riesco a trovare settings.gradle.kts!")
        return

    print(f"[Vocalfox UI Polish] Aggiornamento in corso su:\n  {root}\n")

    for rel_path, content in FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  + Aggiornato: {rel_path}")

    drawable_dir = root / "app/src/main/res/drawable-nodpi"
    drawable_dir.mkdir(parents=True, exist_ok=True)

    for asset_name in [
        "vocalfox_text.png",
        "vocalfox.png",
        "splash_screen.webp",
        "logo.png",
        "mascot_idle.png",
        "mascot_celebrate.png",
        "mascot_thinking.png",
        "mascot_strict.png",
        "mascot_sad.png",
        "mascot_sleeping.png",
    ]:
        src_candidate = root / asset_name
        dst_candidate = drawable_dir / asset_name
        if src_candidate.exists() and src_candidate.resolve() != dst_candidate.resolve():
            shutil.copy2(src_candidate, dst_candidate)
            print(f"  + Copiato asset: {asset_name} -> app/src/main/res/drawable-nodpi/{asset_name}")

    print("\n========================================================")
    print("AGGIORNAMENTO UI VOCALFOX COMPLETATO!")
    print("Ora esegui:")
    print("========================================================\n")
    print(f'cd "{root}"')
    print("git add -A")
    print('git commit -m "Fix UI vertical text wrapping, clean bottom nav, WebP splash video & Vocalfox branding"')
    print("git push origin main")


if __name__ == "__main__":
    main()
