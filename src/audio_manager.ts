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
  private currentMusicPath: string | null = null; // Track which music is currently playing
  private soundEffects: Map<string, HTMLAudioElement> = new Map();
  private playingSoundEffects: Map<string, HTMLAudioElement> = new Map(); // Track currently playing sounds
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
      // If the same music is already playing, don't restart it
      if (this.currentMusic && this.currentMusicPath === path && !this.currentMusic.paused) {
        // Same music is already playing, just return it
        return this.currentMusic;
      }

      // Stop current music if playing (different track or paused)
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
      this.currentMusicPath = path;
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
    // If the same music is already playing, don't do anything
    if (this.currentMusic && this.currentMusicPath === path && !this.currentMusic.paused) {
      return;
    }

    this.loadMusic(path, loop).catch((error) => {
      console.warn('Error playing music:', error);
    });
  }

  stopMusic(): void {
    if (this.currentMusic) {
      this.currentMusic.pause();
      this.currentMusic.currentTime = 0;
      // Don't clear currentMusicPath here - we want to track what was playing
    }
  }

  playSoundEffect(name: string): HTMLAudioElement | null {
    if (this.muted) return null;

    // Check if this sound effect is already playing
    const currentlyPlaying = this.playingSoundEffects.get(name);
    if (currentlyPlaying && !currentlyPlaying.paused && !currentlyPlaying.ended) {
      // Sound is already playing, don't play another instance
      return currentlyPlaying;
    }

    const audio = this.soundEffects.get(name);
    if (audio) {
      // Clone and play
      const clone = audio.cloneNode() as HTMLAudioElement;
      clone.volume = this.sfxVolume;
      
      // Track this playing sound
      this.playingSoundEffects.set(name, clone);
      
      // Remove from tracking when it finishes
      clone.addEventListener('ended', () => {
        this.playingSoundEffects.delete(name);
      });
      
      clone.play().catch((error) => {
        console.warn(`Could not play sound effect ${name}:`, error);
        this.playingSoundEffects.delete(name);
      });
      
      return clone;
    }
    
    return null;
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

