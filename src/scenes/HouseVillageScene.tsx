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
  private playerHeight = 64;
  private characterSprite: AnimatedSprite | null = null;

  // Movement state
  private movingUp = false;
  private movingDown = false;
  private movingLeft = false;
  private movingRight = false;
  private currentDirection = 0; // 0=down, 1=up, 2=right, 3=left

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
  private battleLugiaFrames: HTMLImageElement[] = [];
  private battleLugiaCurrentFrame = 0;
  private battleLugiaAnimationTime = 0;
  private battleLugiaX = 0;
  private battleLugiaY = 0;
  private battleLugiaTargetX = 0;
  private battleLugiaVisible = false;
  private battleVenuFrames: HTMLImageElement[] = [];
  private battleVenuCurrentFrame = 0;
  private battleVenuAnimationTime = 0;
  private battleVenuX = 0;
  private battleVenuY = 0;
  private battleVenuTargetY = 0;
  private battleVenuVisible = false;
  private battleVenuStat: HTMLImageElement | null = null;
  private battleVenuStatX = 0;
  private battleVenuStatY = 0;
  private battleVenuStatVisible = true;

  // Battle text
  private battleTextState: 'lugia' | 'venusaur' | 'transitioning' = 'lugia';
  private battleTextLugiaAlpha = 255;
  private battleTextVenusaurAlpha = 0;
  private battleTextFading = false;

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
      // Load Pokemon pixel font
      const fontFace = new FontFace(
        'Pokemon Pixel Font',
        `url(${Config.FONTS_PATH}/pokemon_pixel_font.ttf)`
      );
      try {
        await fontFace.load();
        document.fonts.add(fontFace);
        this.fontLoaded = true;
      } catch (error) {
        console.warn('Unable to load Pokemon pixel font, using fallback:', error);
        this.dialogFont = '32px Arial, sans-serif';
      }

      // Load map
      this.mapImage = await loadImage(`${Config.IMAGES_PATH}/map_background.png`);
      this.mapWidth = this.mapImage.width;
      this.mapHeight = this.mapImage.height;

      // Load character sprite
      const characterImg = await loadImage(`${Config.SPRITES_PATH}/character_red.png`);
      const characterSheet = new SpriteSheet(characterImg, 32, 64, 128, 256);
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

      // Load fighting background
      this.fightingBackground = await loadImage(`${Config.IMAGES_PATH}/fighting_background.png`);

      // Load battle UI
      this.battleDialog = await loadImage(`${Config.IMAGES_PATH}/battle_dialog.png`);
      this.battleGrass = await loadImage(`${Config.IMAGES_PATH}/battle_grass.png`);
      this.battlePokemonstat = await loadImage(`${Config.IMAGES_PATH}/battle_lugia_stat.png`);
      this.battleWater = await loadImage(`${Config.IMAGES_PATH}/battle_water.png`);
      this.battleVenuStat = await loadImage(`${Config.IMAGES_PATH}/battle_venu_stat.png`);

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

      // Load battle Lugia GIF (simplified - browsers can display animated GIFs)
      const battleLugiaImg = await loadImage(`${Config.SPRITES_PATH}/battle_lugia.gif`);
      this.battleLugiaFrames.push(battleLugiaImg);
      // Note: For frame-by-frame GIF extraction, consider using a library like 'gif.js' or 'omggif'

      // Load battle Venusaur GIF
      const battleVenuImg = await loadImage(`${Config.SPRITES_PATH}/battle_venu.gif`);
      this.battleVenuFrames.push(battleVenuImg);

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
    if (this.battleLugiaFrames.length > 0 && this.battleWater) {
      this.battleLugiaX = Config.SCREEN_WIDTH;
      const waterCenterX = this.battleWaterTargetX + this.battleWater.width / 2;
      this.battleLugiaTargetX = waterCenterX - this.battleLugiaFrames[0].width / 2;
      this.battleLugiaY = this.battleWaterY + this.battleWater.height - this.battleLugiaFrames[0].height;
    }

    // Battle Venusaur
    if (this.battleVenuFrames.length > 0) {
      this.battleVenuY = Config.SCREEN_HEIGHT;
      if (this.battleDialog) {
        this.battleVenuTargetY = Config.SCREEN_HEIGHT - this.battleDialog.height - this.battleVenuFrames[0].height;
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
          // Restart map music
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
    } else if (event instanceof MouseEvent && event.type === 'mousedown') {
      // Mark user interaction
      if (!this.userHasInteracted) {
        this.userHasInteracted = true;
        if (this.mapMusicLoaded && !this.battleMusicStarted) {
          audioManager.playMusic(`${Config.SOUNDS_PATH}/mtmoon.wav`, true);
        }
      }

      if (this.lugiaAnimationComplete && this.dialogFullyVisible && this.fadeState !== 'faded') {
        if (this.fightingBackground) {
          this.fadeState = 'fading';
          this.fadeAlpha = 0;
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
            this.dialogVisible = true;
            this.dialogFullyVisible = false;
            this.dialogSlideY = Config.SCREEN_HEIGHT;
            this.dialogText = 'Lugia wants to battle!';
          }
        }
      }
    } else if (this.lugiaState === 'stopped') {
      if (this.lugiaSprites.length > 0) {
        this.lugiaCurrentFrame = this.lugiaSprites.length - 1;
      }
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
        }
      } else {
        this.dialogFullyVisible = true;
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
          this.battleGrassVisible = true;
          this.battlePokemonstatVisible = true;
          this.battleWaterVisible = true;
          this.battleLugiaVisible = true;
          this.battleTrainerVisible = true;
          if (this.battleVenuStat) {
            this.battleVenuStatVisible = true;
          }

          // Start battle music
          if (!this.battleMusicStarted) {
            audioManager.playMusic(`${Config.SOUNDS_PATH}/battle.wav`, true);
            this.battleMusicStarted = true;
          }
        }
      }
    }

    // Update battle UI animations
    if (this.fadeState === 'fading') {
      if (this.battleDialogVisible && this.battleDialog) {
        this.battleDialogAlpha = Math.min(255, Math.floor(this.fadeAlpha));
      }
    }

    if (this.fadeState === 'faded') {
      if (this.battleDialogVisible && this.battleDialog) {
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
      if (this.battleLugiaVisible && this.battleLugiaFrames.length > 0) {
        if (this.battleLugiaX > this.battleLugiaTargetX) {
          this.battleLugiaX -= this.battleWaterSpeed;
          if (this.battleLugiaX <= this.battleLugiaTargetX) {
            this.battleLugiaX = this.battleLugiaTargetX;
          }
        }

        if (this.battleLugiaFrames.length > 1) {
          this.battleLugiaAnimationTime += this.battleLugiaAnimationSpeed * (deltaTime / 16.67);
          if (this.battleLugiaAnimationTime >= 1.0) {
            this.battleLugiaAnimationTime = 0;
            this.battleLugiaCurrentFrame = (this.battleLugiaCurrentFrame + 1) % this.battleLugiaFrames.length;
          }
        }
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

        if (allAnimationsComplete) {
          this.battleTrainerCanAnimate = true;
        }

        if (this.battleTrainerCanAnimate && this.battleTrainerX === this.battleTrainerTargetX && !this.battleTrainerSlideOut) {
          this.battleTrainerAnimationTime += this.battleTrainerAnimationSpeed * (deltaTime / 16.67);
          if (this.battleTrainerAnimationTime >= 1.0) {
            this.battleTrainerAnimationTime = 0;
            if (this.battleTrainerCurrentFrame < this.battleTrainerSprites.length - 1) {
              this.battleTrainerCurrentFrame += 1;
            } else {
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
      if (this.battleVenuVisible && this.battleVenuFrames.length > 0) {
        if (this.battleVenuY > this.battleVenuTargetY) {
          this.battleVenuY -= this.battleTrainerSpeed;
          if (this.battleVenuY <= this.battleVenuTargetY) {
            this.battleVenuY = this.battleVenuTargetY;
          }
        }

        if (this.battleVenuFrames.length > 1) {
          this.battleVenuAnimationTime += this.battleVenuAnimationSpeed * (deltaTime / 16.67);
          if (this.battleVenuAnimationTime >= 1.0) {
            this.battleVenuAnimationTime = 0;
            this.battleVenuCurrentFrame = (this.battleVenuCurrentFrame + 1) % this.battleVenuFrames.length;
          }
        }
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
        ctx.globalAlpha = this.battleTrainerAlpha / 255;
        ctx.drawImage(trainerSprite, this.battleTrainerX, this.battleTrainerY);
        ctx.globalAlpha = 1.0;
      }

      if (this.battleWaterVisible && this.battleWater) {
        ctx.drawImage(this.battleWater, this.battleWaterX, this.battleWaterY);
      }

      if (this.battleLugiaVisible && this.battleLugiaFrames.length > 0) {
        const frame = Math.min(this.battleLugiaCurrentFrame, this.battleLugiaFrames.length - 1);
        const lugiaImg = this.battleLugiaFrames[frame];
        // Draw at original size (no scaling)
        ctx.drawImage(lugiaImg, this.battleLugiaX, this.battleLugiaY, lugiaImg.width, lugiaImg.height);
      }

      if (this.battlePokemonstatVisible && this.battlePokemonstat) {
        ctx.drawImage(this.battlePokemonstat, this.battlePokemonstatX, this.battlePokemonstatY);
      }

      if (this.battleVenuVisible && this.battleVenuFrames.length > 0) {
        const frame = Math.min(this.battleVenuCurrentFrame, this.battleVenuFrames.length - 1);
        const venuImg = this.battleVenuFrames[frame];
        // Draw at original size (no scaling)
        ctx.drawImage(venuImg, this.battleVenuX, this.battleVenuY, venuImg.width, venuImg.height);
      }

      if (this.battleVenuStatVisible && this.battleVenuStat) {
        ctx.drawImage(this.battleVenuStat, this.battleVenuStatX, this.battleVenuStatY);
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
        const spriteWidth = currentSprite.width;
        const spriteX = playerScreenX - (spriteWidth - this.playerWidth) / 2;
        ctx.drawImage(currentSprite, spriteX, playerScreenY);
        ctx.globalAlpha = 1.0;
      }
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

