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
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView

enum class MascotState(val drawableName: String) {
    LOGO_IDLE("mascot_idle"),
    CELEBRATE("mascot_celebrate"),
    THINKING("mascot_thinking"),
    STRICT_COACH("mascot_strict"),
    ENCOURAGE_SAD("mascot_sad"),
    SLEEPING("mascot_sleeping")
}

/**
 * Automatically trims excess white or transparent margins around mascot PNGs
 * so every pose is optically centered and fills its container generously.
 */
object MascotBitmapCache {
    private val cache = mutableMapOf<String, ImageBitmap>()

    fun getTrimmedBitmap(context: Context, resourceName: String, trimWhiteBg: Boolean): ImageBitmap? {
        val cacheKey = "${resourceName}_$trimWhiteBg"
        cache[cacheKey]?.let { return it }

        val resId = context.resources.getIdentifier(resourceName, "drawable", context.packageName)
        if (resId == 0) return null

        val raw = BitmapFactory.decodeResource(context.resources, resId) ?: return null
        if (!trimWhiteBg) {
            val img = raw.asImageBitmap()
            cache[cacheKey] = img
            return img
        }

        val trimmed = trimWhitespaceAndMakeTransparent(raw)
        val result = trimmed.asImageBitmap()
        cache[cacheKey] = result
        return result
    }

    private fun trimWhitespaceAndMakeTransparent(src: Bitmap): Bitmap {
        val w = src.width
        val h = src.height
        if (w <= 4 || h <= 4) return src

        val pixels = IntArray(w * h)
        src.getPixels(pixels, 0, w, 0, 0, w, h)

        var minX = w
        var minY = h
        var maxX = 0
        var maxY = 0

        for (y in 0 until h) {
            val rowOffset = y * w
            for (x in 0 until w) {
                val c = pixels[rowOffset + x]
                val a = (c ushr 24) and 0xFF
                val r = (c ushr 16) and 0xFF
                val g = (c ushr 8) and 0xFF
                val b = c and 0xFF

                // Treat near-white background pixels or transparent pixels as empty margin
                val isNearWhiteOrGreyShadow = (r > 236 && g > 236 && b > 236)
                val isEmpty = (a < 25) || isNearWhiteOrGreyShadow

                if (isNearWhiteOrGreyShadow) {
                    // Make outer white background transparent so the fox blends on tinted cards
                    pixels[rowOffset + x] = 0x00000000
                }

                if (!isEmpty) {
                    if (x < minX) minX = x
                    if (x > maxX) maxX = x
                    if (y < minY) minY = y
                    if (y > maxY) maxY = y
                }
            }
        }

        val cleaned = Bitmap.createBitmap(pixels, w, h, Bitmap.Config.ARGB_8888)
        if (maxX <= minX || maxY <= minY) return cleaned

        val padX = ((maxX - minX) * 0.04f).toInt().coerceAtLeast(2)
        val padY = ((maxY - minY) * 0.04f).toInt().coerceAtLeast(2)
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
            trimWhiteBg = !useLogoEmblem
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
                modifier = Modifier.fillMaxSize(if (useLogoEmblem) 1f else 0.92f)
            )
        } else {
            VectorFoxFallback(state = state, size = size * 0.88f)
        }
    }
}

/**
 * Renders `splash_screen.webp` (animated WebP with alpha transparency) natively via Android ImageDecoder.
 * Falls back to the trimmed mascot if `splash_screen.webp` is not yet in `res/drawable-nodpi/`.
 */
@Composable
fun AnimatedWebpSplashPlayer(
    modifier: Modifier = Modifier,
    size: Dp = 220.dp
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
            }
        )
    } else {
        VocalFoxMascot(
            state = MascotState.CELEBRATE,
            size = size
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
            size = 64.dp,
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
