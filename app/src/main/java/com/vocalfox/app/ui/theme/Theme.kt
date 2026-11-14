package com.vocalfox.app.ui.theme

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.unit.dp

/**
 * Unslop Motion & Nested Radius Tokens
 * - Single easing curve: cubic-bezier(0.22, 1, 0.36, 1)
 * - Nested radius math: Card = 16dp, Inner Control/Row = 8dp (16 - 8 padding), Tag/Keycap = 6dp.
 */
object VocalFoxTokens {
    val Easing = CubicBezierEasing(0.22f, 1.0f, 0.36f, 1.0f)
    const val DurationFast = 150
    const val DurationMedium = 220

    val RadiusKeycap = 6.dp
    val RadiusControl = 8.dp
    val RadiusCard = 16.dp
    val RadiusPanel = 20.dp
}

private val VocalFoxShapes = Shapes(
    extraSmall = RoundedCornerShape(VocalFoxTokens.RadiusKeycap),
    small = RoundedCornerShape(VocalFoxTokens.RadiusControl),
    medium = RoundedCornerShape(VocalFoxTokens.RadiusCard),
    large = RoundedCornerShape(VocalFoxTokens.RadiusPanel)
)

@Composable
fun VocalFoxTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) DarkVocalFoxColors else LightVocalFoxColors

    val materialScheme = if (darkTheme) {
        darkColorScheme(
            primary = colors.accent,
            onPrimary = colors.onAccent,
            background = colors.background,
            onBackground = colors.primaryText,
            surface = colors.card,
            onSurface = colors.primaryText,
            surfaceVariant = colors.raised,
            onSurfaceVariant = colors.secondaryText,
            outline = colors.hairline
        )
    } else {
        lightColorScheme(
            primary = colors.accent,
            onPrimary = colors.onAccent,
            background = colors.background,
            onBackground = colors.primaryText,
            surface = colors.card,
            onSurface = colors.primaryText,
            surfaceVariant = colors.raised,
            onSurfaceVariant = colors.secondaryText,
            outline = colors.hairline
        )
    }

    CompositionLocalProvider(LocalVocalFoxColors provides colors) {
        MaterialTheme(
            colorScheme = materialScheme,
            typography = VocalFoxMaterialTypography,
            shapes = VocalFoxShapes,
            content = content
        )
    }
}

object VocalFoxTheme {
    val colors: VocalFoxColors
        @Composable
        get() = LocalVocalFoxColors.current
}
