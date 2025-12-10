/**
 * Utility functions for sprite animation
 */

import { Config } from './config';

export class SpriteSheet {
  private image: HTMLImageElement;
  private spriteWidth: number;
  private spriteHeight: number;
  private cols: number;
  private rows: number;

  constructor(
    image: HTMLImageElement,
    spriteWidth: number,
    spriteHeight: number,
    expectedWidth?: number,
    expectedHeight?: number
  ) {
    this.image = image;
    this.spriteWidth = spriteWidth;
    this.spriteHeight = spriteHeight;

    const sheetWidth = image.width;
    const sheetHeight = image.height;

    // Validate dimensions if expected values provided
    if (expectedWidth && sheetWidth !== expectedWidth) {
      console.warn(
        `Warning: Sprite sheet width mismatch. Expected ${expectedWidth}, got ${sheetWidth}`
      );
    }

    // Calculate grid dimensions
    this.cols = Math.floor(sheetWidth / spriteWidth);
    this.rows = Math.floor(sheetHeight / spriteHeight);
  }

  getSprite(row: number, col: number): HTMLImageElement | null {
    const x = col * this.spriteWidth;
    const y = row * this.spriteHeight;

    // Check bounds
    if (
      x + this.spriteWidth <= this.image.width &&
      y + this.spriteHeight <= this.image.height &&
      x >= 0 &&
      y >= 0
    ) {
      // Create a canvas to extract the sprite
      const canvas = document.createElement('canvas');
      canvas.width = this.spriteWidth;
      canvas.height = this.spriteHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;

      ctx.drawImage(
        this.image,
        x,
        y,
        this.spriteWidth,
        this.spriteHeight,
        0,
        0,
        this.spriteWidth,
        this.spriteHeight
      );

      // Convert canvas to image
      const spriteImage = new Image();
      spriteImage.src = canvas.toDataURL();
      return spriteImage;
    }

    return null;
  }

  getSpriteAsCanvas(row: number, col: number): HTMLCanvasElement | null {
    const x = col * this.spriteWidth;
    const y = row * this.spriteHeight;

    // Check bounds
    if (
      x + this.spriteWidth <= this.image.width &&
      y + this.spriteHeight <= this.image.height &&
      x >= 0 &&
      y >= 0
    ) {
      const canvas = document.createElement('canvas');
      canvas.width = this.spriteWidth;
      canvas.height = this.spriteHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;

      ctx.drawImage(
        this.image,
        x,
        y,
        this.spriteWidth,
        this.spriteHeight,
        0,
        0,
        this.spriteWidth,
        this.spriteHeight
      );

      return canvas;
    }

    return null;
  }
}

export class AnimatedSprite {
  private spriteSheet: SpriteSheet;
  private numFrames: number;
  private currentFrame: number = 0;
  private currentDirection: number = 0; // 0=down, 1=up, 2=right, 3=left
  private animationTime: number = 0;
  private animationSpeed: number = 0.15; // Frame change speed
  private isMoving: boolean = false;

  constructor(spriteSheet: SpriteSheet, numFrames: number = 4) {
    this.spriteSheet = spriteSheet;
    this.numFrames = numFrames;
  }

  update(direction: number, moving: boolean, deltaTime: number): void {
    this.currentDirection = direction;
    this.isMoving = moving;

    if (moving) {
      // Cycle through all 4 frames continuously when moving
      this.animationTime += this.animationSpeed * (deltaTime / 16.67); // Normalize to 60fps
      if (this.animationTime >= 1.0) {
        this.animationTime = 0;
        this.currentFrame = (this.currentFrame + 1) % this.numFrames;
      }
    } else {
      // Reset to frame 0 when not moving
      this.currentFrame = 0;
      this.animationTime = 0;
    }
  }

  getCurrentSprite(): HTMLCanvasElement | null {
    return this.spriteSheet.getSpriteAsCanvas(this.currentDirection, this.currentFrame);
  }
}

export async function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

export async function loadAudio(src: string): Promise<HTMLAudioElement> {
  return new Promise((resolve, reject) => {
    const audio = new Audio(src);
    audio.oncanplaythrough = () => resolve(audio);
    audio.onerror = reject;
    audio.load();
  });
}

export function loadGifFrames(src: string): Promise<HTMLImageElement[]> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      // For GIFs, we'll need to extract frames
      // This is a simplified version - for full GIF support, consider using a library
      // For now, we'll just return the image as a single frame
      resolve([img]);
    };
    img.onerror = reject;
    img.src = src;
  });
}

