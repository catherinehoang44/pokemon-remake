/**
 * Character Selection Scene
 * Recreates the character selection screen
 */

import { Config } from '../config';

export class CharacterSelectionScene {
  private selectedCharacter: { name: string; color: string; x: number; y: number } | null = null;
  private characterOptions = [
    { name: 'Red', color: 'rgb(255, 0, 0)', x: 200, y: 200 },
    { name: 'Blue', color: 'rgb(0, 0, 255)', x: 400, y: 200 },
  ];
  private cursorPos: number = 0;
  private confirmed: boolean = false;
  private onChangeScene?: (sceneName: string) => void;
  private fontLarge: string = '48px "Pokemon Pixel Font", Arial, sans-serif';
  private fontMedium: string = '32px "Pokemon Pixel Font", Arial, sans-serif';
  private fontLoaded = false;

  constructor(onChangeScene?: (sceneName: string) => void) {
    this.onChangeScene = onChangeScene;
    this.loadFont();
  }

  private async loadFont(): Promise<void> {
    // Font should already be loaded by font_loader, but check anyway
    if (document.fonts.check('32px "Pokemon Pixel Font"')) {
      this.fontLoaded = true;
    } else {
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
      }
    }
  }

  onEnter(): void {
    this.selectedCharacter = null;
    this.cursorPos = 0;
    this.confirmed = false;
  }

  handleEvent(event: KeyboardEvent | MouseEvent): void {
    if (event instanceof KeyboardEvent && event.type === 'keydown' && !this.confirmed) {
      if (event.key === 'ArrowLeft' && this.cursorPos > 0) {
        this.cursorPos -= 1;
      } else if (event.key === 'ArrowRight' && this.cursorPos < this.characterOptions.length - 1) {
        this.cursorPos += 1;
      } else if (event.key === 'Enter' || event.key === ' ') {
        // Select character
        this.selectedCharacter = this.characterOptions[this.cursorPos];
        this.confirmed = true;
        // Transition to house/village scene
        if (this.onChangeScene) {
          this.onChangeScene('house_village');
        }
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
    ctx.fillText('Choose Your Character', Config.SCREEN_WIDTH / 2, 80);

    // Draw character options
    for (let i = 0; i < this.characterOptions.length; i++) {
      const character = this.characterOptions[i];
      const boxX = character.x - 60;
      const boxY = character.y - 80;
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

      // Character placeholder (colored circle)
      ctx.fillStyle = character.color;
      ctx.beginPath();
      ctx.ellipse(character.x, character.y, 40, 40, 0, 0, 2 * Math.PI);
      ctx.fill();

      // Character name
      ctx.fillStyle = `rgb(${Config.BLACK.join(',')})`;
      ctx.font = this.fontMedium;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(character.name, character.x, character.y + 60);
    }

    // Instructions or confirmation message
    ctx.font = this.fontMedium;
    ctx.textBaseline = 'top';
    if (this.confirmed) {
      ctx.fillStyle = `rgb(${Config.GREEN.join(',')})`;
      ctx.fillText(
        `You chose ${this.selectedCharacter!.name}!`,
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

