"""
Utility functions for sprite animation
"""

import pygame


class SpriteSheet:
    """Handles loading and extracting sprites from a sprite sheet"""
    
    def __init__(self, image_path, sprite_width, sprite_height, expected_width=None, expected_height=None):
        """
        Load sprite sheet
        
        Args:
            image_path: Path to sprite sheet image
            sprite_width: Width of each sprite
            sprite_height: Height of each sprite
            expected_width: Expected total width (optional, for validation)
            expected_height: Expected total height (optional, for validation)
        """
        try:
            self.sheet = pygame.image.load(image_path).convert_alpha()
            sheet_width = self.sheet.get_width()
            sheet_height = self.sheet.get_height()
            
            # Validate dimensions if expected values provided
            if expected_width and sheet_width != expected_width:
                print(f"Warning: Sprite sheet width mismatch. Expected {expected_width}, got {sheet_width}")
                # Auto-resize if needed
                if sheet_width < expected_width or sheet_height < expected_height:
                    new_sheet = pygame.Surface((expected_width, expected_height), pygame.SRCALPHA)
                    new_sheet.blit(self.sheet, (0, 0))
                    self.sheet = new_sheet
                    sheet_width = expected_width
                    sheet_height = expected_height
            
            self.sprite_width = sprite_width
            self.sprite_height = sprite_height
            self.sheet_width = sheet_width
            self.sheet_height = sheet_height
            
            # Calculate grid dimensions
            self.cols = sheet_width // sprite_width
            self.rows = sheet_height // sprite_height
            
        except pygame.error as e:
            print(f"Unable to load sprite sheet: {image_path}")
            print(f"Error: {e}")
            # Create a placeholder magenta sprite
            self.sheet = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            self.sheet.fill((255, 0, 255, 128))
            self.sprite_width = sprite_width
            self.sprite_height = sprite_height
            self.sheet_width = sprite_width
            self.sheet_height = sprite_height
            self.cols = 1
            self.rows = 1
    
    def get_sprite(self, row, col):
        """
        Extract a sprite from the sheet
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
        
        Returns:
            pygame.Surface: The extracted sprite
        """
        x = col * self.sprite_width
        y = row * self.sprite_height
        
        # Check bounds
        if (x + self.sprite_width <= self.sheet_width and 
            y + self.sprite_height <= self.sheet_height and
            x >= 0 and y >= 0):
            try:
                sprite_rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
                sprite = self.sheet.subsurface(sprite_rect)
                return sprite
            except (ValueError, pygame.error) as e:
                print(f"Error extracting sprite at ({row}, {col}): {e}")
                # Return placeholder
                placeholder = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
                placeholder.fill((255, 0, 255, 128))
                return placeholder
        else:
            # Out of bounds - return placeholder
            placeholder = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))
            return placeholder


class AnimatedSprite:
    """Handles sprite animation with different directions and states"""
    
    def __init__(self, sprite_sheet, num_frames=4):
        """
        Initialize animated sprite
        
        Args:
            sprite_sheet: SpriteSheet instance
            num_frames: Number of animation frames per direction
        """
        self.sprite_sheet = sprite_sheet
        self.num_frames = num_frames
        self.current_frame = 0
        self.current_direction = 0  # 0=down, 1=up, 2=right, 3=left
        self.animation_time = 0
        self.animation_speed = 0.15  # Frame change speed
        self.is_moving = False
    
    def update(self, direction, moving):
        """
        Update animation
        
        Args:
            direction: Direction (0=down, 1=up, 2=right, 3=left)
            moving: Whether the sprite is moving
        """
        self.current_direction = direction
        self.is_moving = moving
        
        if moving:
            # Cycle through all 4 frames continuously when moving
            self.animation_time += self.animation_speed
            if self.animation_time >= 1.0:
                self.animation_time = 0
                self.current_frame = (self.current_frame + 1) % self.num_frames
        else:
            # Reset to frame 0 when not moving
            self.current_frame = 0
            self.animation_time = 0
    
    def get_current_sprite(self):
        """Get the current sprite frame"""
        return self.sprite_sheet.get_sprite(self.current_direction, self.current_frame)















