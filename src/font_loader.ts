/**
 * Font Loader
 * Loads the Pokemon Pixel Font before the game starts
 */

import { Config } from './config';

let fontLoaded = false;
let fontLoading = false;

export async function loadPokemonFont(): Promise<boolean> {
  if (fontLoaded) return true;
  if (fontLoading) {
    // Wait for existing load to complete
    while (fontLoading) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    return fontLoaded;
  }

  fontLoading = true;

  try {
    const fontFace = new FontFace(
      'Pokemon Pixel Font',
      `url(${Config.FONTS_PATH}/pokemon_pixel_font.ttf)`
    );

    await fontFace.load();
    document.fonts.add(fontFace);

    // Wait for font to be ready
    await document.fonts.ready;

    fontLoaded = true;
    fontLoading = false;
    console.log('Pokemon Pixel Font loaded successfully');
    return true;
  } catch (error) {
    console.error('Failed to load Pokemon Pixel Font:', error);
    console.error('Font path attempted:', `${Config.FONTS_PATH}/pokemon_pixel_font.ttf`);
    fontLoading = false;
    return false;
  }
}

export function isFontLoaded(): boolean {
  return fontLoaded;
}

