/**
 * Pokemon Selection Scene
 * Recreates the Pokemon selection screen
 */

import { Config } from '../config';

export class PokemonSelectionScene {
  private selectedPokemon: { name: string; type: string; color: string; x: number; y: number } | null = null;
  private pokemonOptions = [
    { name: 'Bulbasaur', type: 'Grass', color: 'rgb(100, 255, 100)', x: 200, y: 300 },
    { name: 'Charmander', type: 'Fire', color: 'rgb(255, 100, 100)', x: 400, y: 300 },
    { name: 'Squirtle', type: 'Water', color: 'rgb(100, 100, 255)', x: 600, y: 300 },
  ];
  private cursorPos: number = 0;
  private confirmed: boolean = false;
  private fontLarge: string = '48px "Pokemon Pixel Font", Arial, sans-serif';
  private fontMedium: string = '32px "Pokemon Pixel Font", Arial, sans-serif';
  private fontSmall: string = '24px "Pokemon Pixel Font", Arial, sans-serif';
  private fontLoaded = false;

  constructor() {
    this.loadFont();
  }

  private async loadFont(): Promise<void> {
    try {
      const fontFace = new FontFace(
        'Pokemon Pixel Font',
        `url(${Config.FONTS_PATH}/pokemon_pixel_font.ttf)`
      );
      await fontFace.load();
      document.fonts.add(fontFace);
      this.fontLoaded = true;
    } catch (error) {
      console.warn('Unable to load Pokemon pixel font, using fallback:', error);
      this.fontLarge = '48px Arial, sans-serif';
      this.fontMedium = '32px Arial, sans-serif';
      this.fontSmall = '24px Arial, sans-serif';
    }
  }

  onEnter(): void {
    this.selectedPokemon = null;
    this.cursorPos = 0;
    this.confirmed = false;
  }

  handleEvent(event: KeyboardEvent | MouseEvent): void {
    if (event instanceof KeyboardEvent && event.type === 'keydown' && !this.confirmed) {
      if (event.key === 'ArrowLeft' && this.cursorPos > 0) {
        this.cursorPos -= 1;
      } else if (event.key === 'ArrowRight' && this.cursorPos < this.pokemonOptions.length - 1) {
        this.cursorPos += 1;
      } else if (event.key === 'Enter' || event.key === ' ') {
        // Select Pokemon
        this.selectedPokemon = this.pokemonOptions[this.cursorPos];
        this.confirmed = true;
      }
    }
  }

  update(_deltaTime: number): void {
    // No update logic needed
  }

  render(ctx: CanvasRenderingContext2D): void {
    // Clear with background color
    ctx.fillStyle = `rgb(${Config.BG_COLOR.join(',')})`;
    ctx.fillRect(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT);

    // Title
    ctx.fillStyle = `rgb(${Config.BLACK.join(',')})`;
    ctx.font = this.fontLarge;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText('Choose Your Pokemon', Config.SCREEN_WIDTH / 2, 80);

    // Draw Pokemon options
    for (let i = 0; i < this.pokemonOptions.length; i++) {
      const pokemon = this.pokemonOptions[i];
      const boxX = pokemon.x - 60;
      const boxY = pokemon.y - 80;
      const boxWidth = 120;
      const boxHeight = 120;

      // Highlight selected
      if (i === this.cursorPos) {
        ctx.strokeStyle = this.confirmed
          ? `rgb(${Config.GREEN.join(',')})`
          : `rgb(${Config.WHITE.join(',')})`;
        ctx.lineWidth = 4;
        ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);
      }

      // Pokemon placeholder (colored circle)
      ctx.fillStyle = pokemon.color;
      ctx.beginPath();
      ctx.ellipse(pokemon.x, pokemon.y, 40, 40, 0, 0, 2 * Math.PI);
      ctx.fill();

      // Pokemon name
      ctx.fillStyle = `rgb(${Config.BLACK.join(',')})`;
      ctx.font = this.fontMedium;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(pokemon.name, pokemon.x, pokemon.y + 60);

      // Pokemon type
      ctx.fillStyle = `rgb(${Config.DARK_GRAY.join(',')})`;
      ctx.font = this.fontSmall;
      ctx.fillText(pokemon.type, pokemon.x, pokemon.y + 85);
    }

    // Instructions or confirmation message
    ctx.font = this.fontMedium;
    ctx.textBaseline = 'top';
    if (this.confirmed) {
      ctx.fillStyle = `rgb(${Config.GREEN.join(',')})`;
      ctx.fillText(
        `You chose ${this.selectedPokemon!.name}!`,
        Config.SCREEN_WIDTH / 2,
        Config.SCREEN_HEIGHT - 40
      );
    } else {
      ctx.fillStyle = `rgb(${Config.DARK_GRAY.join(',')})`;
      ctx.fillText(
        'Use Arrow Keys to select, Enter to confirm',
        Config.SCREEN_WIDTH / 2,
        Config.SCREEN_HEIGHT - 40
      );
    }
  }
}

