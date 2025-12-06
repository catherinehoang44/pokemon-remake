"""
Character Selection Scene
Recreates the character selection screen
"""

import pygame
from config import Config


class CharacterSelectionScene:
    def __init__(self, game):
        self.game = game
        self.selected_character = None
        self.character_options = [
            {"name": "Red", "color": (255, 0, 0), "x": 200, "y": 200},
            {"name": "Blue", "color": (0, 0, 255), "x": 400, "y": 200}
        ]
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.cursor_pos = 0  # 0-1 for the two characters
        self.confirmed = False
    
    def on_enter(self):
        """Called when entering character selection"""
        self.selected_character = None
        self.cursor_pos = 0
        self.confirmed = False
    
    def handle_event(self, event):
        """Handle input for character selection"""
        if event.type == pygame.KEYDOWN and not self.confirmed:
            if event.key == pygame.K_LEFT and self.cursor_pos > 0:
                self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT and self.cursor_pos < len(self.character_options) - 1:
                self.cursor_pos += 1
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select character
                self.selected_character = self.character_options[self.cursor_pos]
                self.confirmed = True
                # Transition to house/village scene
                self.game.scene_manager.change_scene("house_village")
    
    def update(self):
        """Update character selection logic"""
        pass
    
    def render(self, screen):
        """Render character selection screen"""
        # Title
        title = self.font_large.render("Choose Your Character", True, Config.BLACK)
        title_rect = title.get_rect(center=(Config.SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Draw character options
        for i, character in enumerate(self.character_options):
            # Character box
            box_rect = pygame.Rect(character["x"] - 60, character["y"] - 80, 120, 120)
            
            # Highlight selected
            if i == self.cursor_pos:
                pygame.draw.rect(screen, Config.WHITE, box_rect, 4)
                if self.confirmed:
                    pygame.draw.rect(screen, Config.GREEN, box_rect, 4)
            
            # Character placeholder (colored circle/rectangle)
            character_rect = pygame.Rect(character["x"] - 40, character["y"] - 40, 80, 80)
            pygame.draw.ellipse(screen, character["color"], character_rect)
            
            # Character name
            name_text = self.font_medium.render(character["name"], True, Config.BLACK)
            name_rect = name_text.get_rect(center=(character["x"], character["y"] + 60))
            screen.blit(name_text, name_rect)
        
        # Instructions or confirmation message
        if self.confirmed:
            text = self.font_medium.render(
                f"You chose {self.selected_character['name']}!", 
                True, Config.GREEN
            )
        else:
            text = self.font_medium.render(
                "Use Arrow Keys to select, Enter to confirm", 
                True, Config.DARK_GRAY
            )
        text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT - 40))
        screen.blit(text, text_rect)


