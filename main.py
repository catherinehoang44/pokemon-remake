"""
Pokemon-style 2D Pixel Art Game
Main entry point for the game
Supports both desktop and web (browser) deployment
"""

import pygame
import sys
import asyncio
import platform
from config import Config
from scene_manager import SceneManager
from scenes.character_selection import CharacterSelectionScene
from scenes.pokemon_map import PokemonMapScene
from scenes.pokemon_selection import PokemonSelectionScene


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(Config.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize scene manager
        self.scene_manager = SceneManager()
        
        # Register all scenes
        self.scene_manager.register_scene("character_selection", CharacterSelectionScene(self))
        self.scene_manager.register_scene("house_village", PokemonMapScene(self))
        self.scene_manager.register_scene("pokemon_selection", PokemonSelectionScene(self))
        
        # Start directly on the map
        self.scene_manager.change_scene("house_village")
    
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                # Pass events to current scene
                self.scene_manager.handle_event(event)
    
    def update(self):
        """Update game logic"""
        self.scene_manager.update()
    
    def render(self):
        """Render the game"""
        self.screen.fill(Config.BG_COLOR)
        self.scene_manager.render(self.screen)
        pygame.display.flip()
    
    async def run(self):
        """Main game loop (async for web compatibility)"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(Config.FPS)
            await asyncio.sleep(0)  # Yield control for web compatibility


async def main():
    """Main entry point"""
    game = Game()
    await game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    # Always use async mode (works for both web and desktop)
    # Web platform detection happens automatically in pygbag
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()


