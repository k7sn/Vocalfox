package com.vocalfox.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * Unslop Typography Scale
 * - Weights restricted to 400 (Normal), 500 (Medium), and rare 600 (SemiBold).
 * - Never 700-900, never uppercase tracked labels, never negative letter-spacing on small text.
 * - Tabular figures (`tnum`) enabled on numeric & phonetic styles.
 */
object VocalFoxType {
    val Sans = FontFamily.SansSerif
    val Mono = FontFamily.Monospace

    val PageTitle = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 28.sp,
        lineHeight = 34.sp,
        letterSpacing = (-0.3).sp
    )

    val SectionTitle = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 20.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.sp
    )

    val CardFigure = TextStyle(
        fontFamily = Mono,
        fontWeight = FontWeight.Medium,
        fontSize = 28.sp,
        lineHeight = 32.sp,
        fontFeatureSettings = "tnum"
    )

    val SentenceDisplay = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 22.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.sp
    )

    val Body = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.sp
    )

    val BodyMedium = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 15.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.sp
    )

    val SecondaryCaption = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Normal,
        fontSize = 13.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.sp
    )

    val MetaMono = TextStyle(
        fontFamily = Mono,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.1.sp,
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
