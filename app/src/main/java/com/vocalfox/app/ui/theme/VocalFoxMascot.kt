package com.vocalfox.app.ui.theme

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Pedagogical Mascot States mapped to individual drawable resources in `res/drawable-nodpi/`:
 * - `logo.png` (App icon & header emblem)
 * - `mascot_idle.png` (`MascotState.LOGO_IDLE` — friendly hands-on-hips smile)
 * - `mascot_celebrate.png` (`MascotState.CELEBRATE` — joyful raised arms with sparkles)
 * - `mascot_thinking.png` (`MascotState.THINKING` — hand on chin with question mark)
 * - `mascot_strict.png` (`MascotState.STRICT_COACH` — hands-on-hips frowning coach)
 * - `mascot_sad.png` (`MascotState.ENCOURAGE_SAD` — sitting puppy-eyes)
 * - `mascot_sleeping.png` (`MascotState.SLEEPING` — yawning with Zzz)
 */
enum class MascotState(val drawableName: String) {
    LOGO_IDLE("mascot_idle"),
    CELEBRATE("mascot_celebrate"),
    THINKING("mascot_thinking"),
    STRICT_COACH("mascot_strict"),
    ENCOURAGE_SAD("mascot_sad"),
    SLEEPING("mascot_sleeping")
}

@Composable
fun VocalFoxMascot(
    state: MascotState,
    modifier: Modifier = Modifier,
    size: Dp = 64.dp,
    useLogoEmblem: Boolean = false
) {
    val context = LocalContext.current
    val colors = VocalFoxTheme.colors

    val resId = remember(state, useLogoEmblem) {
        val resourceName = if (useLogoEmblem) "logo" else state.drawableName
        context.resources.getIdentifier(resourceName, "drawable", context.packageName)
    }

    val containerBg = if (useLogoEmblem) {
        VocalFoxPalette.FoxLogoBrownBackdrop
    } else if (colors.isDark) {
        VocalFoxPalette.FoxMuzzleCream
    } else {
        Color.White
    }

    Box(
        modifier = modifier
            .size(size)
            .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
            .background(containerBg)
            .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard)),
        contentAlignment = Alignment.Center
    ) {
        if (resId != 0) {
            Image(
                painter = painterResource(id = resId),
                contentDescription = state.name,
                contentScale = ContentScale.Fit,
                modifier = Modifier.size(size - 4.dp)
            )
        } else {
            VectorFoxFallback(state = state, size = size - 8.dp)
        }
    }
}

@Composable
private fun VectorFoxFallback(state: MascotState, size: Dp) {
    Canvas(modifier = Modifier.size(size)) {
        val w = this.size.width
        val h = this.size.height

        // Left & Right Ears
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

        // Dark Brown Ear Tips
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

        // Head Oval
        drawRoundRect(
            color = VocalFoxPalette.FoxFurOrange,
            topLeft = Offset(w * 0.15f, h * 0.25f),
            size = Size(w * 0.70f, h * 0.58f),
            cornerRadius = CornerRadius(w * 0.28f, w * 0.28f)
        )

        // Cream Muzzle
        drawRoundRect(
            color = VocalFoxPalette.FoxMuzzleTint,
            topLeft = Offset(w * 0.18f, h * 0.52f),
            size = Size(w * 0.64f, h * 0.30f),
            cornerRadius = CornerRadius(w * 0.22f, w * 0.22f)
        )

        // Eyes & Expression by MascotState
        val eyeY = h * 0.46f
        when (state) {
            MascotState.SLEEPING -> {
                drawLine(
                    color = VocalFoxPalette.FoxDeepInkBrown,
                    start = Offset(w * 0.28f, eyeY),
                    end = Offset(w * 0.42f, eyeY),
                    strokeWidth = 4f
                )
                drawLine(
                    color = VocalFoxPalette.FoxDeepInkBrown,
                    start = Offset(w * 0.58f, eyeY),
                    end = Offset(w * 0.72f, eyeY),
                    strokeWidth = 4f
                )
            }
            MascotState.CELEBRATE -> {
                drawArc(
                    color = VocalFoxPalette.FoxDeepInkBrown,
                    startAngle = 180f,
                    sweepAngle = 180f,
                    useCenter = false,
                    topLeft = Offset(w * 0.28f, eyeY - 8f),
                    size = Size(w * 0.14f, 16f),
                    style = Stroke(width = 4.5f)
                )
                drawArc(
                    color = VocalFoxPalette.FoxDeepInkBrown,
                    startAngle = 180f,
                    sweepAngle = 180f,
                    useCenter = false,
                    topLeft = Offset(w * 0.58f, eyeY - 8f),
                    size = Size(w * 0.14f, 16f),
                    style = Stroke(width = 4.5f)
                )
            }
            else -> {
                drawCircle(Color.White, radius = w * 0.09f, center = Offset(w * 0.35f, eyeY))
                drawCircle(Color.White, radius = w * 0.09f, center = Offset(w * 0.65f, eyeY))
                drawCircle(VocalFoxPalette.FoxDeepInkBrown, radius = w * 0.055f, center = Offset(w * 0.35f, eyeY))
                drawCircle(VocalFoxPalette.FoxDeepInkBrown, radius = w * 0.055f, center = Offset(w * 0.65f, eyeY))
                drawCircle(Color.White, radius = w * 0.02f, center = Offset(w * 0.33f, eyeY - 3f))
                drawCircle(Color.White, radius = w * 0.02f, center = Offset(w * 0.63f, eyeY - 3f))

                if (state == MascotState.STRICT_COACH) {
                    drawLine(
                        color = VocalFoxPalette.FoxDeepInkBrown,
                        start = Offset(w * 0.26f, eyeY - w * 0.11f),
                        end = Offset(w * 0.44f, eyeY - w * 0.06f),
                        strokeWidth = 4.5f
                    )
                    drawLine(
                        color = VocalFoxPalette.FoxDeepInkBrown,
                        start = Offset(w * 0.74f, eyeY - w * 0.11f),
                        end = Offset(w * 0.56f, eyeY - w * 0.06f),
                        strokeWidth = 4.5f
                    )
                }
            }
        }

        // Nose
        drawCircle(
            color = VocalFoxPalette.FoxDeepInkBrown,
            radius = w * 0.045f,
            center = Offset(w * 0.50f, h * 0.58f)
        )

        // Mouth
        val mouthStartAngle = if (state == MascotState.STRICT_COACH || state == MascotState.ENCOURAGE_SAD) 190f else 10f
        val mouthSweep = 160f
        drawArc(
            color = VocalFoxPalette.FoxDeepInkBrown,
            startAngle = mouthStartAngle,
            sweepAngle = mouthSweep,
            useCenter = false,
            topLeft = Offset(w * 0.42f, h * 0.63f),
            size = Size(w * 0.16f, h * 0.08f),
            style = Stroke(width = 4f)
        )
    }
}

/**
 * Quiet, structured pedagogical banner pairing `VocalFoxMascot` with a concise explanation.
 */
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
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        VocalFoxMascot(state = state, size = 60.dp)

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
