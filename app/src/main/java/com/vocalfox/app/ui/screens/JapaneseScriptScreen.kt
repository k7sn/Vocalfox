package com.vocalfox.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
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
import androidx.compose.ui.unit.sp
import com.vocalfox.app.domain.model.LanguagePack
import com.vocalfox.app.domain.model.ScriptCardItem
import com.vocalfox.app.ui.i18n.SystemLang
import com.vocalfox.app.ui.i18n.UiStrings
import com.vocalfox.app.ui.theme.VocalFoxTheme
import com.vocalfox.app.ui.theme.VocalFoxTokens
import com.vocalfox.app.ui.theme.VocalFoxType

@Composable
fun JapaneseScriptScreen(
    currentPack: LanguagePack,
    systemLang: SystemLang,
    strings: UiStrings,
    showFurigana: Boolean,
    showRomaji: Boolean,
    onToggleFurigana: (Boolean) -> Unit,
    onToggleRomaji: (Boolean) -> Unit,
    onPlayAudio: (String) -> Unit
) {
    val colors = VocalFoxTheme.colors
    val categories = remember(currentPack.languageCode) {
        currentPack.scriptCards.map { it.scriptCategory }.distinct()
    }
    var selectedCategory by remember(currentPack.languageCode) {
        mutableStateOf(categories.firstOrNull().orEmpty())
    }
    var inspectedCard by remember(currentPack.languageCode, selectedCategory) {
        mutableStateOf(currentPack.scriptCards.firstOrNull { it.scriptCategory == selectedCategory })
    }

    val filteredCards = currentPack.scriptCards.filter { it.scriptCategory == selectedCategory }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.background)
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = strings.scriptHeader,
                style = VocalFoxType.PageTitle,
                color = colors.primaryText
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                        .background(if (showFurigana) colors.accent else colors.raised)
                        .clickable { onToggleFurigana(!showFurigana) }
                        .padding(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = strings.showFuriganaLabel,
                        style = VocalFoxType.MetaMono,
                        color = if (showFurigana) colors.onAccent else colors.secondaryText
                    )
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                        .background(if (showRomaji) colors.accent else colors.raised)
                        .clickable { onToggleRomaji(!showRomaji) }
                        .padding(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = strings.showRomajiLabel,
                        style = VocalFoxType.MetaMono,
                        color = if (showRomaji) colors.onAccent else colors.secondaryText
                    )
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            categories.forEach { category ->
                val isSelected = category == selectedCategory
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(VocalFoxTokens.RadiusControl))
                        .background(if (isSelected) colors.card else colors.raised)
                        .border(
                            width = 1.dp,
                            color = if (isSelected) colors.accent else colors.hairline,
                            shape = RoundedCornerShape(VocalFoxTokens.RadiusControl)
                        )
                        .clickable {
                            selectedCategory = category
                            inspectedCard = currentPack.scriptCards.firstOrNull { it.scriptCategory == category }
                        }
                        .padding(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = category,
                        style = VocalFoxType.BodyMedium,
                        color = if (isSelected) colors.accent else colors.secondaryText
                    )
                }
            }
        }

        val currentCard: ScriptCardItem? = inspectedCard
        if (currentCard != null) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(VocalFoxTokens.RadiusCard))
                    .background(colors.card)
                    .border(1.dp, colors.hairline, RoundedCornerShape(VocalFoxTokens.RadiusCard))
                    .padding(20.dp),
                horizontalArrangement = Arrangement.spacedBy(20.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(84.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(colors.raised)
                        .clickable { onPlayAudio(currentCard.exampleWord) },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = currentCard.symbol,
                        style = VocalFoxType.PageTitle.copy(fontSize = 36.sp),
                        color = colors.primaryText
                    )
                }

                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        if (showFurigana) {
                            Text(
                                text = currentCard.readingOrFurigana,
                                style = VocalFoxType.BodyMedium,
                                color = colors.accent
                            )
                        }
                        if (showRomaji) {
                            Text(
                                text = "[${currentCard.romajiOrIpa}]",
                                style = VocalFoxType.MetaMono,
                                color = colors.mutedText
                            )
                        }
                        Text(
                            text = "${currentCard.strokeCount} strokes",
                            style = VocalFoxType.MetaMono,
                            color = colors.mutedText
                        )
                    }

                    Text(
                        text = currentCard.meaning.get(systemLang),
                        style = VocalFoxType.BodyMedium,
                        color = colors.primaryText
                    )

                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(VocalFoxTokens.RadiusKeycap))
                            .background(colors.raised)
                            .clickable { onPlayAudio(currentCard.exampleWord) }
                            .padding(horizontal = 10.dp, vertical = 6.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.VolumeUp,
                            contentDescription = null,
                            tint = colors.secondaryText,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = "${currentCard.exampleWord} (${currentCard.exampleReading})",
                            style = VocalFoxType.SecondaryCaption,
                            color = colors.secondaryText
                        )
                    }
                }
            }
        }

        LazyVerticalGrid(
            columns = GridCells.Adaptive(minSize = 96.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            modifier = Modifier.weight(1f)
        ) {
            items(filteredCards) { item ->
                val isSelected = item == inspectedCard
                Column(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(colors.card)
                        .border(
                            width = 1.dp,
                            color = if (isSelected) colors.accent else colors.hairline,
                            shape = RoundedCornerShape(12.dp)
                        )
                        .clickable {
                            inspectedCard = item
                            onPlayAudio(item.symbol)
                        }
                        .padding(12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    if (showFurigana) {
                        Text(
                            text = item.readingOrFurigana,
                            style = VocalFoxType.MetaMono,
                            color = colors.accent,
                            maxLines = 1
                        )
                    }
                    Text(
                        text = item.symbol,
                        style = VocalFoxType.SectionTitle,
                        color = colors.primaryText
                    )
                    if (showRomaji) {
                        Text(
                            text = item.romajiOrIpa,
                            style = VocalFoxType.MetaMono,
                            color = colors.mutedText,
                            maxLines = 1
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))
    }
}
