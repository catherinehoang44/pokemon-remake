import { useEffect, useRef } from 'react';
import { SceneManager } from './scene_manager';
import { CharacterSelectionScene } from './scenes/CharacterSelectionScene';
import { PokemonSelectionScene } from './scenes/PokemonSelectionScene';
import { HouseVillageScene } from './scenes/HouseVillageScene';
import { Config } from './config';

function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sceneManagerRef = useRef<SceneManager | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = Config.SCREEN_WIDTH;
    canvas.height = Config.SCREEN_HEIGHT;
    canvas.style.width = `${Config.SCREEN_WIDTH * 2}px`;
    canvas.style.height = `${Config.SCREEN_HEIGHT * 2}px`;
    canvas.style.imageRendering = 'pixelated';

    // Initialize scene manager
    const sceneManager = new SceneManager();

    // Create scenes
    const houseVillageScene = new HouseVillageScene((sceneName) => {
      sceneManager.changeScene(sceneName);
    });

    const characterSelectionScene = new CharacterSelectionScene((sceneName) => {
      sceneManager.changeScene(sceneName);
    });

    const pokemonSelectionScene = new PokemonSelectionScene();

    // Register scenes
    sceneManager.registerScene('character_selection', characterSelectionScene);
    sceneManager.registerScene('house_village', houseVillageScene);
    sceneManager.registerScene('pokemon_selection', pokemonSelectionScene);

    // Start with house_village scene
    sceneManager.changeScene('house_village');

    sceneManagerRef.current = sceneManager;

    // Event handlers
    const handleKeyDown = (e: KeyboardEvent) => {
      sceneManager.handleEvent(e);
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      sceneManager.handleEvent(e);
    };

    const handleMouseDown = (e: MouseEvent) => {
      sceneManager.handleEvent(e);
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    window.addEventListener('mousedown', handleMouseDown);

    // Game loop
    const gameLoop = (currentTime: number) => {
      const deltaTime = currentTime - lastTimeRef.current;
      lastTimeRef.current = currentTime;

      // Clear canvas
      ctx.fillStyle = `rgb(${Config.BG_COLOR.join(',')})`;
      ctx.fillRect(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT);

      // Update and render
      if (sceneManagerRef.current) {
        sceneManagerRef.current.update(deltaTime);
        sceneManagerRef.current.render(ctx);
      }

      animationFrameRef.current = requestAnimationFrame(gameLoop);
    };

    lastTimeRef.current = performance.now();
    animationFrameRef.current = requestAnimationFrame(gameLoop);

    // Cleanup
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      window.removeEventListener('mousedown', handleMouseDown);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#000',
      }}
    >
      <canvas ref={canvasRef} />
    </div>
  );
}

export default App;

