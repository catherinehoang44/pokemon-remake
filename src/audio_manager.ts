/**
 * Audio Manager
 * Handles music and sound effects playback
 */

import { Config } from './config';

export class AudioManager {
  private musicVolume = 0.3;
  private sfxVolume = 0.6;
  private muted = false;
  private currentMusic: HTMLAudioElement | null = null;
  private soundEffects: Map<string, HTMLAudioElement> = new Map();
  private userHasInteracted = false;
  private musicLoaded = false;

  constructor() {
    // Listen for user interaction to enable audio
    const enableAudio = () => {
      this.userHasInteracted = true;
      if (this.currentMusic && this.musicLoaded) {
        this.currentMusic.play().catch((e) => {
          console.warn('Could not play music:', e);
        });
      }
      // Remove listeners after first interaction
      document.removeEventListener('click', enableAudio);
      document.removeEventListener('keydown', enableAudio);
      document.removeEventListener('touchstart', enableAudio);
    };

    document.addEventListener('click', enableAudio, { once: true });
    document.addEventListener('keydown', enableAudio, { once: true });
    document.addEventListener('touchstart', enableAudio, { once: true });
  }

  async loadSoundEffect(name: string, path: string): Promise<void> {
    try {
      const audio = new Audio(path);
      audio.volume = this.sfxVolume;
      audio.preload = 'auto';
      await new Promise((resolve, reject) => {
        audio.oncanplaythrough = resolve;
        audio.onerror = reject;
        audio.load();
      });
      this.soundEffects.set(name, audio);
    } catch (error) {
      console.warn(`Unable to load sound effect ${name}:`, error);
    }
  }

  async loadMusic(path: string, loop: boolean = true): Promise<HTMLAudioElement | null> {
    try {
      // Stop current music if playing
      this.stopMusic();

      const audio = new Audio(path);
      audio.volume = this.musicVolume;
      audio.loop = loop;
      audio.preload = 'auto';
      
      await new Promise((resolve, reject) => {
        audio.oncanplaythrough = resolve;
        audio.onerror = reject;
        audio.load();
      });

      this.currentMusic = audio;
      this.musicLoaded = true;

      // Play if user has already interacted
      if (this.userHasInteracted && !this.muted) {
        await audio.play();
      }

      return audio;
    } catch (error) {
      console.warn('Unable to load music:', error);
      return null;
    }
  }

  playMusic(path: string, loop: boolean = true): void {
    this.loadMusic(path, loop).catch((error) => {
      console.warn('Error playing music:', error);
    });
  }

  stopMusic(): void {
    if (this.currentMusic) {
      this.currentMusic.pause();
      this.currentMusic.currentTime = 0;
    }
  }

  playSoundEffect(name: string): void {
    if (this.muted) return;

    const audio = this.soundEffects.get(name);
    if (audio) {
      // Clone and play to allow overlapping sounds
      const clone = audio.cloneNode() as HTMLAudioElement;
      clone.volume = this.sfxVolume;
      clone.play().catch((error) => {
        console.warn(`Could not play sound effect ${name}:`, error);
      });
    }
  }

  setMusicVolume(volume: number): void {
    this.musicVolume = Math.max(0, Math.min(1, volume));
    if (this.currentMusic) {
      this.currentMusic.volume = this.muted ? 0 : this.musicVolume;
    }
  }

  setSfxVolume(volume: number): void {
    this.sfxVolume = Math.max(0, Math.min(1, volume));
    // Update existing sound effects
    this.soundEffects.forEach((audio) => {
      audio.volume = this.sfxVolume;
    });
  }

  toggleMute(): void {
    this.muted = !this.muted;
    if (this.currentMusic) {
      this.currentMusic.volume = this.muted ? 0 : this.musicVolume;
    }
  }

  isMuted(): boolean {
    return this.muted;
  }

  getMusicVolume(): number {
    return this.musicVolume;
  }

  getSfxVolume(): number {
    return this.sfxVolume;
  }
}

// Singleton instance
export const audioManager = new AudioManager();

