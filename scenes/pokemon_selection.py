"""
Pokemon Selection Scene
Recreates the Pokemon selection screen
"""

import pygame
from config import Config


class PokemonSelectionScene:
    def __init__(self, game):
        self.game = game
        self.selected_pokemon = None
        self.pokemon_options = [
            {"name": "Bulbasaur", "type": "Grass", "color": (100, 255, 100), "x": 200, "y": 300},
            {"name": "Charmander", "type": "Fire", "color": (255, 100, 100), "x": 400, "y": 300},
            {"name": "Squirtle", "type": "Water", "color": (100, 100, 255), "x": 600, "y": 300}
        ]
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.cursor_pos = 0  # 0-2 for the three Pokemon
        self.confirmed = False
    
    def on_enter(self):
        """Called when entering Pokemon selection"""
        self.selected_pokemon = None
        self.cursor_pos = 0
        self.confirmed = False
    
    def handle_event(self, event):
        """Handle input for Pokemon selection"""
        if event.type == pygame.KEYDOWN and not self.confirmed:
            if event.key == pygame.K_LEFT and self.cursor_pos > 0:
                self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT and self.cursor_pos < len(self.pokemon_options) - 1:
                self.cursor_pos += 1
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select Pokemon
                self.selected_pokemon = self.pokemon_options[self.cursor_pos]
                self.confirmed = True
    
    def update(self):
        """Update Pokemon selection logic"""
        pass
    
    def render(self, screen):
        """Render Pokemon selection screen"""
        # Title
        title = self.font_large.render("Choose Your Pokemon", True, Config.BLACK)
        title_rect = title.get_rect(center=(Config.SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Draw Pokemon options
        for i, pokemon in enumerate(self.pokemon_options):
            # Pokemon box
            box_rect = pygame.Rect(pokemon["x"] - 60, pokemon["y"] - 80, 120, 120)
            
            # Highlight selected
            if i == self.cursor_pos:
                pygame.draw.rect(screen, Config.WHITE, box_rect, 4)
                if self.confirmed:
                    pygame.draw.rect(screen, Config.GREEN, box_rect, 4)
            
            # Pokemon placeholder (colored circle/rectangle)
            pokemon_rect = pygame.Rect(pokemon["x"] - 40, pokemon["y"] - 40, 80, 80)
            pygame.draw.ellipse(screen, pokemon["color"], pokemon_rect)
            
            # Pokemon name
            name_text = self.font_medium.render(pokemon["name"], True, Config.BLACK)
            name_rect = name_text.get_rect(center=(pokemon["x"], pokemon["y"] + 60))
            screen.blit(name_text, name_rect)
            
            # Pokemon type
            type_text = self.font_small.render(pokemon["type"], True, Config.DARK_GRAY)
            type_rect = type_text.get_rect(center=(pokemon["x"], pokemon["y"] + 85))
            screen.blit(type_text, type_rect)
        
        # Instructions or confirmation message
        if self.confirmed:
            text = self.font_medium.render(
                f"You chose {self.selected_pokemon['name']}!", 
                True, Config.GREEN
            )
        else:
            text = self.font_medium.render(
                "Use Arrow Keys to select, Enter to confirm", 
                True, Config.DARK_GRAY
            )
        text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT - 40))
        screen.blit(text, text_rect)


