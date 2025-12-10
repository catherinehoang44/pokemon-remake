/**
 * Scene Manager
 * Handles scene transitions and state management
 */

export interface Scene {
  onEnter?(): void;
  onExit?(): void;
  handleEvent?(event: KeyboardEvent | MouseEvent): void;
  update?(deltaTime: number): void;
  render?(ctx: CanvasRenderingContext2D): void;
}

export class SceneManager {
  private scenes: Map<string, Scene> = new Map();
  private currentScene: Scene | null = null;
  private currentSceneName: string | null = null;

  registerScene(name: string, scene: Scene): void {
    this.scenes.set(name, scene);
  }

  changeScene(name: string): void {
    if (this.scenes.has(name)) {
      // Call on_exit on current scene if it exists
      if (this.currentScene?.onExit) {
        this.currentScene.onExit();
      }

      // Switch to new scene
      this.currentSceneName = name;
      this.currentScene = this.scenes.get(name)!;

      // Call on_enter on new scene
      if (this.currentScene?.onEnter) {
        this.currentScene.onEnter();
      }
    } else {
      console.warn(`Warning: Scene '${name}' not found`);
    }
  }

  handleEvent(event: KeyboardEvent | MouseEvent): void {
    if (this.currentScene?.handleEvent) {
      this.currentScene.handleEvent(event);
    }
  }

  update(deltaTime: number): void {
    if (this.currentScene?.update) {
      this.currentScene.update(deltaTime);
    }
  }

  render(ctx: CanvasRenderingContext2D): void {
    if (this.currentScene?.render) {
      this.currentScene.render(ctx);
    }
  }

  getCurrentSceneName(): string | null {
    return this.currentSceneName;
  }
}

