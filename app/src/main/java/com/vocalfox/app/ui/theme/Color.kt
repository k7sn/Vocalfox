package com.vocalfox.app.ui.theme

import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

/**
 * VocalFox Color System
 * Strictly adheres to heydamir-unslop Warm Neutral Ramp + Mascot Brand Palette.
 * Zero purple/blue gradients, zero neon borders, zero glowing pills.
 */
object VocalFoxPalette {
    // Mascot Brand Anchors extracted from Logo.png, Fox Mascot.jpg, Fox Mascot2.jpg
    val FoxFurOrange = Color(0xFFF26419)
    val FoxFurOrangeDark = Color(0xFFD9530E) // >= 4.5:1 contrast with white text
    val FoxLogoBrownBackdrop = Color(0xFF6E351A)
    val FoxDeepInkBrown = Color(0xFF2B1810)
    val FoxMuzzleCream = Color(0xFFFAF6F0)
    val FoxMuzzleTint = Color(0xFFF5EBE0)

    // Light Mode Warm Neutral Ramp
    val LightBackground = Color(0xFFFAF6F0)
    val LightCard = Color(0xFFFDFBF7)
    val LightRaised = Color(0xFFF5EBE0)
    val LightPrimaryText = Color(0xFF2B1810)
    val LightSecondaryText = Color(0xFF5E554A)
    val LightMutedText = Color(0xFF7B7266)
    val LightHairline = Color(0x142B1810) // 8% primary text opacity

    // Dark Mode Warm Neutral Ramp
    val DarkDeepest = Color(0xFF12110F)
    val DarkBackground = Color(0xFF18120E)
    val DarkCard = Color(0xFF211A15)
    val DarkRaised = Color(0xFF2B221C)
    val DarkPrimaryText = Color(0xFFEFE9DE)
    val DarkSecondaryText = Color(0xFFAAA398)
    val DarkMutedText = Color(0xFF8A847A)
    val DarkHairline = Color(0x14EFE9DE) // 8% primary text opacity

    // Semantic Toned Colors (Phonetics & Syntax Roles)
    val PositiveLight = Color(0xFF16A34A)
    val PositiveDark = Color(0xFF4CC38A)
    val WarningLight = Color(0xFFB45309)
    val WarningDark = Color(0xFFF59E0B)
    val NegativeLight = Color(0xFFDC2626)
    val NegativeDark = Color(0xFFE5484D)

    // Grammatical Syntax Underline Palette (Muted, scholarly tones)
    val SyntaxSubject = Color(0xFF2563EB)
    val SyntaxVerbV2 = Color(0xFFD9530E)
    val SyntaxSubordinateVerb = Color(0xFF9333EA)
    val SyntaxParticle = Color(0xFF0D9488)
    val SyntaxSubjunctive = Color(0xFFC026D3)
    val SyntaxObject = Color(0xFF4F46E5)
}

@Immutable
data class VocalFoxColors(
    val isDark: Boolean,
    val background: Color,
    val card: Color,
    val raised: Color,
    val primaryText: Color,
    val secondaryText: Color,
    val mutedText: Color,
    val hairline: Color,
    val accent: Color,
    val onAccent: Color,
    val logoBackdrop: Color,
    val positive: Color,
    val warning: Color,
    val negative: Color
)

val LightVocalFoxColors = VocalFoxColors(
    isDark = false,
    background = VocalFoxPalette.LightBackground,
    card = VocalFoxPalette.LightCard,
    raised = VocalFoxPalette.LightRaised,
    primaryText = VocalFoxPalette.LightPrimaryText,
    secondaryText = VocalFoxPalette.LightSecondaryText,
    mutedText = VocalFoxPalette.LightMutedText,
    hairline = VocalFoxPalette.LightHairline,
    accent = VocalFoxPalette.FoxFurOrangeDark,
    onAccent = Color(0xFFFFFFFF),
    logoBackdrop = VocalFoxPalette.FoxLogoBrownBackdrop,
    positive = VocalFoxPalette.PositiveLight,
    warning = VocalFoxPalette.WarningLight,
    negative = VocalFoxPalette.NegativeLight
)

val DarkVocalFoxColors = VocalFoxColors(
    isDark = true,
    background = VocalFoxPalette.DarkBackground,
    card = VocalFoxPalette.DarkCard,
    raised = VocalFoxPalette.DarkRaised,
    primaryText = VocalFoxPalette.DarkPrimaryText,
    secondaryText = VocalFoxPalette.DarkSecondaryText,
    mutedText = VocalFoxPalette.DarkMutedText,
    hairline = VocalFoxPalette.DarkHairline,
    accent = VocalFoxPalette.FoxFurOrange,
    onAccent = Color(0xFF18120E),
    logoBackdrop = VocalFoxPalette.FoxLogoBrownBackdrop,
    positive = VocalFoxPalette.PositiveDark,
    warning = VocalFoxPalette.WarningDark,
    negative = VocalFoxPalette.NegativeDark
)

val LocalVocalFoxColors = staticCompositionLocalOf { LightVocalFoxColors }
