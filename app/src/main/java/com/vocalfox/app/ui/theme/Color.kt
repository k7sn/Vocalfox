package com.vocalfox.app.ui.theme

import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

object VocalFoxPalette {
    val FoxFurOrange = Color(0xFFF26419)
    val FoxFurOrangeDark = Color(0xFFE0530C)
    val FoxLogoBrownBackdrop = Color(0xFF6E351A)
    val FoxDeepInkBrown = Color(0xFF231610)
    val FoxMuzzleCream = Color(0xFFFAF6F0)
    val FoxMuzzleTint = Color(0xFFF3ECE2)

    // Warm Card Illustration Tints (Inspired by Design Example.pdf Page 1 & 2)
    val TintWarmAmber = Color(0xFFFFE8D1)
    val TintSoftGold = Color(0xFFFFF2C6)
    val TintMintSage = Color(0xFFDDF3E8)
    val TintCalmSky = Color(0xFFE3EFFD)

    val LightBackground = Color(0xFFFAF6F0)
    val LightCard = Color(0xFFFFFFFF)
    val LightRaised = Color(0xFFF3ECE2)
    val LightPrimaryText = Color(0xFF231610)
    val LightSecondaryText = Color(0xFF5E5349)
    val LightMutedText = Color(0xFF85796D)
    val LightHairline = Color(0x14231610)

    val DarkBackground = Color(0xFF16120F)
    val DarkCard = Color(0xFF211B16)
    val DarkRaised = Color(0xFF2C241E)
    val DarkPrimaryText = Color(0xFFF5EFE6)
    val DarkSecondaryText = Color(0xFFB5ABA0)
    val DarkMutedText = Color(0xFF8A8077)
    val DarkHairline = Color(0x18F5EFE6)

    val PositiveLight = Color(0xFF15803D)
    val PositiveDark = Color(0xFF4ADE80)
    val WarningLight = Color(0xFFD97706)
    val WarningDark = Color(0xFFFBBF24)
    val NegativeLight = Color(0xFFDC2626)
    val NegativeDark = Color(0xFFF87171)

    val SyntaxSubject = Color(0xFF2563EB)
    val SyntaxVerbV2 = Color(0xFFE0530C)
    val SyntaxSubordinateVerb = Color(0xFF7C3AED)
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
    onAccent = Color.White,
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
    onAccent = Color(0xFF16120F),
    logoBackdrop = VocalFoxPalette.FoxLogoBrownBackdrop,
    positive = VocalFoxPalette.PositiveDark,
    warning = VocalFoxPalette.WarningDark,
    negative = VocalFoxPalette.NegativeDark
)

val LocalVocalFoxColors = staticCompositionLocalOf { LightVocalFoxColors }
