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
