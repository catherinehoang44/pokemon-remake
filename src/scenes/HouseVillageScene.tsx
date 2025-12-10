/**
 * House/Village Scene
 * Map exploration with scrolling camera, character movement, Lugia sequence, and dialog
 */

import { Config } from '../config';
import { SpriteSheet, AnimatedSprite, loadImage } from '../utils';
import { audioManager } from '../audio_manager';

type LugiaState = 'hidden' | 'flying_in' | 'animating' | 'stopped';
type FadeState = 'none' | 'fading' | 'faded';

export class HouseVillageScene {
  // Walkable areas configuration
  private walkableRectangles: Array<[number, number, number, number]> = [
    [15, 4, 16, 7],   // Rectangle from 15,4 to 16,7
    [14, 8, 16, 12],  // Rectangle from 14,8 to 16,12
  ];
  private walkableCells: Array<[number, number]> = [
    [17, 8],
    [17, 9],
    [18, 9],
  ];

  // Speed adjustments
  private lugiaAnimationSpeed = 0.1;
  private lugiaFlySpeed = 2;
  private dialogSlideSpeed = 8;
  private fadeSpeed = 20;
  private battleTextFadeSpeed = 5;
  private battleSlideSpeedBase = 5;
  private battleTrainerAnimationSpeed = 0.2;
  private battleLugiaAnimationSpeed = 0.1;
  private battleVenuAnimationSpeed = 0.1;

  // Map and player
  private mapImage: HTMLImageElement | null = null;
  private mapWidth = 768;
  private mapHeight = 512;
  private playerWorldX = 0;
  private playerWorldY = 0;
  private cameraX = 0;
  private cameraY = 0;
  private playerWidth = 32;
  private playerHeight = 42;
  private characterSprite: AnimatedSprite | null = null;

  // Movement state
  private movingUp = false;
  private movingDown = false;
  private movingLeft = false;
  private movingRight = false;
  private currentDirection = 0; // 0=down, 1=up, 2=right, 3=left
  
  // Exclamation mark popup
  private exclamationImage: HTMLImageElement | null = null;
  private exclamationVisible = false;
  private exclamationTimer = 0;
  private exclamationDuration = 500; // milliseconds
  private exclamationY = 0; // Y offset for animation

  // Lugia
  private lugiaSprites: HTMLImageElement[] = [];
  private lugiaCurrentFrame = 0;
  private lugiaAnimationTime = 0;
  private lugiaState: LugiaState = 'hidden';
  private lugiaTargetX = 0;
  private lugiaTargetY = 0;
  private lugiaX = 0;
  private lugiaY = -200;
  private lugiaAnimationComplete = false;
  private lugiaCryFinished = false;

  // Dialog
  private dialogImage: HTMLImageElement | null = null;
  private dialogVisible = false;
  private dialogSlideY = Config.SCREEN_HEIGHT;
  private dialogFullyVisible = false;
  private dialogText = '';
  private dialogFont: string = '32px "Pokemon Pixel Font", Arial, sans-serif';
  private fontLoaded = false;

  // Battle
  private fightingBackground: HTMLImageElement | null = null;
  private fadeState: FadeState = 'none';
  private fadeAlpha = 0;
  private fadeComplete = false;
  private dialogPauseTimer = 0;
  private dialogPauseDuration = 2000;
  private battleAnimationsStarted = false;

  // Battle UI elements
  private battleDialog: HTMLImageElement | null = null;
  private battleDialogX = 0;
  private battleDialogY = 0;
  private battleDialogAlpha = 0;
  private battleDialogVisible = false;
  private battleGrass: HTMLImageElement | null = null;
  private battleGrassLeftX = 0;
  private battleGrassY = 0;
  private battleGrassLeftTargetX = 0;
  private battleGrassVisible = false;
  private battleGrassSpeed = 5;
  private battlePokemonstat: HTMLImageElement | null = null;
  private battlePokemonstatX = 0;
  private battlePokemonstatY = 0;
  private battlePokemonstatTargetX = 0;
  private battlePokemonstatVisible = false;
  private battlePokemonstatSpeed = 5;
  private battleWater: HTMLImageElement | null = null;
  private battleWaterX = 0;
  private battleWaterY = 0;
  private battleWaterTargetX = 0;
  private battleWaterVisible = false;
  private battleWaterSpeed = 5;
  private battleTrainerSprites: HTMLImageElement[] = [];
  private battleTrainerX = 0;
  private battleTrainerY = 0;
  private battleTrainerTargetX = 0;
  private battleTrainerCurrentFrame = 0;
  private battleTrainerAnimationTime = 0;
  private battleTrainerVisible = false;
  private battleTrainerCanAnimate = false;
  private battleTrainerSlideOut = false;
  private battleTrainerAlpha = 255;
  private battleTrainerSpeed = 5;
  private allBattleElementsSlidIn = false;
  private battleLugiaGif: HTMLImageElement | null = null;
  private battleLugiaX = 0;
  private battleLugiaY = 0;
  private battleLugiaTargetX = 0;
  private battleLugiaVisible = false;
  private battleVenuGif: HTMLImageElement | null = null;
  private battleVenuX = 0;
  private battleVenuY = 0;
  private battleVenuTargetY = 0;
  private battleVenuVisible = false;
  private ballPoofPlayed = false;
  private battleVenuStat: HTMLImageElement | null = null;
  private battleVenuStatX = 0;
  private battleVenuStatY = 0;
  private battleVenuStatVisible = true;

  // Battle text
  private battleTextState: 'lugia' | 'venusaur' | 'transitioning' = 'lugia';
  private battleTextLugiaAlpha = 255;
  private battleTextVenusaurAlpha = 0;
  private battleTextFading = false;

  // Health bars
  private lugiaMaxHP = 100;
  private lugiaCurrentHP = 100;
  private venusaurMaxHP = 100;
  private venusaurCurrentHP = 100;
  private healthBarVisible = false;

  // Battle menu UI
  private battleMenuUI: HTMLImageElement | null = null;
  private battleMenuVisible = false;
  private battleMenuCursorPos = 0; // 0=Fight, 1=Bag, 2=Pokemon, 3=Run
  private battleMenuOptions = ['FIGHT', 'BAG', 'POKEMON', 'RUN']; // All caps like Python version
  private battleMenuHoveredOption: number | null = null;
  private battleMenuX = 0;
  private battleMenuY = 0;
  private battleMenuOptionWidth = 0;
  private battleMenuOptionHeight = 0;
  private battleMenuPadding = 12; // Padding like Python version
  
  // Menu screens
  private bagScreenImage: HTMLImageElement | null = null;
  private pokemonScreenImage: HTMLImageElement | null = null;
  private bagScreenVisible = false;
  private pokemonScreenVisible = false;
  
  // Text messages
  private runTextVisible = false;
  private runTextAlpha = 255;
  private fullHPTextVisible = false;
  private fullHPTextAlpha = 255;
  private battleMenuSelectedCell: number | null = null; // Keep selected cell highlighted (for Run and Bag)

  // Combat UI (shown when Fight is clicked)
  private combatUI: HTMLImageElement | null = null;
  private combatUIVisible = false;
  private combatUIPadding = 12;
  private combatUILeftGridCols = 2;
  private combatUILeftGridRows = 2;
  private combatUIRightGridCols = 2;
  private combatUIRightGridRows = 2;
  private combatUILeftCellWidth = 0;
  private combatUILeftCellHeight = 0;
  private combatUIRightCellWidth = 0;
  private combatUIRightCellHeight = 0;
  private combatUILeftGridContentWidth = 0;
  private combatUIRightGridContentWidth = 0;
  private combatUIHoveredCell: { gridSide: 'left' | 'right'; row: number; col: number } | null = null;
  private combatUIMoveLabels = ['Context Recall', 'Syntax Slash', 'Debug Dash', 'Prompt Pulse'];
  private combatUIMoveDetails: { [key: string]: { pp: number; pp_max: number; type: string } } = {
    'Context Recall': { pp: 0, pp_max: 20, type: 'Psychic' },
    'Syntax Slash': { pp: 0, pp_max: 10, type: 'Steel' },
    'Debug Dash': { pp: 0, pp_max: 15, type: 'Steel' },
    'Prompt Pulse': { pp: 1, pp_max: 5, type: 'Psychic' }
  };
  
  // Attack sequence
  private attackPulseImage: HTMLImageElement | null = null;
  private attackPulseEndImage: HTMLImageElement | null = null;
  private attackSequenceActive = false;
  private attackPulseVisible = false;
  private attackPulseAlpha = 0;
  private attackPulseScale = 0.5;
  private attackPulseTimer = 0;
  private attackPulseDuration = 1000; // milliseconds
  private attackPulseEndVisible = false;
  private attackPulseEndAlpha = 0;
  private attackPulseEndTimer = 0;
  private attackPulseEndDuration = 500;

  // Audio
  private musicVolume = 0.3;
  private sfxVolume = 0.6;
  private battleMusicStarted = false;
  private mapMusicLoaded = false;
  private userHasInteracted = false;

  private onChangeScene?: (sceneName: string) => void;
  private keys: Set<string> = new Set();

  constructor(onChangeScene?: (sceneName: string) => void) {
    this.onChangeScene = onChangeScene;
    this.loadAssets();
  }

  private async loadAssets(): Promise<void> {
    try {
      // Font should already be loaded by font_loader, but check anyway
      if (document.fonts.check('32px "Pokemon Pixel Font"')) {
        this.fontLoaded = true;
      } else {
        // Try to load if not already loaded
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
          this.dialogFont = '32px Arial, sans-serif';
        }
      }

      // Load map
      this.mapImage = await loadImage(`${Config.IMAGES_PATH}/map_background.png`);
      this.mapWidth = this.mapImage.width;
      this.mapHeight = this.mapImage.height;

      // Load character sprite
      const characterImg = await loadImage(`${Config.SPRITES_PATH}/character_red.png`);
      const characterSheet = new SpriteSheet(characterImg, 32, 42);
      this.characterSprite = new AnimatedSprite(characterSheet, 4);

      // Load Lugia sprites
      const lugiaImg = await loadImage(`${Config.SPRITES_PATH}/lugia.png`);
      const lugiaSheet = new SpriteSheet(lugiaImg, 132, 132);
      const numFrames = Math.floor(lugiaImg.width / 132);
      for (let i = 0; i < numFrames; i++) {
        const sprite = lugiaSheet.getSpriteAsCanvas(0, i);
        if (sprite) {
          const img = new Image();
          img.src = sprite.toDataURL();
          await new Promise((resolve) => {
            img.onload = resolve;
          });
          this.lugiaSprites.push(img);
        }
      }

      // Calculate Lugia position
      const gridSize = 32;
      const lugiaTargetCellX = Math.floor(this.mapWidth / 32) / 2 - 3;
      const lugiaTargetCellY = Math.floor(this.mapHeight / 32) / 4 - 5;
      const [lugiaPixelX, lugiaPixelY] = this.cellToPixel(lugiaTargetCellX, lugiaTargetCellY);
      this.lugiaTargetX = lugiaPixelX + 16;
      this.lugiaTargetY = lugiaPixelY;
      this.lugiaX = this.lugiaTargetX;

      // Load dialog
      this.dialogImage = await loadImage(`${Config.IMAGES_PATH}/dialog.png`);

      // Load exclamation mark
      this.exclamationImage = await loadImage(`${Config.IMAGES_PATH}/exclamation.png`);

      // Load fighting background
      this.fightingBackground = await loadImage(`${Config.IMAGES_PATH}/fighting_background.png`);

      // Load battle UI
      this.battleDialog = await loadImage(`${Config.IMAGES_PATH}/battle_dialog.png`);
      this.battleGrass = await loadImage(`${Config.IMAGES_PATH}/battle_grass.png`);
      this.battlePokemonstat = await loadImage(`${Config.IMAGES_PATH}/battle_lugia_stat.png`);
      this.battleWater = await loadImage(`${Config.IMAGES_PATH}/battle_water.png`);
      this.battleVenuStat = await loadImage(`${Config.IMAGES_PATH}/battle_venu_stat.png`);
      this.battleMenuUI = await loadImage(`${Config.IMAGES_PATH}/fight_ui.png`);
      this.bagScreenImage = await loadImage(`${Config.IMAGES_PATH}/screen-bag.png`).catch(() => null);
      this.pokemonScreenImage = await loadImage(`${Config.IMAGES_PATH}/screen-party.jpg`).catch(() => null);
      this.combatUI = await loadImage(`${Config.IMAGES_PATH}/combat-ui.png`).catch(() => null);
      this.attackPulseImage = await loadImage(`${Config.IMAGES_PATH}/attack_pulse.png`).catch(() => null);
      this.attackPulseEndImage = await loadImage(`${Config.IMAGES_PATH}/attack_pulse_end.png`).catch(() => null);

      // Load battle trainer
      const trainerImg = await loadImage(`${Config.SPRITES_PATH}/battle_trainer.png`);
      const trainerSheet = new SpriteSheet(trainerImg, 180, 128);
      const numTrainerFrames = Math.floor(trainerImg.width / 180);
      for (let i = 0; i < numTrainerFrames; i++) {
        const sprite = trainerSheet.getSpriteAsCanvas(0, i);
        if (sprite) {
          const img = new Image();
          img.src = sprite.toDataURL();
          await new Promise((resolve) => {
            img.onload = resolve;
          });
          this.battleTrainerSprites.push(img);
        }
      }

      // Load battle Lugia GIF - keep visible but off-screen so browser animates it
      // GIFs need to be visible (not display:none) and have proper dimensions to animate
      const battleLugiaImg = document.createElement('img');
      battleLugiaImg.style.position = 'fixed';
      battleLugiaImg.style.left = '-2000px';
      battleLugiaImg.style.top = '0';
      battleLugiaImg.style.width = '232px'; // Actual display width
      battleLugiaImg.style.height = 'auto';
      battleLugiaImg.style.opacity = '0.01'; // Nearly invisible but still "visible" to browser
      document.body.appendChild(battleLugiaImg);
      await new Promise((resolve, reject) => {
        battleLugiaImg.onload = resolve;
        battleLugiaImg.onerror = reject;
        battleLugiaImg.src = `${Config.SPRITES_PATH}/battle_lugia.gif`;
      });
      this.battleLugiaGif = battleLugiaImg;

      // Load battle Venusaur GIF - keep visible but off-screen so browser animates it
      const battleVenuImg = document.createElement('img');
      battleVenuImg.style.position = 'fixed';
      battleVenuImg.style.left = '-2000px';
      battleVenuImg.style.top = '0';
      battleVenuImg.style.width = '214px'; // Actual display width
      battleVenuImg.style.height = 'auto';
      battleVenuImg.style.opacity = '0.01'; // Nearly invisible but still "visible" to browser
      document.body.appendChild(battleVenuImg);
      await new Promise((resolve, reject) => {
        battleVenuImg.onload = resolve;
        battleVenuImg.onerror = reject;
        battleVenuImg.src = `${Config.SPRITES_PATH}/battle_venu.gif`;
      });
      this.battleVenuGif = battleVenuImg;

      // Set up battle positions
      this.setupBattlePositions();

      // Load audio
      await this.loadAudio();
    } catch (error) {
      console.error('Error loading assets:', error);
    }
  }

  private async loadAudio(): Promise<void> {
    try {
      // Load map music
      await audioManager.loadMusic(`${Config.SOUNDS_PATH}/mtmoon.wav`, true);
      this.mapMusicLoaded = true;

      // Load sound effects
      await audioManager.loadSoundEffect('collision', `${Config.SOUNDS_PATH}/SFX_COLLISION.wav`);
      await audioManager.loadSoundEffect('press_ab', `${Config.SOUNDS_PATH}/SFX_PRESS_AB.wav`);
      await audioManager.loadSoundEffect('ball_toss', `${Config.SOUNDS_PATH}/SFX_BALL_TOSS.wav`);
      await audioManager.loadSoundEffect('ball_poof', `${Config.SOUNDS_PATH}/SFX_BALL_POOF.wav`);
      await audioManager.loadSoundEffect('denied', `${Config.SOUNDS_PATH}/SFX_DENIED.wav`);
      await audioManager.loadSoundEffect('cry_17', `${Config.SOUNDS_PATH}/SFX_CRY_17.wav`);
      await audioManager.loadSoundEffect('spore', `${Config.SOUNDS_PATH}/spore.wav`);
      await audioManager.loadSoundEffect('spike_cannon', `${Config.SOUNDS_PATH}/spikecannon.wav`);

      // Set volumes
      audioManager.setMusicVolume(this.musicVolume);
      audioManager.setSfxVolume(this.sfxVolume);
    } catch (error) {
      console.warn('Error loading audio:', error);
    }
  }

  private setupBattlePositions(): void {
    if (!this.battleDialog || !this.battleGrass || !this.battleWater || !this.battlePokemonstat) return;

    // Battle dialog
    this.battleDialogX = (Config.SCREEN_WIDTH - this.battleDialog.width) / 2;
    this.battleDialogY = Config.SCREEN_HEIGHT - this.battleDialog.height;

    // Battle grass
    this.battleGrassLeftX = -this.battleGrass.width;
    if (this.battleDialog) {
      this.battleGrassY = Config.SCREEN_HEIGHT - this.battleDialog.height - this.battleGrass.height;
    }
    this.battleGrassLeftTargetX = 0;

    // Battle trainer
    if (this.battleTrainerSprites.length > 0) {
      this.battleTrainerX = Config.SCREEN_WIDTH;
      if (this.battleDialog) {
        this.battleTrainerY = Config.SCREEN_HEIGHT - this.battleDialog.height - 128;
      }
      this.battleTrainerTargetX = 0;
    }

    // Battle pokemonstat
    this.battlePokemonstatX = -this.battlePokemonstat.width;
    this.battlePokemonstatTargetX = 0;
    this.battlePokemonstatY = 0;

    // Battle water
    this.battleWaterX = Config.SCREEN_WIDTH;
    this.battleWaterTargetX = Config.SCREEN_WIDTH - this.battleWater.width;
    if (this.battlePokemonstat) {
      this.battleWaterY = this.battlePokemonstat.height;
    }

    // Battle Lugia
    if (this.battleLugiaGif && this.battleWater) {
      this.battleLugiaX = Config.SCREEN_WIDTH;
      const waterCenterX = this.battleWaterTargetX + this.battleWater.width / 2;
      const lugiaTargetWidth = 232; // Scaled width
      const lugiaScaleFactor = lugiaTargetWidth / this.battleLugiaGif.width;
      const lugiaScaledHeight = this.battleLugiaGif.height * lugiaScaleFactor;
      this.battleLugiaTargetX = waterCenterX - lugiaTargetWidth / 2;
      this.battleLugiaY = this.battleWaterY + this.battleWater.height - lugiaScaledHeight;
    }

    // Battle Venusaur
    if (this.battleVenuGif) {
      this.battleVenuY = Config.SCREEN_HEIGHT;
      const venuTargetWidth = 214; // Scaled width
      const venuScaleFactor = venuTargetWidth / this.battleVenuGif.width;
      const venuScaledHeight = this.battleVenuGif.height * venuScaleFactor;
      if (this.battleDialog) {
        this.battleVenuTargetY = Config.SCREEN_HEIGHT - this.battleDialog.height - venuScaledHeight + 40; // Decrease Y by 40px (was +80, now +40)
      }
      this.battleVenuX = 0;
    }

    // Battle Venusaur stat
    if (this.battleVenuStat) {
      this.battleVenuStatX = Config.SCREEN_WIDTH - this.battleVenuStat.width;
      if (this.battleDialog) {
        this.battleVenuStatY = Config.SCREEN_HEIGHT - this.battleDialog.height - this.battleVenuStat.height;
      }
    }

    // Calculate slide speeds
    this.calculateBattleSpeeds();
  }

  private calculateBattleSpeeds(): void {
    const distances: Record<string, number> = {};
    let maxDistance = 0;

    if (this.battleGrass) {
      const dist = Math.abs(this.battleGrassLeftTargetX - this.battleGrassLeftX);
      distances['grass'] = dist;
      maxDistance = Math.max(maxDistance, dist);
    }

    if (this.battlePokemonstat) {
      const dist = Math.abs(this.battlePokemonstatTargetX - this.battlePokemonstatX);
      distances['pokemonstat'] = dist;
      maxDistance = Math.max(maxDistance, dist);
    }

    if (this.battleWater) {
      const dist = Math.abs(this.battleWaterTargetX - this.battleWaterX);
      distances['water'] = dist;
      maxDistance = Math.max(maxDistance, dist);
    }

    if (this.battleTrainerSprites.length > 0) {
      const dist = Math.abs(this.battleTrainerTargetX - this.battleTrainerX);
      distances['trainer'] = dist;
      maxDistance = Math.max(maxDistance, dist);
    }

    if (maxDistance > 0) {
      if (distances['grass'] && distances['grass'] > 0) {
        this.battleGrassSpeed = (distances['grass'] / maxDistance) * this.battleSlideSpeedBase;
      }
      if (distances['pokemonstat'] && distances['pokemonstat'] > 0) {
        this.battlePokemonstatSpeed = (distances['pokemonstat'] / maxDistance) * this.battleSlideSpeedBase;
      }
      if (distances['water'] && distances['water'] > 0) {
        this.battleWaterSpeed = (distances['water'] / maxDistance) * this.battleSlideSpeedBase;
      }
      if (distances['trainer'] && distances['trainer'] > 0) {
        this.battleTrainerSpeed = (distances['trainer'] / maxDistance) * this.battleSlideSpeedBase;
      }
    }
  }

  private cellToPixel(cellX: number, cellY: number): [number, number] {
    const gridSize = 32;
    return [cellX * gridSize, cellY * gridSize];
  }

  private handleBattleMenuSelection(option: number): void {
    switch (option) {
      case 0: // Fight
        // Show combat UI instead of starting attack directly
        if (this.combatUI) {
          this.combatUIVisible = true;
          audioManager.playSoundEffect('press_ab');
          // Calculate combat UI grid dimensions
          if (this.combatUI) {
            const usableWidth = this.combatUI.width - (this.combatUIPadding * 2);
            const usableHeight = this.combatUI.height - (this.combatUIPadding * 2);
            // Left grid: 2x2 for moves
            this.combatUILeftGridContentWidth = usableWidth / 2; // Left half
            this.combatUILeftCellWidth = this.combatUILeftGridContentWidth / this.combatUILeftGridCols;
            this.combatUILeftCellHeight = usableHeight / this.combatUILeftGridRows;
            // Right grid: 2x2 for PP and Type info
            this.combatUIRightGridContentWidth = usableWidth / 2; // Right half
            this.combatUIRightCellWidth = this.combatUIRightGridContentWidth / this.combatUIRightGridCols;
            this.combatUIRightCellHeight = usableHeight / this.combatUIRightGridRows;
          }
        }
        break;
      case 1: // Bag
        if (this.bagScreenImage) {
          this.bagScreenVisible = true;
          this.battleMenuSelectedCell = 1; // Keep Bag highlighted
          audioManager.playSoundEffect('press_ab');
        }
        break;
      case 2: // Pokemon
        if (this.pokemonScreenImage) {
          this.pokemonScreenVisible = true;
          this.battleMenuSelectedCell = 2; // Keep Pokemon highlighted
          audioManager.playSoundEffect('press_ab');
        }
        break;
      case 3: // Run
        if (this.runTextVisible) {
          // Clicking again deselects
          this.runTextVisible = false;
          this.battleMenuSelectedCell = null;
        } else {
          // Show "Venusaur can't run away!" text
          this.runTextVisible = true;
          this.runTextAlpha = 255;
          this.battleMenuSelectedCell = 3; // Keep Run highlighted
          audioManager.playSoundEffect('denied');
        }
        break;
    }
  }

  onEnter(): void {
    const gridSize = 32;
    this.playerWorldX = 15 * gridSize + gridSize / 2;
    this.playerWorldY = 6 * gridSize + gridSize / 2;
    this.updateCamera();
    this.movingUp = false;
    this.movingDown = false;
    this.movingLeft = false;
    this.movingRight = false;
    this.currentDirection = 0;

    // Start map music
    if (this.mapMusicLoaded) {
      audioManager.playMusic(`${Config.SOUNDS_PATH}/mtmoon.wav`, true);
      this.battleMusicStarted = false;
    }
  }

  handleEvent(event: KeyboardEvent | MouseEvent): void {
    // Mark user interaction for audio
    if (!this.userHasInteracted) {
      this.userHasInteracted = true;
      if (this.mapMusicLoaded && !this.battleMusicStarted) {
        audioManager.playMusic(`${Config.SOUNDS_PATH}/mtmoon.wav`, true);
      }
    }

    if (event instanceof KeyboardEvent) {
      if (event.type === 'keydown') {
        if (event.key === 'r' || event.key === 'R') {
          this.onEnter();
          this.lugiaState = 'hidden';
          this.lugiaY = -200;
          this.lugiaAnimationComplete = false;
          this.dialogVisible = false;
          this.dialogFullyVisible = false;
          this.dialogSlideY = Config.SCREEN_HEIGHT;
          this.fadeState = 'none';
          this.fadeAlpha = 0;
          this.battleAnimationsStarted = false;
          
          // Reset text messages
          this.runTextVisible = false;
          this.runTextAlpha = 255;
          this.fullHPTextVisible = false;
          this.fullHPTextAlpha = 255;
          this.battleMenuSelectedCell = null;
          this.combatUIVisible = false;
          this.ballPoofPlayed = false;
          this.battleMenuVisible = false;
          this.battleMenuCursorPos = 0;
          this.lugiaCryFinished = false;
          this.allBattleElementsSlidIn = false;
          this.attackSequenceActive = false;
          this.attackPulseVisible = false;
          this.attackPulseEndVisible = false;
          // Stop any playing music and restart map music
          audioManager.stopMusic();
          if (this.mapMusicLoaded) {
            audioManager.playMusic(`${Config.SOUNDS_PATH}/mtmoon.wav`, true);
            this.battleMusicStarted = false;
          }
          return;
        }

        // Mute toggle (M key)
        if (event.key === 'm' || event.key === 'M') {
          audioManager.toggleMute();
          return;
        }

        // Battle menu navigation
        if (this.battleMenuVisible && this.fadeState === 'faded') {
          if (event.key === 'ArrowUp' || event.key === 'w' || event.key === 'W') {
            if (this.battleMenuCursorPos === 2 || this.battleMenuCursorPos === 3) {
              this.battleMenuCursorPos -= 2;
              audioManager.playSoundEffect('press_ab');
            }
            return;
          } else if (event.key === 'ArrowDown' || event.key === 's' || event.key === 'S') {
            if (this.battleMenuCursorPos === 0 || this.battleMenuCursorPos === 1) {
              this.battleMenuCursorPos += 2;
              audioManager.playSoundEffect('press_ab');
            }
            return;
          } else if (event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') {
            if (this.battleMenuCursorPos === 1 || this.battleMenuCursorPos === 3) {
              this.battleMenuCursorPos -= 1;
              audioManager.playSoundEffect('press_ab');
            }
            return;
          } else if (event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') {
            if (this.battleMenuCursorPos === 0 || this.battleMenuCursorPos === 2) {
              this.battleMenuCursorPos += 1;
              audioManager.playSoundEffect('press_ab');
            }
            return;
          } else if (event.key === 'Enter' || event.key === ' ') {
            // Handle menu selection
            audioManager.playSoundEffect('press_ab');
            this.handleBattleMenuSelection(this.battleMenuCursorPos);
            return;
          } else if (event.key === 'Escape' || event.key === 'Escape') {
            // Close bag/pokemon screens
            if (this.bagScreenVisible) {
              this.bagScreenVisible = false;
              audioManager.playSoundEffect('press_ab');
              return;
            }
            if (this.pokemonScreenVisible) {
              this.pokemonScreenVisible = false;
              audioManager.playSoundEffect('press_ab');
              return;
            }
          }
        }

        if (event.key === 'ArrowUp' || event.key === 'w' || event.key === 'W') {
          this.movingUp = true;
          this.currentDirection = 1;
        } else if (event.key === 'ArrowDown' || event.key === 's' || event.key === 'S') {
          this.movingDown = true;
          this.currentDirection = 0;
        } else if (event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') {
          this.movingLeft = true;
          this.currentDirection = 3;
        } else if (event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') {
          this.movingRight = true;
          this.currentDirection = 2;
        }
        this.keys.add(event.key);
      } else if (event.type === 'keyup') {
        if (event.key === 'ArrowUp' || event.key === 'w' || event.key === 'W') {
          this.movingUp = false;
        } else if (event.key === 'ArrowDown' || event.key === 's' || event.key === 'S') {
          this.movingDown = false;
        } else if (event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') {
          this.movingLeft = false;
        } else if (event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') {
          this.movingRight = false;
        }
        this.keys.delete(event.key);
      }
    } else if (event instanceof MouseEvent) {
      // Mark user interaction
      if (!this.userHasInteracted) {
        this.userHasInteracted = true;
        if (this.mapMusicLoaded && !this.battleMusicStarted) {
          audioManager.playMusic(`${Config.SOUNDS_PATH}/mtmoon.wav`, true);
        }
      }

      if (event.type === 'mousedown') {
        // Handle combat UI clicks (for Prompt Pulse)
        if (this.combatUIVisible && this.combatUI && !this.bagScreenVisible && !this.pokemonScreenVisible) {
          const canvas = (event.target as HTMLElement).closest('canvas') as HTMLCanvasElement;
          if (canvas) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (event.clientX - rect.left) * scaleX;
            const y = (event.clientY - rect.top) * scaleY;
            
            const combatUIX = 0;
            const combatUIY = Config.SCREEN_HEIGHT - this.combatUI.height;
            const leftGridX = combatUIX + this.combatUIPadding;
            const leftGridY = combatUIY + this.combatUIPadding;
            
            // Check if click is on left grid (moves)
            if (x >= leftGridX && x <= leftGridX + this.combatUILeftGridContentWidth &&
                y >= leftGridY && y <= leftGridY + (this.combatUILeftGridRows * this.combatUILeftCellHeight)) {
              const relativeX = x - leftGridX;
              const relativeY = y - leftGridY;
              const col = Math.floor(relativeX / this.combatUILeftCellWidth);
              const row = Math.floor(relativeY / this.combatUILeftCellHeight);
              const clampedCol = Math.max(0, Math.min(col, 1));
              const clampedRow = Math.max(0, Math.min(row, 1));
              const moveIndex = clampedRow * this.combatUILeftGridCols + clampedCol;
              
              if (moveIndex < this.combatUIMoveLabels.length) {
                const moveName = this.combatUIMoveLabels[moveIndex];
                
                // Play denied sound for greyed out moves, press AB for Prompt Pulse
                if (moveName === 'Context Recall' || moveName === 'Syntax Slash' || moveName === 'Debug Dash') {
                  audioManager.playSoundEffect('denied');
                } else if (moveName === 'Prompt Pulse') {
                  audioManager.playSoundEffect('press_ab');
                  // Start attack sequence
                  if (!this.attackSequenceActive && this.attackPulseImage) {
                    this.attackSequenceActive = true;
                    this.attackPulseVisible = true;
                    this.attackPulseAlpha = 255;
                    this.attackPulseScale = 0.5;
                    this.attackPulseTimer = 0;
                    this.attackPulseEndVisible = false;
                    this.attackPulseEndAlpha = 0;
                    this.attackPulseEndTimer = 0;
                    this.combatUIVisible = false; // Hide combat UI when attack starts
                    audioManager.playSoundEffect('spore'); // Play attack sound
                  }
                }
              }
              return;
            }
          }
        }
        
        // Handle battle menu clicks (accounting for padding like Python version)
        if (this.battleMenuVisible && this.fadeState === 'faded' && !this.bagScreenVisible && !this.pokemonScreenVisible && !this.combatUIVisible) {
          const canvas = (event.target as HTMLElement).closest('canvas') as HTMLCanvasElement;
          if (canvas) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (event.clientX - rect.left) * scaleX;
            const y = (event.clientY - rect.top) * scaleY;
            
            // Check if click is within menu bounds
            if (x >= this.battleMenuX && x <= this.battleMenuX + this.battleMenuUI!.width &&
                y >= this.battleMenuY && y <= this.battleMenuY + this.battleMenuUI!.height) {
              // Calculate relative position accounting for padding (like Python)
              const relativeX = x - this.battleMenuX - this.battleMenuPadding;
              const relativeY = y - this.battleMenuY - this.battleMenuPadding;
              const usableWidth = this.battleMenuUI!.width - (this.battleMenuPadding * 2);
              const usableHeight = this.battleMenuUI!.height - (this.battleMenuPadding * 2);
              
              // Check if within usable area (excluding padding)
              if (relativeX >= 0 && relativeX < usableWidth && relativeY >= 0 && relativeY < usableHeight) {
                // Determine which cell (row, col) - Python uses (row, col) format
                const col = Math.floor(relativeX / this.battleMenuOptionWidth);
                const row = Math.floor(relativeY / this.battleMenuOptionHeight);
                // Clamp to valid range
                const clampedCol = Math.max(0, Math.min(col, 1));
                const clampedRow = Math.max(0, Math.min(row, 1));
                // Convert (row, col) to option index: row 0, col 0 = 0 (FIGHT), row 0, col 1 = 1 (BAG), row 1, col 0 = 2 (POKEMON), row 1, col 1 = 3 (RUN)
                const clickedOption = clampedRow * 2 + clampedCol;
                
                if (clickedOption >= 0 && clickedOption < 4) {
                  audioManager.playSoundEffect('press_ab');
                  this.handleBattleMenuSelection(clickedOption);
                  return;
                }
              }
            }
          }
        }
        
        // Handle clicks on text messages (dismiss them)
        if (this.runTextVisible) {
          // Click anywhere to dismiss (no sound, handled in handleBattleMenuSelection)
          return;
        }
        if (this.fullHPTextVisible) {
          // Click anywhere to dismiss
          this.fullHPTextVisible = false;
          this.battleMenuSelectedCell = null;
          return;
        }
        
        // Handle bag screen USE button click
        if (this.bagScreenVisible && this.bagScreenImage) {
          const canvas = (event.target as HTMLElement).closest('canvas') as HTMLCanvasElement;
          if (canvas) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (event.clientX - rect.left) * scaleX;
            const y = (event.clientY - rect.top) * scaleY;
            
            // Check if click is on USE button (bottom right area)
            const textBoxWidth = 96;
            const textBoxHeight = 21;
            const textBoxX = Config.SCREEN_WIDTH - 8 - textBoxWidth;
            const textBoxY = Config.SCREEN_HEIGHT - 22 - textBoxHeight;
            
            if (x >= textBoxX && x <= textBoxX + textBoxWidth &&
                y >= textBoxY && y <= textBoxY + textBoxHeight) {
              // USE button clicked - show full HP message
              this.fullHPTextVisible = true;
              this.fullHPTextAlpha = 255;
              this.bagScreenVisible = false;
              this.battleMenuSelectedCell = 1; // Keep Bag highlighted
              audioManager.playSoundEffect('denied');
              return;
            }
          }
        }
        
        // Close bag/pokemon screens on click outside
        if (this.bagScreenVisible || this.pokemonScreenVisible) {
          this.bagScreenVisible = false;
          this.pokemonScreenVisible = false;
          this.battleMenuSelectedCell = null;
          audioManager.playSoundEffect('press_ab');
          return;
        }

        if (this.lugiaAnimationComplete && this.dialogFullyVisible && this.fadeState !== 'faded') {
          if (this.fightingBackground) {
            this.fadeState = 'fading';
            this.fadeAlpha = 0;
            // Play press AB sound when clicking to advance
            audioManager.playSoundEffect('press_ab');
          }
        }
      } else if (event.type === 'mousemove') {
        // Handle mouse hover for combat UI
        if (this.combatUIVisible && this.combatUI && !this.bagScreenVisible && !this.pokemonScreenVisible) {
          const canvas = (event.target as HTMLElement).closest('canvas') as HTMLCanvasElement;
          if (canvas) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (event.clientX - rect.left) * scaleX;
            const y = (event.clientY - rect.top) * scaleY;
            
            const combatUIX = 0;
            const combatUIY = Config.SCREEN_HEIGHT - this.combatUI.height;
            const leftGridX = combatUIX + this.combatUIPadding;
            const leftGridY = combatUIY + this.combatUIPadding;
            
            // Check if mouse is on left grid (moves)
            if (x >= leftGridX && x <= leftGridX + this.combatUILeftGridContentWidth &&
                y >= leftGridY && y <= leftGridY + (this.combatUILeftGridRows * this.combatUILeftCellHeight)) {
              const relativeX = x - leftGridX;
              const relativeY = y - leftGridY;
              const col = Math.floor(relativeX / this.combatUILeftCellWidth);
              const row = Math.floor(relativeY / this.combatUILeftCellHeight);
              const clampedCol = Math.max(0, Math.min(col, 1));
              const clampedRow = Math.max(0, Math.min(row, 1));
              this.combatUIHoveredCell = { gridSide: 'left', row: clampedRow, col: clampedCol };
            } else {
              this.combatUIHoveredCell = null;
            }
          }
        }
        
        // Handle mouse hover for battle menu (accounting for padding like Python version)
        if (this.battleMenuVisible && this.fadeState === 'faded' && !this.bagScreenVisible && !this.pokemonScreenVisible && !this.combatUIVisible) {
          const canvas = (event.target as HTMLElement).closest('canvas') as HTMLCanvasElement;
          if (canvas) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (event.clientX - rect.left) * scaleX;
            const y = (event.clientY - rect.top) * scaleY;
            
            // Check if mouse is within menu bounds
            if (x >= this.battleMenuX && x <= this.battleMenuX + this.battleMenuUI!.width &&
                y >= this.battleMenuY && y <= this.battleMenuY + this.battleMenuUI!.height) {
              // Calculate relative position accounting for padding (like Python)
              const relativeX = x - this.battleMenuX - this.battleMenuPadding;
              const relativeY = y - this.battleMenuY - this.battleMenuPadding;
              const usableWidth = this.battleMenuUI!.width - (this.battleMenuPadding * 2);
              const usableHeight = this.battleMenuUI!.height - (this.battleMenuPadding * 2);
              
              // Check if within usable area (excluding padding)
              if (relativeX >= 0 && relativeX < usableWidth && relativeY >= 0 && relativeY < usableHeight) {
                // Determine which cell (row, col) - Python uses (row, col) format
                const col = Math.floor(relativeX / this.battleMenuOptionWidth);
                const row = Math.floor(relativeY / this.battleMenuOptionHeight);
                // Clamp to valid range
                const clampedCol = Math.max(0, Math.min(col, 1));
                const clampedRow = Math.max(0, Math.min(row, 1));
                // Convert (row, col) to option index
                const hoveredOption = clampedRow * 2 + clampedCol;
                
                if (hoveredOption >= 0 && hoveredOption < 4) {
                  this.battleMenuHoveredOption = hoveredOption;
                  this.battleMenuCursorPos = hoveredOption;
                } else {
                  this.battleMenuHoveredOption = null;
                }
              } else {
                this.battleMenuHoveredOption = null;
              }
            } else {
              this.battleMenuHoveredOption = null;
            }
          }
        }
      }
    }
  }

  private updateCamera(): void {
    const targetCameraX = this.playerWorldX - Config.SCREEN_WIDTH / 2;
    const targetCameraY = this.playerWorldY - Config.SCREEN_HEIGHT / 2;

    const minCameraX = 0;
    const maxCameraX = Math.max(0, this.mapWidth - Config.SCREEN_WIDTH);
    const minCameraY = 0;
    const maxCameraY = Math.max(0, this.mapHeight - Config.SCREEN_HEIGHT);

    this.cameraX = Math.max(minCameraX, Math.min(targetCameraX, maxCameraX));
    this.cameraY = Math.max(minCameraY, Math.min(targetCameraY, maxCameraY));
  }

  update(deltaTime: number): void {
    // Stop player movement when dialog is visible
    if (this.dialogVisible || (this.lugiaState !== 'hidden' && !this.lugiaAnimationComplete)) {
      // Player cannot move
    } else {
      let dx = 0;
      let dy = 0;

      if (this.movingLeft) {
        dx -= Config.PLAYER_SPEED;
        this.currentDirection = 3;
      }
      if (this.movingRight) {
        dx += Config.PLAYER_SPEED;
        this.currentDirection = 2;
      }
      if (this.movingUp) {
        dy -= Config.PLAYER_SPEED;
        this.currentDirection = 1;
      }
      if (this.movingDown) {
        dy += Config.PLAYER_SPEED;
        this.currentDirection = 0;
      }

      if (dx !== 0 || dy !== 0) {
        let newX = this.playerWorldX + dx;
        let newY = this.playerWorldY + dy;

        const margin = 10;
        newX = Math.max(margin, Math.min(newX, this.mapWidth - this.playerWidth - margin));
        newY = Math.max(margin, Math.min(newY, this.mapHeight - this.playerHeight - margin));

        const gridSize = 32;
        const playerCenterX = newX + this.playerWidth / 2;
        const playerCenterY = newY + this.playerHeight / 2;
        const playerCellX = Math.floor(playerCenterX / gridSize);
        const playerCellY = Math.floor(playerCenterY / gridSize);

        let isWalkable = false;

        // Check rectangles
        for (const [minX, minY, maxX, maxY] of this.walkableRectangles) {
          if (playerCellX >= minX && playerCellX <= maxX && playerCellY >= minY && playerCellY <= maxY) {
            isWalkable = true;
            break;
          }
        }

        // Check individual cells
        if (!isWalkable) {
          for (const [cellX, cellY] of this.walkableCells) {
            if (playerCellX === cellX && playerCellY === cellY) {
              isWalkable = true;
              break;
            }
          }
        }

        if (isWalkable) {
          this.playerWorldX = newX;
          this.playerWorldY = newY;
        } else {
          // Play collision sound when hitting border
          audioManager.playSoundEffect('collision');
          // No exclamation mark for wall collisions - only for Lugia encounters
        }
      }
    }

    this.updateCamera();

    // Update animation
    if (this.characterSprite) {
      const canMove = this.lugiaState === 'hidden' || this.lugiaAnimationComplete;
      const isMoving = (this.movingUp || this.movingDown || this.movingLeft || this.movingRight) && canMove;
      this.characterSprite.update(this.currentDirection, isMoving, deltaTime);
    }

    // Check if player is under Lugia
    const gridSize = 32;
    const lugiaLeftCellX = Math.floor(this.lugiaTargetX / gridSize);
    const lugiaRightCellX = Math.floor((this.lugiaTargetX + 132) / gridSize);
    const lugiaBottomY = this.lugiaTargetY + 132;
    const lugiaBottomCellY = Math.floor(lugiaBottomY / gridSize);

    const playerCellX = Math.floor((this.playerWorldX + this.playerWidth / 2) / gridSize);
    const playerCellY = Math.floor((this.playerWorldY + this.playerHeight / 2) / gridSize);

    const underLugia = lugiaLeftCellX <= playerCellX && playerCellX <= lugiaRightCellX && playerCellY === lugiaBottomCellY;

    // Update Lugia state machine
    if (this.lugiaState === 'hidden' && underLugia) {
      this.lugiaState = 'flying_in';
      // Show exclamation mark when encountering Lugia
      if (!this.exclamationVisible) {
        this.exclamationVisible = true;
        this.exclamationTimer = 0;
        this.exclamationY = 0;
        // Play exclamation sound on encounter
        audioManager.playSoundEffect('press_ab');
      }
    } else if (this.lugiaState === 'flying_in') {
      if (this.lugiaY < this.lugiaTargetY) {
        this.lugiaY += this.lugiaFlySpeed;
      } else {
        this.lugiaY = this.lugiaTargetY;
        this.lugiaState = 'animating';
        this.lugiaCurrentFrame = 0;
      }
    } else if (this.lugiaState === 'animating') {
      if (this.lugiaSprites.length > 0) {
        this.lugiaAnimationTime += this.lugiaAnimationSpeed * (deltaTime / 16.67);
        if (this.lugiaAnimationTime >= 1.0) {
          this.lugiaAnimationTime = 0;
          this.lugiaCurrentFrame += 1;

          if (this.lugiaCurrentFrame >= this.lugiaSprites.length) {
            this.lugiaCurrentFrame = this.lugiaSprites.length - 1;
            this.lugiaState = 'stopped';
            this.lugiaAnimationComplete = true;
            // Play Lugia cry sound immediately when animation completes
            // Don't show dialog until cry finishes
            this.lugiaCryFinished = false;
            const cryAudio = audioManager.playSoundEffect('cry_17');
            // Track when cry finishes
            if (cryAudio) {
              cryAudio.addEventListener('ended', () => {
                this.lugiaCryFinished = true;
              });
            } else {
              // Fallback: if audio fails to load, wait 1.5 seconds
              setTimeout(() => {
                this.lugiaCryFinished = true;
              }, 1500);
            }
          }
        }
      }
    } else if (this.lugiaState === 'stopped') {
      if (this.lugiaSprites.length > 0) {
        this.lugiaCurrentFrame = this.lugiaSprites.length - 1;
      }
    }

    // Update exclamation mark popup
    if (this.exclamationVisible) {
      this.exclamationTimer += deltaTime;
      // Animate exclamation mark bouncing up
      if (this.exclamationTimer < this.exclamationDuration) {
        const progress = this.exclamationTimer / this.exclamationDuration;
        this.exclamationY = -20 * Math.sin(progress * Math.PI); // Bounce animation
      } else {
        this.exclamationVisible = false;
        this.exclamationTimer = 0;
        this.exclamationY = 0;
      }
    }

    // Show dialog only after Lugia cry finishes
    if (this.lugiaAnimationComplete && !this.dialogVisible && this.lugiaCryFinished) {
      this.dialogVisible = true;
      this.dialogFullyVisible = false;
      this.dialogSlideY = Config.SCREEN_HEIGHT;
      this.dialogText = 'Lugia wants to battle!';
    }

    // Update dialog slide animation
    if (this.dialogVisible) {
      const dialogHeight = this.dialogImage ? this.dialogImage.height : 56;
      const dialogTargetY = Config.SCREEN_HEIGHT - dialogHeight;

      if (this.dialogSlideY > dialogTargetY) {
        this.dialogSlideY -= this.dialogSlideSpeed;
        if (this.dialogSlideY <= dialogTargetY) {
          this.dialogSlideY = dialogTargetY;
          this.dialogFullyVisible = true;
          // Play dialog appear sound immediately when dialog reaches position
          audioManager.playSoundEffect('press_ab');
        } else {
          // Play sound earlier, when dialog starts sliding in
          if (this.dialogSlideY === Config.SCREEN_HEIGHT - 1) {
            audioManager.playSoundEffect('press_ab');
          }
        }
      } else {
        if (!this.dialogFullyVisible) {
          this.dialogFullyVisible = true;
          // Play dialog appear sound
          audioManager.playSoundEffect('press_ab');
        }
      }

      if (this.dialogFullyVisible && this.lugiaAnimationComplete && this.fadeState === 'none') {
        this.dialogPauseTimer += deltaTime;
        if (this.dialogPauseTimer >= this.dialogPauseDuration) {
          if (this.fightingBackground) {
            this.fadeState = 'fading';
            this.fadeAlpha = 0;
            this.dialogPauseTimer = 0;
          }
        }
      }

      if (this.fadeState === 'fading') {
        this.dialogSlideY += this.dialogSlideSpeed;
        if (this.dialogSlideY >= Config.SCREEN_HEIGHT) {
          this.dialogVisible = false;
        }
      }
    }

    // Handle fade transition
    if (this.fadeState === 'fading') {
      this.fadeAlpha += this.fadeSpeed * (deltaTime / 16.67);
      if (this.fadeAlpha >= 255) {
        this.fadeAlpha = 255;
        this.fadeState = 'faded';
        this.fadeComplete = true;
        if (!this.battleAnimationsStarted) {
          this.battleAnimationsStarted = true;
          this.battleDialogVisible = true;
          this.battleDialogAlpha = 255; // Make dialog fully visible immediately
          this.battleGrassVisible = true;
          this.battlePokemonstatVisible = true;
          this.battleWaterVisible = true;
          this.battleLugiaVisible = true;
          this.battleTrainerVisible = true;
          if (this.battleVenuStat) {
            this.battleVenuStatVisible = true;
          }

          // Start battle music (this will stop map music automatically)
          if (!this.battleMusicStarted) {
            // Stop map music before starting battle music
            audioManager.stopMusic();
            audioManager.playMusic(`${Config.SOUNDS_PATH}/battle.wav`, true);
            this.battleMusicStarted = true;
            // Play battle start sound effect immediately
            audioManager.playSoundEffect('cry_17');
            // Show health bars when battle starts
            this.healthBarVisible = true;
          }
        }
      }
    }

    // Update battle UI animations
    if (this.fadeState === 'fading') {
      if (this.battleDialogVisible && this.battleDialog) {
        // Fade in dialog as screen fades
        this.battleDialogAlpha = Math.min(255, Math.floor(this.fadeAlpha));
      }
    }

    if (this.fadeState === 'faded') {
      if (this.battleDialogVisible && this.battleDialog) {
        // Ensure dialog is fully visible after fade completes
        this.battleDialogAlpha = 255;
      }

      // Battle grass
      if (this.battleGrassVisible && this.battleGrass) {
        if (this.battleGrassLeftX < this.battleGrassLeftTargetX) {
          this.battleGrassLeftX += this.battleGrassSpeed;
          if (this.battleGrassLeftX >= this.battleGrassLeftTargetX) {
            this.battleGrassLeftX = this.battleGrassLeftTargetX;
          }
        }
      }

      // Battle pokemonstat
      if (this.battlePokemonstatVisible && this.battlePokemonstat) {
        if (this.battlePokemonstatX < this.battlePokemonstatTargetX) {
          this.battlePokemonstatX += this.battlePokemonstatSpeed;
          if (this.battlePokemonstatX >= this.battlePokemonstatTargetX) {
            this.battlePokemonstatX = this.battlePokemonstatTargetX;
          }
        }
      }

      // Battle water
      if (this.battleWaterVisible && this.battleWater) {
        if (this.battleWaterX > this.battleWaterTargetX) {
          this.battleWaterX -= this.battleWaterSpeed;
          if (this.battleWaterX <= this.battleWaterTargetX) {
            this.battleWaterX = this.battleWaterTargetX;
          }
        }
      }

      // Battle Lugia
      if (this.battleLugiaVisible && this.battleLugiaGif) {
        if (this.battleLugiaX > this.battleLugiaTargetX) {
          this.battleLugiaX -= this.battleWaterSpeed;
          if (this.battleLugiaX <= this.battleLugiaTargetX) {
            this.battleLugiaX = this.battleLugiaTargetX;
          }
        }
        // Browser handles GIF animation automatically when drawn from img element
      }

      // Battle trainer
      if (this.battleTrainerVisible && this.battleTrainerSprites.length > 0) {
        if (this.battleTrainerX > this.battleTrainerTargetX) {
          this.battleTrainerX -= this.battleTrainerSpeed;
          if (this.battleTrainerX <= this.battleTrainerTargetX) {
            this.battleTrainerX = this.battleTrainerTargetX;
          }
        }

        let allAnimationsComplete = true;
        if (this.battleGrassVisible && this.battleGrass) {
          if (this.battleGrassLeftX !== this.battleGrassLeftTargetX) {
            allAnimationsComplete = false;
          }
        }
        if (this.battlePokemonstatVisible && this.battlePokemonstat) {
          if (this.battlePokemonstatX !== this.battlePokemonstatTargetX) {
            allAnimationsComplete = false;
          }
        }
        if (this.battleWaterVisible && this.battleWater) {
          if (this.battleWaterX !== this.battleWaterTargetX) {
            allAnimationsComplete = false;
          }
        }
        if (this.battleTrainerX !== this.battleTrainerTargetX) {
          allAnimationsComplete = false;
        }

        if (allAnimationsComplete && !this.allBattleElementsSlidIn) {
          this.allBattleElementsSlidIn = true;
          this.battleTrainerCanAnimate = true;
        }

        // Only animate trainer and throw ball after all elements have slid in
        if (this.allBattleElementsSlidIn && this.battleTrainerCanAnimate && this.battleTrainerX === this.battleTrainerTargetX && !this.battleTrainerSlideOut) {
          this.battleTrainerAnimationTime += this.battleTrainerAnimationSpeed * (deltaTime / 16.67);
          if (this.battleTrainerAnimationTime >= 1.0) {
            this.battleTrainerAnimationTime = 0;
            if (this.battleTrainerCurrentFrame < this.battleTrainerSprites.length - 1) {
              this.battleTrainerCurrentFrame += 1;
            } else {
              // Trainer throws pokeball - play ball toss sound
              audioManager.playSoundEffect('ball_toss');
              this.battleVenuVisible = true;
              if (!this.battleTextFading) {
                this.battleTextFading = true;
                this.battleTextState = 'transitioning';
              }
              this.battleTrainerSlideOut = true;
              this.battleTrainerAlpha = 255;
            }
          }
        }

        if (this.battleTrainerSlideOut) {
          const trainerSlideOutTarget = -180;
          if (this.battleTrainerX > trainerSlideOutTarget) {
            this.battleTrainerX -= this.battleTrainerSpeed;
            const totalSlideDistance = Math.abs(this.battleTrainerTargetX - trainerSlideOutTarget);
            const currentSlideDistance = Math.abs(this.battleTrainerX - this.battleTrainerTargetX);
            const fadeProgress = Math.min(1.0, currentSlideDistance / totalSlideDistance);
            this.battleTrainerAlpha = Math.floor(255 * (1.0 - fadeProgress));
          }

          if (this.battleTrainerX <= trainerSlideOutTarget || this.battleTrainerAlpha <= 0) {
            this.battleTrainerAlpha = 0;
            this.battleTrainerVisible = false;
          }
        }
      }

      // Battle Venusaur
      if (this.battleVenuVisible && this.battleVenuGif) {
        if (this.battleVenuY > this.battleVenuTargetY) {
          this.battleVenuY -= this.battleTrainerSpeed;
          if (this.battleVenuY <= this.battleVenuTargetY) {
            this.battleVenuY = this.battleVenuTargetY;
            // Play ball poof sound when Venusaur appears (pokeball opens)
            if (!this.ballPoofPlayed) {
              audioManager.playSoundEffect('ball_poof');
              this.ballPoofPlayed = true;
            }
          }
        } else {
          // Venusaur is at target position, play poof sound if not already played
          if (!this.ballPoofPlayed) {
            audioManager.playSoundEffect('ball_poof');
            this.ballPoofPlayed = true;
          }
        }
        // Browser handles GIF animation automatically when drawn from img element
      }

      // Handle text fade transition
      if (this.battleTextFading) {
        if (this.battleTextLugiaAlpha > 0) {
          this.battleTextLugiaAlpha = Math.max(0, this.battleTextLugiaAlpha - this.battleTextFadeSpeed * (deltaTime / 16.67));
        }
        if (this.battleTextLugiaAlpha === 0 && this.battleTextVenusaurAlpha < 255) {
          this.battleTextVenusaurAlpha = Math.min(255, this.battleTextVenusaurAlpha + this.battleTextFadeSpeed * (deltaTime / 16.67));
          if (this.battleTextVenusaurAlpha >= 255) {
            this.battleTextState = 'venusaur';
            this.battleTextFading = false;
            // Show battle menu when Venusaur text is fully visible
            this.battleMenuVisible = true;
          }
        }
      }
      
      // Update attack sequence
      if (this.attackSequenceActive) {
        if (this.attackPulseVisible) {
          this.attackPulseTimer += deltaTime;
          const progress = Math.min(1.0, this.attackPulseTimer / this.attackPulseDuration);
          
          // Pulse animation: scale up and fade
          this.attackPulseScale = 0.5 + (progress * 1.5); // Scale from 0.5 to 2.0
          this.attackPulseAlpha = 255 * (1.0 - progress); // Fade out
          
          if (progress >= 1.0) {
            this.attackPulseVisible = false;
            // Show pulse end effect
            if (this.attackPulseEndImage) {
              this.attackPulseEndVisible = true;
              this.attackPulseEndAlpha = 255;
              this.attackPulseEndTimer = 0;
              // Play impact sound
              audioManager.playSoundEffect('spike_cannon');
            } else {
              // No end image, just finish sequence
              this.attackSequenceActive = false;
            }
          }
        }
        
        if (this.attackPulseEndVisible) {
          this.attackPulseEndTimer += deltaTime;
          const progress = Math.min(1.0, this.attackPulseEndTimer / this.attackPulseEndDuration);
          
          // Fade out end effect
          this.attackPulseEndAlpha = 255 * (1.0 - progress);
          
          if (progress >= 1.0) {
            this.attackPulseEndVisible = false;
            this.attackSequenceActive = false;
          }
        }
      }
    }
  }

  render(ctx: CanvasRenderingContext2D): void {
    // If fully faded, show battle screen
    if (this.fadeState === 'faded' && this.fightingBackground) {
      // Draw fighting background
      ctx.drawImage(this.fightingBackground, 0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT);

      // Draw battle UI elements
      if (this.battleGrassVisible && this.battleGrass) {
        ctx.drawImage(this.battleGrass, this.battleGrassLeftX, this.battleGrassY);
      }

      if (this.battleTrainerVisible && this.battleTrainerSprites.length > 0 && this.battleTrainerAlpha > 0) {
        const frame = Math.min(this.battleTrainerCurrentFrame, this.battleTrainerSprites.length - 1);
        const trainerSprite = this.battleTrainerSprites[frame];
        // During battle (fadeState === 'faded'), always render at 100% opacity
        if (this.fadeState === 'faded') {
          ctx.drawImage(trainerSprite, this.battleTrainerX, this.battleTrainerY);
        } else {
          // Only use alpha during fade transitions
          ctx.globalAlpha = this.battleTrainerAlpha / 255;
          ctx.drawImage(trainerSprite, this.battleTrainerX, this.battleTrainerY);
          ctx.globalAlpha = 1.0;
        }
      }

      if (this.battleWaterVisible && this.battleWater) {
        ctx.drawImage(this.battleWater, this.battleWaterX, this.battleWaterY);
      }

      if (this.battleLugiaVisible && this.battleLugiaGif) {
        // Use natural dimensions to avoid stretching, scale to 232px width
        const targetWidth = 232;
        const naturalWidth = this.battleLugiaGif.naturalWidth || this.battleLugiaGif.width;
        const naturalHeight = this.battleLugiaGif.naturalHeight || this.battleLugiaGif.height;
        const scaleFactor = targetWidth / naturalWidth;
        const scaledHeight = naturalHeight * scaleFactor;
        // Draw the animated GIF - browser handles animation automatically
        // Draw from img element directly to keep animation going, use natural dimensions
        ctx.imageSmoothingEnabled = false; // Pixel-perfect rendering
        ctx.drawImage(this.battleLugiaGif, 0, 0, naturalWidth, naturalHeight, this.battleLugiaX, this.battleLugiaY, targetWidth, scaledHeight);
        ctx.imageSmoothingEnabled = true;
      }

      if (this.battlePokemonstatVisible && this.battlePokemonstat) {
        ctx.drawImage(this.battlePokemonstat, this.battlePokemonstatX, this.battlePokemonstatY);
        
        // Draw Lugia health bar (green bar on the stat image)
        if (this.healthBarVisible && this.battlePokemonstat) {
          // Health bar position relative to stat image
          // 26px from right, 18px from bottom of container
          const statImage = this.battlePokemonstat;
          const healthBarWidth = 96; // Fixed width as per Python version
          const healthBarHeight = 6; // Fixed height as per Python version
          const healthBarX = this.battlePokemonstatX + statImage.width - healthBarWidth - 26; // 26px from right
          const healthBarY = this.battlePokemonstatY + statImage.height - 18 - healthBarHeight; // 18px from bottom
          
          // Draw green health bar (current HP / max HP) - no border, color #70F8A8
          const healthPercentage = Math.max(0, Math.min(1, this.lugiaCurrentHP / this.lugiaMaxHP));
          const healthBarFillWidth = healthBarWidth * healthPercentage;
          if (healthBarFillWidth > 0) {
            ctx.fillStyle = '#70F8A8'; // Light green color from Python version
            ctx.fillRect(healthBarX, healthBarY, healthBarFillWidth, healthBarHeight);
          }
        }
      }

      if (this.battleVenuVisible && this.battleVenuGif) {
        // Use natural dimensions to avoid stretching, scale to 214px width
        const targetWidth = 214;
        const naturalWidth = this.battleVenuGif.naturalWidth || this.battleVenuGif.width;
        const naturalHeight = this.battleVenuGif.naturalHeight || this.battleVenuGif.height;
        const scaleFactor = targetWidth / naturalWidth;
        const scaledHeight = naturalHeight * scaleFactor;
        // Draw the animated GIF - browser handles animation automatically
        // Draw from img element directly to keep animation going, use natural dimensions
        ctx.imageSmoothingEnabled = false; // Pixel-perfect rendering
        ctx.drawImage(this.battleVenuGif, 0, 0, naturalWidth, naturalHeight, this.battleVenuX, this.battleVenuY, targetWidth, scaledHeight);
        ctx.imageSmoothingEnabled = true;
      }

      if (this.battleVenuStatVisible && this.battleVenuStat) {
        ctx.drawImage(this.battleVenuStat, this.battleVenuStatX, this.battleVenuStatY);
        
        // Draw Venusaur health bar (green bar on the stat image)
        if (this.healthBarVisible && this.battleVenuStat) {
          // Health bar position relative to stat image
          // 16px from right, 34px from bottom of container
          const statImage = this.battleVenuStat;
          const healthBarWidth = 96; // Fixed width as per Python version
          const healthBarHeight = 6; // Fixed height as per Python version
          const healthBarX = this.battleVenuStatX + statImage.width - healthBarWidth - 16; // 16px from right
          const healthBarY = this.battleVenuStatY + statImage.height - 34 - healthBarHeight; // 34px from bottom
          
          // Draw green health bar (current HP / max HP) - no border, color #70F8A8
          const healthPercentage = Math.max(0, Math.min(1, this.venusaurCurrentHP / this.venusaurMaxHP));
          const healthBarFillWidth = healthBarWidth * healthPercentage;
          if (healthBarFillWidth > 0) {
            ctx.fillStyle = '#70F8A8'; // Light green color from Python version
            ctx.fillRect(healthBarX, healthBarY, healthBarFillWidth, healthBarHeight);
          }
        }
      }

      // Draw battle dialog
      if (this.battleDialogVisible && this.battleDialog) {
        ctx.globalAlpha = this.battleDialogAlpha / 255;
        ctx.drawImage(this.battleDialog, this.battleDialogX, this.battleDialogY);
        ctx.globalAlpha = 1.0;

        // Draw battle dialog text
        if (this.battleDialogAlpha >= 255) {
          ctx.fillStyle = 'rgb(255, 255, 255)'; // White text
          ctx.font = this.dialogFont;
          ctx.textAlign = 'left';
          ctx.textBaseline = 'top';
          const textX = 32;
          const dialogHeight = this.battleDialog.height;
          const maxTextWidth = Config.SCREEN_WIDTH / 2;

          // Lugia text
          const lugiaLine1 = 'A wild Bugia';
          const lugiaLine2 = 'appeared!';
          
          // Measure text
          ctx.font = this.dialogFont;
          const lugiaLine1Metrics = ctx.measureText(lugiaLine1);
          const lugiaLine2Metrics = ctx.measureText(lugiaLine2);
          
          // Scale down if needed (like original)
          let lugiaLine1Width = lugiaLine1Metrics.width;
          let lugiaLine1Height = lugiaLine1Metrics.actualBoundingBoxAscent + lugiaLine1Metrics.actualBoundingBoxDescent;
          let lugiaLine2Width = lugiaLine2Metrics.width;
          let lugiaLine2Height = lugiaLine2Metrics.actualBoundingBoxAscent + lugiaLine2Metrics.actualBoundingBoxDescent;
          
          if (lugiaLine1Width > maxTextWidth) {
            const scaleFactor = maxTextWidth / lugiaLine1Width;
            lugiaLine1Width *= scaleFactor;
            lugiaLine1Height *= scaleFactor;
          }
          if (lugiaLine2Width > maxTextWidth) {
            const scaleFactor = maxTextWidth / lugiaLine2Width;
            lugiaLine2Width *= scaleFactor;
            lugiaLine2Height *= scaleFactor;
          }
          
          const totalTextHeight = lugiaLine1Height + lugiaLine2Height;
          const line1Y = this.battleDialogY + (dialogHeight - totalTextHeight) / 2;
          const line2Y = line1Y + lugiaLine1Height;

          // Draw Lugia text with fade
          if (this.battleTextLugiaAlpha > 0) {
            ctx.globalAlpha = this.battleTextLugiaAlpha / 255;
            if (lugiaLine1Width !== lugiaLine1Metrics.width) {
              // Need to scale - create a temporary canvas
              const tempCanvas = document.createElement('canvas');
              const tempCtx = tempCanvas.getContext('2d');
              if (tempCtx) {
                tempCanvas.width = lugiaLine1Width;
                tempCanvas.height = lugiaLine1Height;
                tempCtx.font = this.dialogFont;
                tempCtx.fillStyle = 'rgb(255, 255, 255)';
                tempCtx.fillText(lugiaLine1, 0, lugiaLine1Height * 0.8);
                ctx.drawImage(tempCanvas, textX, line1Y);
              }
            } else {
              ctx.fillText(lugiaLine1, textX, line1Y);
            }
            if (lugiaLine2Width !== lugiaLine2Metrics.width) {
              const tempCanvas = document.createElement('canvas');
              const tempCtx = tempCanvas.getContext('2d');
              if (tempCtx) {
                tempCanvas.width = lugiaLine2Width;
                tempCanvas.height = lugiaLine2Height;
                tempCtx.font = this.dialogFont;
                tempCtx.fillStyle = 'rgb(255, 255, 255)';
                tempCtx.fillText(lugiaLine2, 0, lugiaLine2Height * 0.8);
                ctx.drawImage(tempCanvas, textX, line2Y);
              }
            } else {
              ctx.fillText(lugiaLine2, textX, line2Y);
            }
          }

          // Venusaur text
          const venusaurLine1 = 'What should';
          const venusaurLine2 = 'Venusaur do?';
          
          const venusaurLine1Metrics = ctx.measureText(venusaurLine1);
          const venusaurLine2Metrics = ctx.measureText(venusaurLine2);
          
          let venusaurLine1Width = venusaurLine1Metrics.width;
          let venusaurLine1Height = venusaurLine1Metrics.actualBoundingBoxAscent + venusaurLine1Metrics.actualBoundingBoxDescent;
          let venusaurLine2Width = venusaurLine2Metrics.width;
          let venusaurLine2Height = venusaurLine2Metrics.actualBoundingBoxAscent + venusaurLine2Metrics.actualBoundingBoxDescent;
          
          if (venusaurLine1Width > maxTextWidth) {
            const scaleFactor = maxTextWidth / venusaurLine1Width;
            venusaurLine1Width *= scaleFactor;
            venusaurLine1Height *= scaleFactor;
          }
          if (venusaurLine2Width > maxTextWidth) {
            const scaleFactor = maxTextWidth / venusaurLine2Width;
            venusaurLine2Width *= scaleFactor;
            venusaurLine2Height *= scaleFactor;
          }

          // Draw Venusaur text with fade
          if (this.battleTextVenusaurAlpha > 0) {
            ctx.globalAlpha = this.battleTextVenusaurAlpha / 255;
            if (venusaurLine1Width !== venusaurLine1Metrics.width) {
              const tempCanvas = document.createElement('canvas');
              const tempCtx = tempCanvas.getContext('2d');
              if (tempCtx) {
                tempCanvas.width = venusaurLine1Width;
                tempCanvas.height = venusaurLine1Height;
                tempCtx.font = this.dialogFont;
                tempCtx.fillStyle = 'rgb(255, 255, 255)';
                tempCtx.fillText(venusaurLine1, 0, venusaurLine1Height * 0.8);
                ctx.drawImage(tempCanvas, textX, line1Y);
              }
            } else {
              ctx.fillText(venusaurLine1, textX, line1Y);
            }
            if (venusaurLine2Width !== venusaurLine2Metrics.width) {
              const tempCanvas = document.createElement('canvas');
              const tempCtx = tempCanvas.getContext('2d');
              if (tempCtx) {
                tempCanvas.width = venusaurLine2Width;
                tempCanvas.height = venusaurLine2Height;
                tempCtx.font = this.dialogFont;
                tempCtx.fillStyle = 'rgb(255, 255, 255)';
                tempCtx.fillText(venusaurLine2, 0, venusaurLine2Height * 0.8);
                ctx.drawImage(tempCanvas, textX, line2Y);
              }
            } else {
              ctx.fillText(venusaurLine2, textX, line2Y);
            }
          }

          ctx.globalAlpha = 1.0;
        }
      }

      // Draw text messages (Run and Full HP) - above battle dialog
      if (this.runTextVisible && this.battleDialog && this.battleTextVenusaurAlpha >= 255) {
        ctx.globalAlpha = this.runTextAlpha / 255;
        ctx.fillStyle = 'rgb(255, 255, 255)';
        ctx.font = this.dialogFont;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        const textX = 32;
        const textY = this.battleDialogY + (this.battleDialog.height / 2);
        ctx.fillText("Venusaur can't run away!", textX, textY);
        ctx.globalAlpha = 1.0;
      }
      
      if (this.fullHPTextVisible && this.battleDialog && this.battleTextVenusaurAlpha >= 255) {
        ctx.globalAlpha = this.fullHPTextAlpha / 255;
        ctx.fillStyle = 'rgb(255, 255, 255)';
        ctx.font = this.dialogFont;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        const textX = 32;
        const textY = this.battleDialogY + (this.battleDialog.height / 2);
        ctx.fillText("Your Cursorsaur already has full HP!", textX, textY);
        ctx.globalAlpha = 1.0;
      }

      // Draw bag/pokemon screens on top of everything
      if (this.bagScreenVisible && this.bagScreenImage) {
        ctx.globalAlpha = 0.95;
        ctx.drawImage(this.bagScreenImage, 0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT);
        ctx.globalAlpha = 1.0;
        
        // Draw "USE" button in bag screen (bottom right area)
        // Position: 22px from bottom, 8px from right, 96x21
        const textBoxWidth = 96;
        const textBoxHeight = 21;
        const textBoxX = Config.SCREEN_WIDTH - 8 - textBoxWidth;
        const textBoxY = Config.SCREEN_HEIGHT - 22 - textBoxHeight;
        
        // Draw "USE" text (center aligned, white)
        ctx.fillStyle = 'rgb(255, 255, 255)';
        ctx.font = '19px "Pokemon Pixel Font", Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('USE', textBoxX + textBoxWidth / 2, textBoxY + textBoxHeight / 2);
      } else if (this.pokemonScreenVisible && this.pokemonScreenImage) {
        ctx.globalAlpha = 0.95;
        ctx.drawImage(this.pokemonScreenImage, 0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT);
        ctx.globalAlpha = 1.0;
        
        // Draw "BACK" button in pokemon screen (bottom right area)
        // Position: 22px from bottom, 8px from right, 96x21
        const textBoxWidth = 96;
        const textBoxHeight = 21;
        const textBoxX = Config.SCREEN_WIDTH - 8 - textBoxWidth;
        const textBoxY = Config.SCREEN_HEIGHT - 22 - textBoxHeight;
        
        // Draw "BACK" text (center aligned, white)
        ctx.fillStyle = 'rgb(255, 255, 255)';
        ctx.font = '19px "Pokemon Pixel Font", Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('BACK', textBoxX + textBoxWidth / 2, textBoxY + textBoxHeight / 2);
      }

      // Draw combat UI (shown when Fight is clicked, above battle menu)
      if (this.combatUIVisible && this.combatUI && !this.bagScreenVisible && !this.pokemonScreenVisible) {
        const combatUIX = 0; // Full width at bottom
        const combatUIY = Config.SCREEN_HEIGHT - this.combatUI.height;
        
        ctx.drawImage(this.combatUI, combatUIX, combatUIY);
        
        // Left grid: Draw move labels and hover highlights
        const leftGridX = combatUIX + this.combatUIPadding;
        const leftGridY = combatUIY + this.combatUIPadding;
        
        // Draw hover highlight on left grid
        if (this.combatUIHoveredCell && this.combatUIHoveredCell.gridSide === 'left') {
          const { row, col } = this.combatUIHoveredCell;
          const cellX = leftGridX + (col * this.combatUILeftCellWidth);
          const cellY = leftGridY + (row * this.combatUILeftCellHeight);
          
          ctx.globalAlpha = 128 / 255; // Light blue with transparency
          ctx.fillStyle = 'rgb(173, 216, 230)';
          ctx.fillRect(cellX, cellY, this.combatUILeftCellWidth, this.combatUILeftCellHeight);
          ctx.globalAlpha = 1.0;
        }
        
        // Draw move labels in left grid
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.font = '19px "Pokemon Pixel Font", Arial, sans-serif'; // 80% of 24px base
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        for (let row = 0; row < this.combatUILeftGridRows; row++) {
          for (let col = 0; col < this.combatUILeftGridCols; col++) {
            const moveIndex = row * this.combatUILeftGridCols + col;
            if (moveIndex < this.combatUIMoveLabels.length) {
              const moveName = this.combatUIMoveLabels[moveIndex];
              const cellX = leftGridX + (col * this.combatUILeftCellWidth);
              const cellY = leftGridY + (row * this.combatUILeftCellHeight);
              const cellCenterX = cellX + (this.combatUILeftCellWidth / 2);
              const cellCenterY = cellY + (this.combatUILeftCellHeight / 2);
              
              // Determine text color (grey for first 3 moves, black for Prompt Pulse)
              if (moveName === 'Context Recall' || moveName === 'Syntax Slash' || moveName === 'Debug Dash') {
                ctx.fillStyle = 'rgb(128, 128, 128)'; // Grey
              } else {
                ctx.fillStyle = 'rgb(0, 0, 0)'; // Black
              }
              
              // Draw text with white outline for visibility
              const text = moveName.toUpperCase();
              const textMetrics = ctx.measureText(text);
              const outlineWidth = 2;
              
              // Draw outline
              ctx.strokeStyle = 'rgb(255, 255, 255)';
              ctx.lineWidth = outlineWidth * 2;
              ctx.strokeText(text, cellCenterX, cellCenterY);
              
              // Draw main text
              ctx.fillText(text, cellCenterX, cellCenterY);
            }
          }
        }
        
        // Right grid: Draw move details (updates based on left grid hover)
        // Position in the far right cell grid (right half of combat UI)
        const rightGridX = combatUIX + this.combatUI.width - this.combatUIPadding - this.combatUIRightGridContentWidth;
        const rightGridY = combatUIY + this.combatUIPadding;
        
        // Get selected move from left grid hover
        let selectedMove: string | null = null;
        if (this.combatUIHoveredCell && this.combatUIHoveredCell.gridSide === 'left') {
          const { row, col } = this.combatUIHoveredCell;
          const moveIndex = row * this.combatUILeftGridCols + col;
          if (moveIndex < this.combatUIMoveLabels.length) {
            selectedMove = this.combatUIMoveLabels[moveIndex];
          }
        }
        
        // Draw right grid text
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.textAlign = 'left';
        
        if (selectedMove && selectedMove in this.combatUIMoveDetails) {
          const moveDetails = this.combatUIMoveDetails[selectedMove];
          
          // Helper function to render text with white outline
          const renderTextWithOutline = (text: string, x: number, y: number, alignRight = false) => {
            const outlineWidth = 2;
            const textMetrics = ctx.measureText(text);
            const textHeight = 19; // Font size
            
            // Draw outline (multiple passes)
            ctx.strokeStyle = 'rgb(255, 255, 255)';
            ctx.lineWidth = outlineWidth * 2;
            ctx.strokeText(text, x, y);
            
            // Draw main text
            ctx.fillText(text, x, y);
          };
          
          // Top left cell: "PP" (left aligned, 8px from left, center height)
          const topLeftCellX = rightGridX + 8;
          const topLeftCellY = rightGridY;
          const topLeftCellCenterY = topLeftCellY + (this.combatUIRightCellHeight / 2);
          renderTextWithOutline('PP', topLeftCellX, topLeftCellCenterY);
          
          // Top right cell: "# / #" (right aligned, 8px from right, center height)
          const topRightCellX = rightGridX + (2 * this.combatUIRightCellWidth) - 8;
          const topRightCellY = rightGridY;
          const topRightCellCenterY = topRightCellY + (this.combatUIRightCellHeight / 2);
          const ppText = selectedMove === 'Prompt Pulse' 
            ? `1 / ${moveDetails.pp_max}` 
            : `0 / ${moveDetails.pp_max}`;
          ctx.textAlign = 'right';
          renderTextWithOutline(ppText, topRightCellX, topRightCellCenterY);
          ctx.textAlign = 'left';
          
          // Bottom left cell: "TYPE/" (left aligned, 8px from left, center height)
          const bottomLeftCellX = rightGridX + 8;
          const bottomLeftCellY = rightGridY + this.combatUIRightCellHeight;
          const bottomLeftCellCenterY = bottomLeftCellY + (this.combatUIRightCellHeight / 2);
          renderTextWithOutline('TYPE/', bottomLeftCellX, bottomLeftCellCenterY);
          
          // Bottom right cell: "TYPENAME" (right aligned, 8px from right, center height)
          const bottomRightCellX = rightGridX + (2 * this.combatUIRightCellWidth) - 8;
          const bottomRightCellY = rightGridY + this.combatUIRightCellHeight;
          const bottomRightCellCenterY = bottomRightCellY + (this.combatUIRightCellHeight / 2);
          ctx.textAlign = 'right';
          renderTextWithOutline(moveDetails.type, bottomRightCellX, bottomRightCellCenterY);
          ctx.textAlign = 'left';
        } else {
          // No move selected, show default
          const topLeftCellX = rightGridX + 8;
          const topLeftCellY = rightGridY;
          const topLeftCellCenterY = topLeftCellY + (this.combatUIRightCellHeight / 2);
          const outlineWidth = 2;
          ctx.strokeStyle = 'rgb(255, 255, 255)';
          ctx.lineWidth = outlineWidth * 2;
          ctx.strokeText('PP', topLeftCellX, topLeftCellCenterY);
          ctx.fillText('PP', topLeftCellX, topLeftCellCenterY);
          
          const bottomLeftCellX = rightGridX + 8;
          const bottomLeftCellY = rightGridY + this.combatUIRightCellHeight;
          const bottomLeftCellCenterY = bottomLeftCellY + (this.combatUIRightCellHeight / 2);
          ctx.strokeText('TYPE/', bottomLeftCellX, bottomLeftCellCenterY);
          ctx.fillText('TYPE/', bottomLeftCellX, bottomLeftCellCenterY);
        }
      }

      // Draw battle menu UI (on top, highest z-index, but hide when combat UI is visible)
      // Position: bottom right, directly on top of whatever is there (highest z-index)
      if (this.battleMenuVisible && this.battleMenuUI && !this.bagScreenVisible && !this.pokemonScreenVisible && !this.combatUIVisible) {
        // Position menu touching bottom right corner (no padding, like Python)
        // Should be on top of battle dialog and other elements
        this.battleMenuX = Config.SCREEN_WIDTH - this.battleMenuUI.width;
        this.battleMenuY = Config.SCREEN_HEIGHT - this.battleMenuUI.height;
        
        // Calculate cell dimensions with padding (like Python version)
        const usableWidth = this.battleMenuUI.width - (this.battleMenuPadding * 2);
        const usableHeight = this.battleMenuUI.height - (this.battleMenuPadding * 2);
        this.battleMenuOptionWidth = usableWidth / 2;
        this.battleMenuOptionHeight = usableHeight / 2;
        
        ctx.drawImage(this.battleMenuUI, this.battleMenuX, this.battleMenuY);

        // Draw blue highlight on hovered/selected option (light blue like Python: 173, 216, 230, 128)
        // Priority: selected cell (when text is showing) > hovered cell
        let cellToHighlight: number | null = null;
        if (this.battleMenuSelectedCell !== null) {
          // Check if text is still showing for selected cell
          if (this.battleMenuSelectedCell === 3 && (this.runTextVisible || this.runTextAlpha > 0)) {
            cellToHighlight = this.battleMenuSelectedCell;
          } else if (this.battleMenuSelectedCell === 1 && (this.fullHPTextVisible || this.fullHPTextAlpha > 0)) {
            cellToHighlight = this.battleMenuSelectedCell;
          } else {
            // Text is gone, clear selection
            this.battleMenuSelectedCell = null;
          }
        }
        
        if (cellToHighlight === null) {
          cellToHighlight = this.battleMenuHoveredOption !== null ? this.battleMenuHoveredOption : this.battleMenuCursorPos;
        }
        
        const cellX = this.battleMenuX + this.battleMenuPadding + (cellToHighlight % 2) * this.battleMenuOptionWidth;
        const cellY = this.battleMenuY + this.battleMenuPadding + Math.floor(cellToHighlight / 2) * this.battleMenuOptionHeight;
        
        // Draw light blue highlight rectangle (under text, like Python)
        ctx.globalAlpha = 128 / 255; // 128 alpha like Python
        ctx.fillStyle = 'rgb(173, 216, 230)'; // Light blue like Python version
        ctx.fillRect(cellX, cellY, this.battleMenuOptionWidth, this.battleMenuOptionHeight);
        ctx.globalAlpha = 1.0;

        // Draw cursor indicator (yellow arrow pointing left)
        const cursorSize = 16;
        const cursorX = this.battleMenuX + this.battleMenuPadding + (this.battleMenuCursorPos % 2) * this.battleMenuOptionWidth + this.battleMenuOptionWidth / 2 - cursorSize / 2;
        const cursorY = this.battleMenuY + this.battleMenuPadding + Math.floor(this.battleMenuCursorPos / 2) * this.battleMenuOptionHeight + this.battleMenuOptionHeight / 2 - cursorSize / 2;
        
        ctx.fillStyle = 'rgb(255, 255, 0)';
        ctx.fillRect(cursorX - 12, cursorY, 8, cursorSize);
        
        // Draw text labels for each option in 2x2 grid order: FIGHT, BAG, POKEMON, RUN
        // Grid layout: [0=FIGHT (top-left), 1=BAG (top-right)] [2=POKEMON (bottom-left), 3=RUN (bottom-right)]
        ctx.fillStyle = 'rgb(0, 0, 0)'; // Black text like Python version
        ctx.font = '24px "Pokemon Pixel Font", Arial, sans-serif'; // Match Python font size
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Draw each option text in correct grid position with padding
        for (let i = 0; i < 4; i++) {
          const col = i % 2; // 0 or 1
          const row = Math.floor(i / 2); // 0 or 1
          const cellX = this.battleMenuX + this.battleMenuPadding + (col * this.battleMenuOptionWidth);
          const cellY = this.battleMenuY + this.battleMenuPadding + (row * this.battleMenuOptionHeight);
          const cellCenterX = cellX + (this.battleMenuOptionWidth / 2);
          const cellCenterY = cellY + (this.battleMenuOptionHeight / 2);
          ctx.fillText(this.battleMenuOptions[i], cellCenterX, cellCenterY);
        }
      }
      
      // Draw attack pulse effects (on top of everything)
      if (this.attackPulseVisible && this.attackPulseImage) {
        const centerX = Config.SCREEN_WIDTH / 2;
        const centerY = Config.SCREEN_HEIGHT / 2;
        const pulseWidth = this.attackPulseImage.width * this.attackPulseScale;
        const pulseHeight = this.attackPulseImage.height * this.attackPulseScale;
        const pulseX = centerX - pulseWidth / 2;
        const pulseY = centerY - pulseHeight / 2;
        
        ctx.globalAlpha = this.attackPulseAlpha / 255;
        ctx.drawImage(this.attackPulseImage, pulseX, pulseY, pulseWidth, pulseHeight);
        ctx.globalAlpha = 1.0;
      }
      
      if (this.attackPulseEndVisible && this.attackPulseEndImage) {
        const centerX = Config.SCREEN_WIDTH / 2;
        const centerY = Config.SCREEN_HEIGHT / 2;
        const endX = centerX - this.attackPulseEndImage.width / 2;
        const endY = centerY - this.attackPulseEndImage.height / 2;
        
        ctx.globalAlpha = this.attackPulseEndAlpha / 255;
        ctx.drawImage(this.attackPulseEndImage, endX, endY);
        ctx.globalAlpha = 1.0;
      }

      return;
    }

    // Calculate fade opacity for current scene
    let sceneOpacity = 1.0;
    if (this.fadeState === 'fading') {
      sceneOpacity = Math.max(0, 1.0 - this.fadeAlpha / 255);
    }

    // Draw map
    if (this.mapImage) {
      ctx.globalAlpha = sceneOpacity;
      ctx.drawImage(
        this.mapImage,
        this.cameraX,
        this.cameraY,
        Config.SCREEN_WIDTH,
        Config.SCREEN_HEIGHT,
        0,
        0,
        Config.SCREEN_WIDTH,
        Config.SCREEN_HEIGHT
      );
      ctx.globalAlpha = 1.0;
    }

    // Draw player
    const playerScreenX = this.playerWorldX - this.cameraX;
    const playerScreenY = this.playerWorldY - this.cameraY;

    if (this.characterSprite) {
      const currentSprite = this.characterSprite.getCurrentSprite();
      if (currentSprite) {
        ctx.globalAlpha = sceneOpacity;
        ctx.imageSmoothingEnabled = false; // Disable smoothing for pixel art
        const spriteWidth = currentSprite.width;
        const spriteHeight = currentSprite.height;
        const spriteX = playerScreenX - (spriteWidth - this.playerWidth) / 2;
        // Draw sprite at exact size (no scaling)
        ctx.drawImage(currentSprite, spriteX, playerScreenY, spriteWidth, spriteHeight);
        ctx.imageSmoothingEnabled = true; // Re-enable for other elements
        ctx.globalAlpha = 1.0;
      }
    }

    // Draw exclamation mark popup above player head
    // Show during normal gameplay (not in battle) or when dialog is visible
    if (this.exclamationVisible && this.fadeState !== 'faded' && this.exclamationImage && !this.dialogVisible) {
      const exclamationX = playerScreenX + this.playerWidth / 2 - this.exclamationImage.width / 2;
      const exclamationY = playerScreenY + this.exclamationY - this.exclamationImage.height - 5;
      ctx.globalAlpha = sceneOpacity;
      ctx.drawImage(this.exclamationImage, exclamationX, exclamationY);
      ctx.globalAlpha = 1.0;
    }

    // Draw Lugia
    if (this.lugiaState !== 'hidden' && this.lugiaSprites.length > 0) {
      const lugiaScreenX = this.lugiaX - this.cameraX;
      const lugiaScreenY = this.lugiaY - this.cameraY;

      if (
        lugiaScreenX + 132 > 0 &&
        lugiaScreenX < Config.SCREEN_WIDTH &&
        lugiaScreenY + 132 > 0 &&
        lugiaScreenY < Config.SCREEN_HEIGHT
      ) {
        const frame = Math.min(this.lugiaCurrentFrame, this.lugiaSprites.length - 1);
        ctx.globalAlpha = sceneOpacity;
        ctx.drawImage(this.lugiaSprites[frame], lugiaScreenX, lugiaScreenY);
        ctx.globalAlpha = 1.0;
      }
    }

    // Draw dialog
    if (this.dialogVisible && this.fadeState !== 'faded') {
      if (0 <= this.dialogSlideY && this.dialogSlideY < Config.SCREEN_HEIGHT) {
        if (this.dialogImage) {
          const dialogX = (Config.SCREEN_WIDTH - this.dialogImage.width) / 2;
          ctx.globalAlpha = sceneOpacity;
          ctx.drawImage(this.dialogImage, dialogX, this.dialogSlideY);

          if (this.dialogText) {
            ctx.fillStyle = `rgb(${Config.BLACK.join(',')})`; // Black text
            ctx.font = this.dialogFont;
            ctx.textAlign = 'left';
            ctx.textBaseline = 'top';
            const textX = 48;
            const textY = this.dialogSlideY + (this.dialogImage.height - 32) / 2;
            ctx.fillText(this.dialogText, textX, textY);
          }
          ctx.globalAlpha = 1.0;
        }
      }
    }

    // Draw fade transition
    if (this.fadeState === 'fading' && this.fightingBackground) {
      const bgOpacity = Math.min(255, Math.floor(this.fadeAlpha)) / 255;
      ctx.globalAlpha = bgOpacity;
      ctx.drawImage(this.fightingBackground, 0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT);
      ctx.globalAlpha = 1.0;
    }
  }
}

