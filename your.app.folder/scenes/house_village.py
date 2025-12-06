"""
House/Village Scene
Map exploration with scrolling camera, character movement, Lugia sequence, and dialog
"""

import pygame
import os
from scenes.base_scene import BaseScene
from config import Config
from utils import SpriteSheet, AnimatedSprite

try:
    from PIL import Image, ImageSequence
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available. GIF animations will not work. Install with: pip install Pillow")


class HouseVillageScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        
        # ============================================================================
        # WALKABLE AREAS CONFIGURATION
        # Easy to add/remove walkable areas here
        # Format: (min_x, min_y, max_x, max_y) for rectangles, or (x, y) for single cells
        # ============================================================================
        # Rectangles (inclusive boundaries): [(min_x, min_y, max_x, max_y), ...]
        self.walkable_rectangles = [
            (15, 4, 16, 7),   # Rectangle from 15,4 to 16,7
            (14, 8, 16, 12),  # Rectangle from 14,8 to 16,12
        ]
        
        # Individual cells: [(x, y), ...]
        self.walkable_cells = [
            (17, 8),
            (17, 9),
            (18, 9),
        ]
        # ============================================================================
        
        # ============================================================================
        # SPEED ADJUSTMENTS CONFIGURATION
        # Easy to adjust all animation and movement speeds here
        # ============================================================================
        # Lugia sequence speeds
        self.lugia_animation_speed = 0.1  # Animation speed for Lugia sprite
        self.lugia_fly_speed = 2  # Speed at which Lugia flies in
        
        # Dialog speeds
        self.dialog_slide_speed = 8  # Speed at which dialog slides up/down
        
        # Fade speeds
        self.fade_speed = 20  # Speed of fade transition to battle background
        self.battle_text_fade_speed = 5  # Speed of text fade transition (lower = slower)
        
        # Battle animation speeds
        self.battle_slide_speed_base = 5  # Base speed for battle UI slide animations
        self.battle_trainer_animation_speed = 0.2  # Speed of trainer sprite animation
        self.battle_lugia_animation_speed = 0.1  # Frame change speed for Lugia GIF
        self.battle_venu_animation_speed = 0.1  # Frame change speed for Venusaur GIF
        # ============================================================================
        
        # Load map image - use original size from image file
        map_path = os.path.join(Config.IMAGES_PATH, "map_background.png")
        try:
            self.map_image = pygame.image.load(map_path).convert()
            # Use actual image dimensions (original size)
            self.map_width = self.map_image.get_width()
            self.map_height = self.map_image.get_height()
        except pygame.error as e:
            print(f"Unable to load map image: {map_path}")
            print(f"Error: {e}")
            # Create placeholder map with default size
            self.map_image = pygame.Surface((768, 512))
            self.map_image.fill((100, 150, 100))
            self.map_width = 768
            self.map_height = 512
        
        # Initialize player position to a walkable area (cell 15,6 - center of first rectangle)
        grid_size = 32
        self.player_world_x = 15 * grid_size + grid_size // 2  # Center of cell 15
        self.player_world_y = 6 * grid_size + grid_size // 2   # Center of cell 6
        
        # Camera position (top-left corner of visible area)
        self.camera_x = 0
        self.camera_y = 0
        
        # Player dimensions
        self.player_width = 32
        self.player_height = 64
        
        # Load character sprite
        character_path = os.path.join(Config.SPRITES_PATH, "character_red.png")
        try:
            character_sheet = SpriteSheet(character_path, 32, 64, 128, 256)
            self.character_sprite = AnimatedSprite(character_sheet, num_frames=4)
        except Exception as e:
            print(f"Error loading character sprite: {e}")
            self.character_sprite = None
        
        # Movement state
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.current_direction = 0  # 0=down, 1=up, 2=right, 3=left
        
        # Plants removed - no longer needed
        self.plants = []
        
        # Load Lugia sprite and set up animation
        self.lugia_sprites = self.load_lugia()
        self.lugia_current_frame = 0
        self.lugia_animation_time = 0
        # Speed set in SPEED ADJUSTMENTS section above
        # Lugia state: "hidden", "flying_in", "animating", "stopped"
        self.lugia_state = "hidden"
        
        # ===== LUGIA POSITION ADJUSTMENT (Grid-based) =====
        # Adjust Lugia's position using 32x32 grid cells
        # Cell (x, y) means Lugia's top-left corner is placed at that grid cell
        # Example: cell (4, 4) means Lugia's top-left is at cell position (4, 4)
        # To place Lugia at cell (4, 4), set: lugia_target_cell_x = 4, lugia_target_cell_y = 4
        
        # Lugia target position in grid cells (edit these values)
        lugia_target_cell_x = (self.map_width // 32) // 2 - 3  # 3 cells left from center (moved 1 more left)
        lugia_target_cell_y = (self.map_height // 32) // 4 - 5  # Example: 4 for cell row 4
        
        # Convert grid cells to pixel position using reusable function
        # You can use this same pattern for any sprite:
        #   tree_cell_x, tree_cell_y = 8, 2  # Tree at cell (8, 2)
        #   tree_pixel_x, tree_pixel_y = self.cell_to_pixel(tree_cell_x, tree_cell_y)
        lugia_pixel_x, lugia_pixel_y = self.cell_to_pixel(lugia_target_cell_x, lugia_target_cell_y)
        # Move Lugia half a cell over (16 pixels to the right)
        self.lugia_target_x = lugia_pixel_x + 16  # Half a cell (32/2 = 16px)
        self.lugia_target_y = lugia_pixel_y
        
        # Start position (off-screen above)
        self.lugia_x = self.lugia_target_x
        self.lugia_y = -200  # Off-screen above
        # Speed set in SPEED ADJUSTMENTS section above
        self.lugia_animation_complete = False
        
        # Load dialog image
        dialog_path = os.path.join(Config.IMAGES_PATH, "dialog.png")
        try:
            self.dialog_image = pygame.image.load(dialog_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load dialog image: {dialog_path}")
            print(f"Error: {e}")
            self.dialog_image = None
        
        # Dialog text box settings
        self.dialog_visible = False  # Start hidden, show when animation completes
        self.dialog_slide_y = Config.SCREEN_HEIGHT  # Start off-screen below
        # Speed set in SPEED ADJUSTMENTS section above
        self.dialog_fully_visible = False
        self.dialog_text = ""  # Dialog text to display
        
        # Text fade animation for battle dialog text transition
        self.battle_text_state = "lugia"  # "lugia" or "venusaur"
        self.battle_text_lugia_alpha = 255  # Alpha for Lugia text
        self.battle_text_venusaur_alpha = 0  # Alpha for Venusaur text
        # Speed set in SPEED ADJUSTMENTS section above
        self.battle_text_fading = False  # Whether text is currently fading
        
        # Load Pokemon pixel font
        font_path = os.path.join(Config.FONTS_PATH, "pokemon_pixel_font.ttf")
        try:
            self.dialog_font = pygame.font.Font(font_path, 32)
        except:
            print(f"Unable to load Pokemon pixel font: {font_path}")
            print("Using default font...")
            self.dialog_font = pygame.font.Font(None, 32)
        
        # Load fighting background for fade transition
        fighting_bg_path = os.path.join(Config.IMAGES_PATH, "fighting_background.png")
        try:
            self.fighting_background = pygame.image.load(fighting_bg_path).convert()
        except pygame.error as e:
            print(f"Unable to load fighting background: {fighting_bg_path}")
            print(f"Error: {e}")
            self.fighting_background = None
        
        # Fade transition state
        self.fade_state = "none"  # "none", "fading", "faded"
        self.fade_alpha = 0
        # Speed set in SPEED ADJUSTMENTS section above
        self.fade_complete = False  # Track when fade is done
        
        # Pause timer before battle fade (2 seconds after dialog appears)
        self.dialog_pause_timer = 0  # Timer in milliseconds
        self.dialog_pause_duration = 2000  # 2 seconds = 2000 milliseconds
        
        # Battle UI elements - fly in animations
        self.battle_animations_started = False
        
        # Load battle dialog (fly in from right, center bottom)
        battle_dialog_path = os.path.join(Config.IMAGES_PATH, "battle_dialog.png")
        try:
            self.battle_dialog = pygame.image.load(battle_dialog_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load battle dialog: {battle_dialog_path}")
            self.battle_dialog = None
        
        # Load battle grass (fly in from right, left and right above dialog)
        battle_grass_path = os.path.join(Config.IMAGES_PATH, "battle_grass.png")
        try:
            self.battle_grass = pygame.image.load(battle_grass_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load battle grass: {battle_grass_path}")
            self.battle_grass = None
        
        # Load battle lugia stat (fly in from left, top left)
        battle_pokemonstat_path = os.path.join(Config.IMAGES_PATH, "battle_lugia_stat.png")
        try:
            self.battle_pokemonstat = pygame.image.load(battle_pokemonstat_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load battle pokemonstat: {battle_pokemonstat_path}")
            self.battle_pokemonstat = None
        
        # Load battle water (fly in from left, top right)
        battle_water_path = os.path.join(Config.IMAGES_PATH, "battle_water.png")
        try:
            self.battle_water = pygame.image.load(battle_water_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load battle water: {battle_water_path}")
            self.battle_water = None
        
        # Battle animation states
        # Calculate speeds so all animations end at the same time
        # We'll calculate these after positions are set
        # Speed set in SPEED ADJUSTMENTS section above
        
        # Battle dialog (fade in at center bottom, same time as fighting background)
        if self.battle_dialog:
            self.battle_dialog_x = (Config.SCREEN_WIDTH - self.battle_dialog.get_width()) // 2  # Center horizontally
            self.battle_dialog_y = Config.SCREEN_HEIGHT - self.battle_dialog.get_height()  # Bottom of screen
            self.battle_dialog_alpha = 0  # Start transparent for fade in
            self.battle_dialog_visible = False
        else:
            self.battle_dialog_x = 0
            self.battle_dialog_y = 0
            self.battle_dialog_alpha = 0
            self.battle_dialog_visible = False
        
        # Load battle trainer sprite sheet (180x128px per sprite)
        battle_trainer_path = os.path.join(Config.SPRITES_PATH, "battle_trainer.png")
        try:
            trainer_sheet = pygame.image.load(battle_trainer_path).convert_alpha()
            sheet_width = trainer_sheet.get_width()
            sheet_height = trainer_sheet.get_height()
            
            # Extract trainer sprites (all in a row, each 180x128px)
            sprite_width = 180
            sprite_height = 128
            num_trainer_frames = sheet_width // sprite_width
            self.battle_trainer_sprites = []
            for i in range(num_trainer_frames):
                x = i * sprite_width
                if x + sprite_width <= sheet_width:
                    try:
                        sprite_rect = pygame.Rect(x, 0, sprite_width, sprite_height)
                        sprite = trainer_sheet.subsurface(sprite_rect)
                        self.battle_trainer_sprites.append(sprite)
                    except (ValueError, pygame.error) as e:
                        print(f"Error extracting trainer frame {i}: {e}")
        except pygame.error as e:
            print(f"Unable to load battle trainer sprite: {battle_trainer_path}")
            print(f"Error: {e}")
            self.battle_trainer_sprites = []
        
        # Battle grass (fly in from left, left side only above dialog)
        if self.battle_grass:
            self.battle_grass_left_x = -self.battle_grass.get_width()  # Start off-screen left
            # Position above dialog
            if self.battle_dialog:
                grass_y = Config.SCREEN_HEIGHT - self.battle_dialog.get_height() - self.battle_grass.get_height()
            else:
                grass_y = Config.SCREEN_HEIGHT - 100
            self.battle_grass_y = grass_y
            # Left grass target: left side
            self.battle_grass_left_target_x = 0
            self.battle_grass_visible = False
        else:
            self.battle_grass_left_x = 0
            self.battle_grass_y = 0
            self.battle_grass_left_target_x = 0
            self.battle_grass_visible = False
        
        # Battle trainer animation state
        if self.battle_trainer_sprites:
            self.battle_trainer_x = Config.SCREEN_WIDTH  # Start off-screen right
            # Position directly above dialog box (same X as grass, but higher z-index)
            # Trainer will be in same location as grass but rendered on top
            if self.battle_dialog:
                trainer_y = Config.SCREEN_HEIGHT - self.battle_dialog.get_height() - 128  # Directly above dialog
            else:
                trainer_y = Config.SCREEN_HEIGHT - 200
            self.battle_trainer_y = trainer_y
            self.battle_trainer_target_x = 0  # Left side, same position as grass
            self.battle_trainer_current_frame = 0
            self.battle_trainer_animation_time = 0
            # Speed set in SPEED ADJUSTMENTS section above
            self.battle_trainer_visible = False
            self.battle_trainer_can_animate = False  # Don't animate until everything has animated in
            self.battle_trainer_slide_out = False  # Track if trainer should slide out
            self.battle_trainer_alpha = 255  # Fade alpha for slide out
        else:
            self.battle_trainer_x = 0
            self.battle_trainer_y = 0
            self.battle_trainer_target_x = 0
            self.battle_trainer_current_frame = 0
            self.battle_trainer_animation_time = 0
            # Speed set in SPEED ADJUSTMENTS section above
            self.battle_trainer_visible = False
            self.battle_trainer_can_animate = False
            self.battle_trainer_sprites = []
        
        # Battle pokemonstat (fly in from left, top left)
        if self.battle_pokemonstat:
            self.battle_pokemonstat_x = -self.battle_pokemonstat.get_width()  # Start off-screen left
            self.battle_pokemonstat_target_x = 0  # Top left
            self.battle_pokemonstat_y = 0  # Top of screen
            self.battle_pokemonstat_visible = False
        else:
            self.battle_pokemonstat_x = 0
            self.battle_pokemonstat_target_x = 0
            self.battle_pokemonstat_y = 0
            self.battle_pokemonstat_visible = False
        
        # Battle water (fly in from right, under pokemonstat, still on the right)
        if self.battle_water:
            self.battle_water_x = Config.SCREEN_WIDTH  # Start off-screen right
            self.battle_water_target_x = Config.SCREEN_WIDTH - self.battle_water.get_width()  # Right side
            # Position under pokemonstat (if pokemonstat exists, place below it)
            if self.battle_pokemonstat:
                self.battle_water_y = self.battle_pokemonstat.get_height()  # Below pokemonstat
            else:
                self.battle_water_y = 0  # Top of screen if no pokemonstat
            self.battle_water_visible = False
        else:
            self.battle_water_x = 0
            self.battle_water_target_x = 0
            self.battle_water_y = 0
            self.battle_water_visible = False
        
        # Load battle Lugia GIF (slides in with water, on top of water)
        battle_lugia_path = os.path.join(Config.SPRITES_PATH, "battle_lugia.gif")
        self.battle_lugia_frames = []
        self.battle_lugia_current_frame = 0
        self.battle_lugia_animation_time = 0
        # Speed set in SPEED ADJUSTMENTS section above
        try:
            if PIL_AVAILABLE:
                # Extract frames from animated GIF
                pil_image = Image.open(battle_lugia_path)
                for frame in ImageSequence.Iterator(pil_image):
                    # Convert PIL image to pygame surface
                    if frame.mode == 'RGBA':
                        frame_surface = pygame.image.frombytes(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                    else:
                        frame_surface = pygame.image.frombytes(frame.convert('RGBA').tobytes(), frame.size, 'RGBA').convert_alpha()
                    self.battle_lugia_frames.append(frame_surface)
                if self.battle_lugia_frames:
                    self.battle_lugia = self.battle_lugia_frames[0]  # Use first frame as default
                else:
                    self.battle_lugia = None
            else:
                # Fallback: load as static image
                self.battle_lugia = pygame.image.load(battle_lugia_path).convert_alpha()
                self.battle_lugia_frames = [self.battle_lugia]
        except Exception as e:
            print(f"Unable to load battle Lugia: {battle_lugia_path}")
            print(f"Error: {e}")
            self.battle_lugia = None
            self.battle_lugia_frames = []
        
        # Battle Lugia animation state (slides in with water, on top of water)
        if self.battle_lugia and self.battle_water:
            # Position directly on top of water (same x/y, centered horizontally)
            self.battle_lugia_x = Config.SCREEN_WIDTH  # Start off-screen right (same as water)
            # Center Lugia horizontally on water
            water_center_x = self.battle_water_target_x + (self.battle_water.get_width() // 2)
            self.battle_lugia_target_x = water_center_x - (self.battle_lugia.get_width() // 2)  # Centered on water
            # Bottom of Lugia touches bottom of water
            self.battle_lugia_y = self.battle_water_y + self.battle_water.get_height() - self.battle_lugia.get_height()
            self.battle_lugia_visible = False
        else:
            self.battle_lugia_x = 0
            self.battle_lugia_target_x = 0
            self.battle_lugia_y = 0
            self.battle_lugia_visible = False
        
        # Load battle venusaur GIF (slides in from under dialog box)
        battle_venu_path = os.path.join(Config.SPRITES_PATH, "battle_venu.gif")
        self.battle_venu_frames = []
        self.battle_venu_current_frame = 0
        self.battle_venu_animation_time = 0
        # Speed set in SPEED ADJUSTMENTS section above
        try:
            if PIL_AVAILABLE:
                # Extract frames from animated GIF
                pil_image = Image.open(battle_venu_path)
                for frame in ImageSequence.Iterator(pil_image):
                    # Convert PIL image to pygame surface
                    if frame.mode == 'RGBA':
                        frame_surface = pygame.image.frombytes(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                    else:
                        frame_surface = pygame.image.frombytes(frame.convert('RGBA').tobytes(), frame.size, 'RGBA').convert_alpha()
                    self.battle_venu_frames.append(frame_surface)
                if self.battle_venu_frames:
                    self.battle_venu = self.battle_venu_frames[0]  # Use first frame as default
                else:
                    self.battle_venu = None
            else:
                # Fallback: load as static image
                self.battle_venu = pygame.image.load(battle_venu_path).convert_alpha()
                self.battle_venu_frames = [self.battle_venu]
        except Exception as e:
            print(f"Unable to load battle Venusaur GIF: {battle_venu_path}")
            print(f"Error: {e}")
            self.battle_venu = None
            self.battle_venu_frames = []
        
        # Load battle venusaur stat PNG (separate image file)
        battle_venu_stat_path = os.path.join(Config.IMAGES_PATH, "battle_venu_stat.png")
        try:
            self.battle_venu_stat = pygame.image.load(battle_venu_stat_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load battle venusaur stat: {battle_venu_stat_path}")
            print(f"Error: {e}")
            self.battle_venu_stat = None
        
        # Battle venusaur GIF animation state (slides in from under dialog box)
        if self.battle_venu:
            # Start under dialog box (below screen)
            if self.battle_dialog:
                self.battle_venu_y = Config.SCREEN_HEIGHT  # Start off-screen below
                self.battle_venu_target_y = Config.SCREEN_HEIGHT - self.battle_dialog.get_height() - self.battle_venu.get_height()  # Above dialog
            else:
                self.battle_venu_y = Config.SCREEN_HEIGHT
                self.battle_venu_target_y = Config.SCREEN_HEIGHT - 200
            # Position above battle dialog, touching the very left of the screen (furthest left)
            self.battle_venu_x = 0  # Furthest left
            self.battle_venu_visible = False
        else:
            self.battle_venu_x = 0
            self.battle_venu_y = 0
            self.battle_venu_target_y = 0
            self.battle_venu_visible = False
        
        # Battle venusaur stat PNG (separate image, not animated, stays in place)
        if self.battle_venu_stat:
            # Position above battle dialog, touching the very right of the screen (stays in place, no sliding)
            self.battle_venu_stat_x = Config.SCREEN_WIDTH - self.battle_venu_stat.get_width()  # Touching right edge
            if self.battle_dialog:
                self.battle_venu_stat_y = Config.SCREEN_HEIGHT - self.battle_dialog.get_height() - self.battle_venu_stat.get_height()  # Above dialog
            else:
                self.battle_venu_stat_y = Config.SCREEN_HEIGHT - 200
            self.battle_venu_stat_visible = True  # Always visible, no sliding animation
        else:
            self.battle_venu_stat_x = 0
            self.battle_venu_stat_y = 0
            self.battle_venu_stat_visible = False
        
        # Calculate slide speeds so all animations end at the same time
        # Find the maximum distance to travel
        max_distance = 0
        distances = {}
        
        if self.battle_grass:
            grass_distance = abs(self.battle_grass_left_target_x - self.battle_grass_left_x)
            distances['grass'] = grass_distance
            max_distance = max(max_distance, grass_distance)
        
        if self.battle_pokemonstat:
            pokemonstat_distance = abs(self.battle_pokemonstat_target_x - self.battle_pokemonstat_x)
            distances['pokemonstat'] = pokemonstat_distance
            max_distance = max(max_distance, pokemonstat_distance)
        
        if self.battle_water:
            water_distance = abs(self.battle_water_target_x - self.battle_water_x)
            distances['water'] = water_distance
            max_distance = max(max_distance, water_distance)
        
        if self.battle_trainer_sprites:
            trainer_distance = abs(self.battle_trainer_target_x - self.battle_trainer_x)
            distances['trainer'] = trainer_distance
            max_distance = max(max_distance, trainer_distance)
        
        # Calculate speeds based on distance (farther = faster)
        # Time to complete = distance / speed, so speed = distance / time
        # We want all to finish in the same time, so speed is proportional to distance
        if max_distance > 0:
            # Calculate speeds proportional to distance
            if 'grass' in distances and distances['grass'] > 0:
                self.battle_grass_speed = (distances['grass'] / max_distance) * self.battle_slide_speed_base
            else:
                self.battle_grass_speed = self.battle_slide_speed_base
            
            if 'pokemonstat' in distances and distances['pokemonstat'] > 0:
                self.battle_pokemonstat_speed = (distances['pokemonstat'] / max_distance) * self.battle_slide_speed_base
            else:
                self.battle_pokemonstat_speed = self.battle_slide_speed_base
            
            if 'water' in distances and distances['water'] > 0:
                self.battle_water_speed = (distances['water'] / max_distance) * self.battle_slide_speed_base
            else:
                self.battle_water_speed = self.battle_slide_speed_base
            
            if 'trainer' in distances and distances['trainer'] > 0:
                self.battle_trainer_speed = (distances['trainer'] / max_distance) * self.battle_slide_speed_base
            else:
                self.battle_trainer_speed = self.battle_slide_speed_base
        else:
            # Fallback if no distances
            self.battle_grass_speed = self.battle_slide_speed_base
            self.battle_pokemonstat_speed = self.battle_slide_speed_base
            self.battle_water_speed = self.battle_slide_speed_base
            self.battle_trainer_speed = self.battle_slide_speed_base
    
    def cell_to_pixel(self, cell_x, cell_y, sprite_width=0, sprite_height=0):
        """
        Convert grid cell coordinates to pixel position.
        Cell (x, y) means the top-left corner of the sprite is placed at that grid cell.
        
        This is a reusable function for placing any sprite on the map.
        Example usage:
            - Lugia at cell (4, 4): cell_to_pixel(4, 4) places Lugia's top-left at cell (4, 4)
            - Tree at cell (8, 2): cell_to_pixel(8, 2) places tree's top-left at cell (8, 2)
        
        Args:
            cell_x: Grid cell X coordinate (0-based, left to right)
            cell_y: Grid cell Y coordinate (0-based, top to bottom)
            sprite_width: Width of sprite in pixels (optional, currently unused)
            sprite_height: Height of sprite in pixels (optional, currently unused)
        
        Returns:
            tuple: (pixel_x, pixel_y) - Top-left pixel position for placing the sprite
        """
        grid_size = 32
        pixel_x = cell_x * grid_size
        pixel_y = cell_y * grid_size
        return (pixel_x, pixel_y)
    
    def load_lugia(self):
        """Load the Lugia sprite sheet - all sprites in a row, each 132x132"""
        lugia_path = os.path.join(Config.SPRITES_PATH, "lugia.png")
        
        try:
            sheet = pygame.image.load(lugia_path).convert_alpha()
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            
            # Calculate number of frames (all sprites in a row)
            sprite_size = 132
            num_frames = sheet_width // sprite_size
            
            if num_frames == 0:
                print(f"Warning: Lugia sprite sheet too small ({sheet_width}px)")
                return []
            
            # Extract all sprites
            lugia_sprites = []
            for i in range(num_frames):
                x = i * sprite_size
                if x + sprite_size <= sheet_width and sprite_size <= sheet_height:
                    try:
                        sprite_rect = pygame.Rect(x, 0, sprite_size, sprite_size)
                        sprite = sheet.subsurface(sprite_rect)
                        lugia_sprites.append(sprite)
                    except (ValueError, pygame.error) as e:
                        print(f"Error extracting Lugia frame {i}: {e}")
                        # Create placeholder
                        placeholder = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
                        placeholder.fill((100, 100, 255, 128))
                        lugia_sprites.append(placeholder)
            
            return lugia_sprites
        except pygame.error as e:
            print(f"Unable to load Lugia sprite: {lugia_path}")
            print(f"Error: {e}")
            # Create a placeholder sprite
            placeholder = pygame.Surface((132, 132), pygame.SRCALPHA)
            placeholder.fill((100, 100, 255, 128))
            return [placeholder]
    
    def on_enter(self):
        """Called when entering house/village scene"""
        # Reset player position to a walkable area (cell 15,6 - center of first rectangle)
        grid_size = 32
        self.player_world_x = 15 * grid_size + grid_size // 2  # Center of cell 15
        self.player_world_y = 6 * grid_size + grid_size // 2   # Center of cell 6
        
        # Reset camera
        self.update_camera()
        
        # Reset movement state
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.current_direction = 0
    
    def handle_event(self, event):
        """Handle input for movement"""
        # Handle R key to restart scene
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Restart the scene from the beginning
                self.on_enter()
                # Reset Lugia state
                self.lugia_state = "hidden"
                self.lugia_y = -200
                self.lugia_animation_complete = False
                self.dialog_visible = False
                self.dialog_fully_visible = False
                self.dialog_slide_y = Config.SCREEN_HEIGHT
                self.fade_state = "none"
                self.fade_alpha = 0
                # Reset battle animations
                self.battle_animations_started = False
                if self.battle_dialog:
                    self.battle_dialog_x = (Config.SCREEN_WIDTH - self.battle_dialog.get_width()) // 2
                    self.battle_dialog_alpha = 0
                    self.battle_dialog_visible = False
                if self.battle_trainer_sprites:
                    self.battle_trainer_x = Config.SCREEN_WIDTH
                    self.battle_trainer_current_frame = 0
                    self.battle_trainer_can_animate = False
                    self.battle_trainer_visible = False
                    self.battle_trainer_slide_out = False
                    self.battle_trainer_alpha = 255
                if self.battle_venu:
                    self.battle_venu_y = Config.SCREEN_HEIGHT
                    self.battle_venu_visible = False
                    self.battle_venu_current_frame = 0
                    self.battle_venu_animation_time = 0
                # Reset text fade state
                self.battle_text_state = "lugia"
                self.battle_text_lugia_alpha = 255
                self.battle_text_venusaur_alpha = 0
                self.battle_text_fading = False
                # Reset dialog pause timer
                self.dialog_pause_timer = 0
                if self.battle_lugia:
                    self.battle_lugia_x = Config.SCREEN_WIDTH
                    self.battle_lugia_visible = False
                    self.battle_lugia_current_frame = 0
                    self.battle_lugia_animation_time = 0
                if self.battle_grass:
                    self.battle_grass_left_x = -self.battle_grass.get_width() if self.battle_grass else 0
                    self.battle_grass_visible = False
                if self.battle_pokemonstat:
                    self.battle_pokemonstat_x = -self.battle_pokemonstat.get_width() if self.battle_pokemonstat else 0
                    self.battle_pokemonstat_visible = False
                if self.battle_water:
                    self.battle_water_x = Config.SCREEN_WIDTH
                    self.battle_water_visible = False
                return
        
        # Handle click to hide dialog and start fade (only if battle hasn't started yet)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.lugia_animation_complete and self.dialog_fully_visible:
                # Only allow click if battle hasn't started (fade_state is not "faded")
                if self.fighting_background and self.fade_state != "faded":
                    self.fade_state = "fading"
                    self.fade_alpha = 0
        
        # Stop movement input when Lugia sequence is active or dialog is visible
        if self.dialog_visible:
            return  # Don't process movement when dialog is showing
        if self.lugia_state != "hidden" and not self.lugia_animation_complete:
            return  # Don't process movement during Lugia sequence
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.moving_up = True
                self.current_direction = 1
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.moving_down = True
                self.current_direction = 0
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.moving_left = True
                self.current_direction = 3
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.moving_right = True
                self.current_direction = 2
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.moving_up = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.moving_down = False
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.moving_left = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.moving_right = False
    
    def update_camera(self):
        """
        Update camera position to keep character centered
        Camera stops at map edges but allows character to move
        """
        # Calculate where camera should be to center character
        target_camera_x = self.player_world_x - Config.SCREEN_WIDTH // 2
        target_camera_y = self.player_world_y - Config.SCREEN_HEIGHT // 2
        
        # Clamp camera to map boundaries
        min_camera_x = 0
        max_camera_x = max(0, self.map_width - Config.SCREEN_WIDTH)
        min_camera_y = 0
        max_camera_y = max(0, self.map_height - Config.SCREEN_HEIGHT)
        
        self.camera_x = max(min_camera_x, min(target_camera_x, max_camera_x))
        self.camera_y = max(min_camera_y, min(target_camera_y, max_camera_y))
    
    def update(self):
        """Update player movement and camera"""
        # Stop player movement completely once dialog is visible
        if self.dialog_visible:
            # Player cannot move at all after dialog appears
            dx = 0
            dy = 0
        elif self.lugia_state != "hidden" and not self.lugia_animation_complete:
            # Player cannot move during Lugia sequence (before dialog)
            dx = 0
            dy = 0
        else:
            # Calculate movement (only if dialog not visible)
            dx = 0
            dy = 0
            
            if self.moving_left:
                dx -= Config.PLAYER_SPEED
                self.current_direction = 3  # Row 3 = left
            if self.moving_right:
                dx += Config.PLAYER_SPEED
                self.current_direction = 2  # Row 2 = right
            if self.moving_up:
                dy -= Config.PLAYER_SPEED
                self.current_direction = 1
            if self.moving_down:
                dy += Config.PLAYER_SPEED
                self.current_direction = 0
        
        # Update player position only if movement allowed
        if dx != 0 or dy != 0:
            # Calculate new position
            new_x = self.player_world_x + dx
            new_y = self.player_world_y + dy
            
            # Keep player within map bounds (with some margin for character size)
            margin = 10
            new_x = max(margin, min(new_x, self.map_width - self.player_width - margin))
            new_y = max(margin, min(new_y, self.map_height - self.player_height - margin))
            
            # Grid/cells are 32x32
            grid_size = 32
            
            # Check if the new position is in a walkable area
            player_center_x = new_x + self.player_width // 2
            player_center_y = new_y + self.player_height // 2
            player_cell_x = player_center_x // grid_size
            player_cell_y = player_center_y // grid_size
            
            # Check if player is in a walkable cell
            is_walkable = False
            
            # Check rectangles
            for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                if min_x <= player_cell_x <= max_x and min_y <= player_cell_y <= max_y:
                    is_walkable = True
                    break
            
            # Check individual cells
            if not is_walkable:
                for cell_x, cell_y in self.walkable_cells:
                    if player_cell_x == cell_x and player_cell_y == cell_y:
                        is_walkable = True
                        break
            
            # Only update position if in a walkable area
            if is_walkable:
                self.player_world_x = new_x
                self.player_world_y = new_y
        
        # Update camera to follow player
        self.update_camera()
        
        # Update animation
        # Stop animating completely when dialog is visible
        if self.dialog_visible:
            # Character stays in place, no animation
            self.character_sprite.update(self.current_direction, False)
        else:
            # Only animate if player can actually move (not locked) and is moving
            can_move = self.lugia_state == "hidden" or self.lugia_animation_complete
            is_moving = (self.moving_up or self.moving_down or self.moving_left or self.moving_right) and can_move
            # If movement is locked, show idle frame (frame 0) - don't animate
            if not can_move:
                # Force idle frame when locked - update with is_moving=False to show idle
                self.character_sprite.update(self.current_direction, False)
            else:
                # Normal animation when movement is allowed
                self.character_sprite.update(self.current_direction, is_moving)
        
        # Check if player is in the cells directly under Lugia
        grid_size = 32
        
        # Calculate Lugia's position in grid cells (from its pixel position)
        lugia_cell_x = self.lugia_target_x // grid_size
        lugia_cell_y = self.lugia_target_y // grid_size
        
        # Lugia is 132x132px, so it spans multiple cells
        # Calculate which cells are directly under Lugia (below its bottom)
        lugia_bottom_y = self.lugia_target_y + 132  # Bottom of Lugia sprite
        lugia_bottom_cell_y = lugia_bottom_y // grid_size  # Cell row below Lugia
        
        # Lugia spans horizontally - check cells under Lugia's width
        lugia_left_cell_x = self.lugia_target_x // grid_size
        lugia_right_cell_x = (self.lugia_target_x + 132) // grid_size  # Right edge of Lugia
        
        # Calculate player's grid cell position
        player_cell_x = (self.player_world_x + self.player_width // 2) // grid_size
        player_cell_y = (self.player_world_y + self.player_height // 2) // grid_size
        
        # Check if player is in cells directly under Lugia (same X range, Y = lugia_bottom_cell_y)
        under_lugia = (lugia_left_cell_x <= player_cell_x <= lugia_right_cell_x and 
                      player_cell_y == lugia_bottom_cell_y)
        
        # Update Lugia state machine
        if self.lugia_state == "hidden" and under_lugia:
            # Player reached bridge end - start Lugia flying in
            self.lugia_state = "flying_in"
        
        elif self.lugia_state == "flying_in":
            # Move Lugia down towards target position
            if self.lugia_y < self.lugia_target_y:
                self.lugia_y += self.lugia_fly_speed
            else:
                # Reached target position - start animation
                self.lugia_y = self.lugia_target_y
                self.lugia_state = "animating"
                self.lugia_current_frame = 0  # Start from first frame
        
        elif self.lugia_state == "animating":
            # Play animation once end to end
            if len(self.lugia_sprites) > 0:
                self.lugia_animation_time += self.lugia_animation_speed
                if self.lugia_animation_time >= 1.0:
                    self.lugia_animation_time = 0
                    self.lugia_current_frame += 1
                    
                    # Check if animation completed (reached last frame)
                    if self.lugia_current_frame >= len(self.lugia_sprites):
                        # Stop on last sprite
                        self.lugia_current_frame = len(self.lugia_sprites) - 1
                        self.lugia_state = "stopped"
                        self.lugia_animation_complete = True
                        # Start showing dialog when animation completes
                        self.dialog_visible = True
                        self.dialog_fully_visible = False
                        # Start dialog at bottom of screen
                        self.dialog_slide_y = Config.SCREEN_HEIGHT
                        # Set dialog text (you can customize this)
                        self.dialog_text = "Lugia wants to battle!"
        
        elif self.lugia_state == "stopped":
            # Animation complete - stay on last frame, dialog will show
            if len(self.lugia_sprites) > 0:
                self.lugia_current_frame = len(self.lugia_sprites) - 1
        
        # Update dialog slide animation
        if self.dialog_visible:
            # Calculate target position based on dialog image or fixed height
            if self.dialog_image:
                dialog_height = self.dialog_image.get_height()
            else:
                dialog_height = 56  # Fallback height
            dialog_target_y = Config.SCREEN_HEIGHT - dialog_height  # Bottom of image touches bottom of screen
            
            if self.dialog_slide_y > dialog_target_y:
                # Slide up
                self.dialog_slide_y -= self.dialog_slide_speed
                if self.dialog_slide_y <= dialog_target_y:
                    self.dialog_slide_y = dialog_target_y
                    self.dialog_fully_visible = True
                    # Start pause timer when dialog becomes fully visible
                    if self.lugia_animation_complete and self.fade_state == "none":
                        self.dialog_pause_timer = 0  # Reset timer
            else:
                self.dialog_fully_visible = True
                # Start pause timer when dialog becomes fully visible
                if self.lugia_animation_complete and self.fade_state == "none":
                    self.dialog_pause_timer = 0  # Reset timer
            
            # Update pause timer and start fade after 2 seconds
            if self.dialog_fully_visible and self.lugia_animation_complete and self.fade_state == "none":
                self.dialog_pause_timer += self.game.clock.get_time()  # Add elapsed time
                if self.dialog_pause_timer >= self.dialog_pause_duration:
                    # 2 seconds have passed, start fade
                    if self.fighting_background:
                        self.fade_state = "fading"
                        self.fade_alpha = 0
                        self.dialog_pause_timer = 0  # Reset timer
            
            # Slide dialog out when fade starts
            if self.fade_state == "fading":
                self.dialog_slide_y += self.dialog_slide_speed
                if self.dialog_slide_y >= Config.SCREEN_HEIGHT:
                    self.dialog_visible = False
        
        # Handle fade transition to fighting background
        if self.fade_state == "fading":
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_state = "faded"
                self.fade_complete = True
                # Start battle slide animations when fade is complete
                if not self.battle_animations_started:
                    self.battle_animations_started = True
                    self.battle_dialog_visible = True
                    # Start all slide animations at the same time
                    self.battle_grass_visible = True
                    self.battle_pokemonstat_visible = True
                    self.battle_water_visible = True
                    self.battle_lugia_visible = True  # Lugia slides in with water
                    self.battle_trainer_visible = True
                    # battle_venu_stat stays in place (always visible, no sliding)
                    if self.battle_venu_stat:
                        self.battle_venu_stat_visible = True
        
        # Update battle UI animations
        # Battle dialog: fade in (same time as fighting background fade)
        if self.fade_state == "fading":
            # Fade in dialog at the same rate as background
            if self.battle_dialog_visible and self.battle_dialog:
                self.battle_dialog_alpha = min(255, int(self.fade_alpha))
        
        if self.fade_state == "faded":
            # Keep dialog fully visible when fade is complete
            if self.battle_dialog_visible and self.battle_dialog:
                self.battle_dialog_alpha = 255
            
            # All slide animations start at the same time after fade completes
            # They all use the same speed so they should finish together
            
            # Battle grass: fly in from left (with calculated speed)
            if self.battle_grass_visible and self.battle_grass:
                if self.battle_grass_left_x < self.battle_grass_left_target_x:
                    self.battle_grass_left_x += self.battle_grass_speed
                    if self.battle_grass_left_x >= self.battle_grass_left_target_x:
                        self.battle_grass_left_x = self.battle_grass_left_target_x
            
            # Battle pokemonstat: fly in from left (with calculated speed)
            if self.battle_pokemonstat_visible and self.battle_pokemonstat:
                if self.battle_pokemonstat_x < self.battle_pokemonstat_target_x:
                    self.battle_pokemonstat_x += self.battle_pokemonstat_speed
                    if self.battle_pokemonstat_x >= self.battle_pokemonstat_target_x:
                        self.battle_pokemonstat_x = self.battle_pokemonstat_target_x
            
            # Battle water: fly in from right (with calculated speed)
            if self.battle_water_visible and self.battle_water:
                if self.battle_water_x > self.battle_water_target_x:
                    self.battle_water_x -= self.battle_water_speed
                    if self.battle_water_x <= self.battle_water_target_x:
                        self.battle_water_x = self.battle_water_target_x
            
            # Battle Lugia: fly in from right with water (same speed and timing)
            if self.battle_lugia_visible and self.battle_lugia and self.battle_lugia_frames:
                if self.battle_lugia_x > self.battle_lugia_target_x:
                    self.battle_lugia_x -= self.battle_water_speed  # Same speed as water
                    if self.battle_lugia_x <= self.battle_lugia_target_x:
                        self.battle_lugia_x = self.battle_lugia_target_x
                
                # Animate Lugia GIF
                if len(self.battle_lugia_frames) > 1:
                    self.battle_lugia_animation_time += self.battle_lugia_animation_speed
                    if self.battle_lugia_animation_time >= 1.0:
                        self.battle_lugia_animation_time = 0
                        self.battle_lugia_current_frame = (self.battle_lugia_current_frame + 1) % len(self.battle_lugia_frames)
                        self.battle_lugia = self.battle_lugia_frames[self.battle_lugia_current_frame]
            
            # Battle trainer: slide in from right, same location as grass but higher z-index (with calculated speed)
            if self.battle_trainer_visible and self.battle_trainer_sprites:
                if self.battle_trainer_x > self.battle_trainer_target_x:
                    self.battle_trainer_x -= self.battle_trainer_speed
                    if self.battle_trainer_x <= self.battle_trainer_target_x:
                        self.battle_trainer_x = self.battle_trainer_target_x
                
                # Check if all slide animations are complete before animating trainer sprite
                all_animations_complete = True
                if self.battle_grass_visible and self.battle_grass:
                    if self.battle_grass_left_x != self.battle_grass_left_target_x:
                        all_animations_complete = False
                if self.battle_pokemonstat_visible and self.battle_pokemonstat:
                    if self.battle_pokemonstat_x != self.battle_pokemonstat_target_x:
                        all_animations_complete = False
                if self.battle_water_visible and self.battle_water:
                    if self.battle_water_x != self.battle_water_target_x:
                        all_animations_complete = False
                if self.battle_trainer_x != self.battle_trainer_target_x:
                    all_animations_complete = False
                
                # Enable trainer sprite animation only when all slide animations are done
                if all_animations_complete:
                    self.battle_trainer_can_animate = True
                
                # Animate trainer sprite only after everything has animated in
                if self.battle_trainer_can_animate and self.battle_trainer_x == self.battle_trainer_target_x and not self.battle_trainer_slide_out:
                    # Animate trainer sprite
                    self.battle_trainer_animation_time += self.battle_trainer_animation_speed
                    if self.battle_trainer_animation_time >= 1.0:
                        self.battle_trainer_animation_time = 0
                        # Only advance frame if not at last frame
                        if self.battle_trainer_current_frame < len(self.battle_trainer_sprites) - 1:
                            self.battle_trainer_current_frame += 1
                        else:
                            # Reached last frame - start venusaur GIF slide in, then slide out
                            # Start venusaur GIF sliding in from under dialog (before trainer fades)
                            self.battle_venu_visible = True
                            # Start text fade transition
                            if not self.battle_text_fading:
                                self.battle_text_fading = True
                                self.battle_text_state = "transitioning"
                            # Then start trainer slide out
                            self.battle_trainer_slide_out = True
                            self.battle_trainer_alpha = 255
                
                # Trainer slide out and fade (to the left, same speed as came in)
                if self.battle_trainer_slide_out:
                    # Slide left (same speed as came in)
                    trainer_slide_out_target = -180  # Off-screen left (trainer width)
                    if self.battle_trainer_x > trainer_slide_out_target:
                        self.battle_trainer_x -= self.battle_trainer_speed
                        # Fade out as it slides (calculate fade based on distance traveled)
                        total_slide_distance = abs(self.battle_trainer_target_x - trainer_slide_out_target)
                        current_slide_distance = abs(self.battle_trainer_x - self.battle_trainer_target_x)
                        fade_progress = min(1.0, current_slide_distance / total_slide_distance)
                        self.battle_trainer_alpha = int(255 * (1.0 - fade_progress))
                    
                    # When trainer has fully faded out
                    if self.battle_trainer_x <= trainer_slide_out_target or self.battle_trainer_alpha <= 0:
                        self.battle_trainer_alpha = 0
                        self.battle_trainer_visible = False
            
            # Battle venusaur GIF: slide in from under dialog box (after trainer animation completes)
            if self.battle_venu_visible and self.battle_venu and self.battle_venu_frames:
                if self.battle_venu_y > self.battle_venu_target_y:
                    self.battle_venu_y -= self.battle_trainer_speed  # Slide up from under dialog
                    if self.battle_venu_y <= self.battle_venu_target_y:
                        self.battle_venu_y = self.battle_venu_target_y
                
                # Animate Venusaur GIF
                if len(self.battle_venu_frames) > 1:
                    self.battle_venu_animation_time += self.battle_venu_animation_speed
                    if self.battle_venu_animation_time >= 1.0:
                        self.battle_venu_animation_time = 0
                        self.battle_venu_current_frame = (self.battle_venu_current_frame + 1) % len(self.battle_venu_frames)
                        self.battle_venu = self.battle_venu_frames[self.battle_venu_current_frame]
            
            # Handle text fade transition
            if self.battle_text_fading:
                # Fade out Lugia text, fade in Venusaur text
                if self.battle_text_lugia_alpha > 0:
                    self.battle_text_lugia_alpha = max(0, self.battle_text_lugia_alpha - self.battle_text_fade_speed)
                if self.battle_text_lugia_alpha == 0 and self.battle_text_venusaur_alpha < 255:
                    self.battle_text_venusaur_alpha = min(255, self.battle_text_venusaur_alpha + self.battle_text_fade_speed)
                    if self.battle_text_venusaur_alpha >= 255:
                        self.battle_text_state = "venusaur"
                        self.battle_text_fading = False
    
    def render(self, screen):
        """Render house/village scene with scrolling map"""
        # If fully faded, show battle screen with animations
        if self.fade_state == "faded" and self.fighting_background:
            # Draw fighting background
            scaled_bg = pygame.transform.scale(self.fighting_background, 
                                             (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
            
            # Draw battle UI elements (order matters - draw in correct z-order)
            # Draw battle grass (left side only, above dialog) - lowest z-index
            if self.battle_grass_visible and self.battle_grass:
                screen.blit(self.battle_grass, (self.battle_grass_left_x, self.battle_grass_y))
            
            # Draw battle trainer (on top of grass, same location, higher z-index)
            # Trainer is directly above dialog, same X position as grass
            if self.battle_trainer_visible and self.battle_trainer_sprites and self.battle_trainer_alpha > 0:
                frame = min(self.battle_trainer_current_frame, len(self.battle_trainer_sprites) - 1)
                current_trainer_sprite = self.battle_trainer_sprites[frame]
                # Apply fade alpha for slide out
                if self.battle_trainer_alpha < 255:
                    temp_trainer = current_trainer_sprite.copy()
                    temp_trainer.set_alpha(int(self.battle_trainer_alpha))
                    screen.blit(temp_trainer, (self.battle_trainer_x, self.battle_trainer_y))
                else:
                    screen.blit(current_trainer_sprite, (self.battle_trainer_x, self.battle_trainer_y))
            
            # Draw battle water (top right)
            if self.battle_water_visible and self.battle_water:
                screen.blit(self.battle_water, (self.battle_water_x, self.battle_water_y))
            
            # Draw battle Lugia (on top of water, higher z-index, centered on water)
            if self.battle_lugia_visible and self.battle_lugia:
                screen.blit(self.battle_lugia, (self.battle_lugia_x, self.battle_lugia_y))
            
            # Draw battle pokemonstat (top left)
            if self.battle_pokemonstat_visible and self.battle_pokemonstat:
                screen.blit(self.battle_pokemonstat, (self.battle_pokemonstat_x, self.battle_pokemonstat_y))
            
            # Draw battle venusaur GIF (above dialog, furthest left)
            if self.battle_venu_visible and self.battle_venu:
                screen.blit(self.battle_venu, (self.battle_venu_x, self.battle_venu_y))
            
            # Draw battle venusaur stat PNG (separate image, stays in place on right side)
            if self.battle_venu_stat_visible and self.battle_venu_stat:
                screen.blit(self.battle_venu_stat, (self.battle_venu_stat_x, self.battle_venu_stat_y))
            
            # Draw battle dialog (center bottom, on top of everything) - highest z-index
            if self.battle_dialog_visible and self.battle_dialog:
                # Apply fade alpha to dialog
                if self.battle_dialog_alpha < 255:
                    temp_dialog = self.battle_dialog.copy()
                    temp_dialog.set_alpha(self.battle_dialog_alpha)
                    screen.blit(temp_dialog, (self.battle_dialog_x, self.battle_dialog_y))
                else:
                    screen.blit(self.battle_dialog, (self.battle_dialog_x, self.battle_dialog_y))
                
                # Draw battle dialog text
                # Starts with "A wild Bugia appeared!" then fades to "What should Venusaur do?" when venusaur slides in
                # Same font/size as Lugia text (32px Pokemon pixel font)
                # Width: half of dialog box/screen, closer to left, white text
                if self.battle_dialog_alpha >= 255:  # Only draw text when dialog is fully visible
                    # Text width should be half of dialog box/screen
                    max_text_width = Config.SCREEN_WIDTH // 2
                    
                    # Position: slightly to the right (32px from left), vertically centered
                    text_x = 32  # Slightly to the right
                    dialog_height = self.battle_dialog.get_height()
                    
                    # Render Lugia text ("A wild Bugia appeared!")
                    lugia_line1_text = "A wild Bugia"
                    lugia_line2_text = "appeared!"
                    lugia_line1_surface = self.dialog_font.render(lugia_line1_text, True, (255, 255, 255))  # White text
                    lugia_line2_surface = self.dialog_font.render(lugia_line2_text, True, (255, 255, 255))  # White text
                    
                    # Scale down if needed
                    if lugia_line1_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / lugia_line1_surface.get_width()
                        new_width = int(lugia_line1_surface.get_width() * scale_factor)
                        new_height = int(lugia_line1_surface.get_height() * scale_factor)
                        lugia_line1_surface = pygame.transform.scale(lugia_line1_surface, (new_width, new_height))
                    
                    if lugia_line2_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / lugia_line2_surface.get_width()
                        new_width = int(lugia_line2_surface.get_width() * scale_factor)
                        new_height = int(lugia_line2_surface.get_height() * scale_factor)
                        lugia_line2_surface = pygame.transform.scale(lugia_line2_surface, (new_width, new_height))
                    
                    # Render Venusaur text ("What should Venusaur do?")
                    venusaur_line1_text = "What should"
                    venusaur_line2_text = "Venusaur do?"
                    venusaur_line1_surface = self.dialog_font.render(venusaur_line1_text, True, (255, 255, 255))  # White text
                    venusaur_line2_surface = self.dialog_font.render(venusaur_line2_text, True, (255, 255, 255))  # White text
                    
                    # Scale down if needed
                    if venusaur_line1_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / venusaur_line1_surface.get_width()
                        new_width = int(venusaur_line1_surface.get_width() * scale_factor)
                        new_height = int(venusaur_line1_surface.get_height() * scale_factor)
                        venusaur_line1_surface = pygame.transform.scale(venusaur_line1_surface, (new_width, new_height))
                    
                    if venusaur_line2_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / venusaur_line2_surface.get_width()
                        new_width = int(venusaur_line2_surface.get_width() * scale_factor)
                        new_height = int(venusaur_line2_surface.get_height() * scale_factor)
                        venusaur_line2_surface = pygame.transform.scale(venusaur_line2_surface, (new_width, new_height))
                    
                    # Calculate total height for both lines (use Lugia text for positioning)
                    total_text_height = lugia_line1_surface.get_height() + lugia_line2_surface.get_height()
                    line1_y = self.battle_dialog_y + (dialog_height - total_text_height) // 2
                    line2_y = line1_y + lugia_line1_surface.get_height()
                    
                    # Draw Lugia text with fade
                    if self.battle_text_lugia_alpha > 0:
                        temp_lugia_line1 = lugia_line1_surface.copy()
                        temp_lugia_line1.set_alpha(int(self.battle_text_lugia_alpha))
                        screen.blit(temp_lugia_line1, (text_x, line1_y))
                        
                        temp_lugia_line2 = lugia_line2_surface.copy()
                        temp_lugia_line2.set_alpha(int(self.battle_text_lugia_alpha))
                        screen.blit(temp_lugia_line2, (text_x, line2_y))
                    
                    # Draw Venusaur text with fade
                    if self.battle_text_venusaur_alpha > 0:
                        temp_venusaur_line1 = venusaur_line1_surface.copy()
                        temp_venusaur_line1.set_alpha(int(self.battle_text_venusaur_alpha))
                        screen.blit(temp_venusaur_line1, (text_x, line1_y))
                        
                        temp_venusaur_line2 = venusaur_line2_surface.copy()
                        temp_venusaur_line2.set_alpha(int(self.battle_text_venusaur_alpha))
                        screen.blit(temp_venusaur_line2, (text_x, line2_y))
            
            return  # Skip drawing the map scene
        
        # Calculate fade opacity for current scene (fades out as transition progresses)
        scene_opacity = 255
        if self.fade_state == "fading":
            scene_opacity = max(0, 255 - self.fade_alpha)
        
        # Calculate the portion of the map to draw
        map_rect = pygame.Rect(
            self.camera_x,
            self.camera_y,
            Config.SCREEN_WIDTH,
            Config.SCREEN_HEIGHT
        )
        
        # Draw the visible portion of the map with fade
        if scene_opacity < 255:
            temp_map = self.map_image.subsurface(map_rect).copy()
            temp_map.set_alpha(scene_opacity)
            screen.blit(temp_map, (0, 0))
        else:
            screen.blit(self.map_image, (0, 0), map_rect)
        
        # Collect all sprites to draw with depth sorting
        sprites_to_draw = []
        
        # Plants removed - no longer drawing them
        
        # Add player
        player_screen_x = self.player_world_x - self.camera_x
        player_screen_y = self.player_world_y - self.camera_y
        
        current_sprite = self.character_sprite.get_current_sprite()
        if current_sprite:
            # Center the sprite horizontally (sprite width may differ from player_width)
            sprite_width = current_sprite.get_width()
            sprite_x = player_screen_x - (sprite_width - self.player_width) // 2
            sprites_to_draw.append({
                'sprite': current_sprite,
                'x': sprite_x,
                'y': player_screen_y,
                'depth': self.player_world_y + self.player_height  # Bottom of player
            })
        else:
            # Fallback: draw placeholder rectangle
            player_rect = pygame.Rect(
                player_screen_x,
                player_screen_y,
                self.player_width,
                self.player_height
            )
            pygame.draw.rect(screen, (255, 0, 0), player_rect)  # Red placeholder
        
        # Add Lugia
        if self.lugia_state != "hidden" and len(self.lugia_sprites) > 0:
            lugia_screen_x = self.lugia_x - self.camera_x
            lugia_screen_y = self.lugia_y - self.camera_y
            
            # Only draw if Lugia is visible on screen
            if (lugia_screen_x + 132 > 0 and lugia_screen_x < Config.SCREEN_WIDTH and
                lugia_screen_y + 132 > 0 and lugia_screen_y < Config.SCREEN_HEIGHT):
                frame = min(self.lugia_current_frame, len(self.lugia_sprites) - 1)
                current_lugia_sprite = self.lugia_sprites[frame]
                sprites_to_draw.append({
                    'sprite': current_lugia_sprite,
                    'x': lugia_screen_x,
                    'y': lugia_screen_y,
                    'depth': self.lugia_y + 132  # Bottom of Lugia
                })
        
        # Sort by depth (Y position) - lower Y values draw first, higher Y values on top
        sprites_to_draw.sort(key=lambda s: s['depth'])
        
        # Draw all sprites in sorted order with fade
        for sprite_data in sprites_to_draw:
            if scene_opacity < 255:
                # Apply fade to sprite
                temp_sprite = sprite_data['sprite'].copy()
                temp_sprite.set_alpha(scene_opacity)
                screen.blit(temp_sprite, (sprite_data['x'], sprite_data['y']))
            else:
                screen.blit(sprite_data['sprite'], (sprite_data['x'], sprite_data['y']))
        
        # DEBUG: Draw transparent red indicator for Lugia trigger area (cells under Lugia)
        grid_size = 32
        
        # Calculate Lugia's trigger cells (cells directly under Lugia)
        lugia_cell_x = self.lugia_target_x // grid_size
        lugia_left_cell_x = self.lugia_target_x // grid_size
        lugia_right_cell_x = (self.lugia_target_x + 132) // grid_size
        lugia_bottom_y = self.lugia_target_y + 132
        lugia_bottom_cell_y = lugia_bottom_y // grid_size
        
        # Draw red transparent rectangles for all cells under Lugia
        for cell_x in range(lugia_left_cell_x, lugia_right_cell_x + 1):
            trigger_world_x = cell_x * grid_size
            trigger_world_y = lugia_bottom_cell_y * grid_size
            trigger_screen_x = trigger_world_x - self.camera_x
            trigger_screen_y = trigger_world_y - self.camera_y
            
            # Draw red transparent rectangle for trigger area
            if (trigger_screen_x + grid_size > 0 and trigger_screen_x < Config.SCREEN_WIDTH and
                trigger_screen_y + grid_size > 0 and trigger_screen_y < Config.SCREEN_HEIGHT):
                debug_surface = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
                debug_surface.fill((255, 0, 0, 128))  # Transparent red
                screen.blit(debug_surface, (trigger_screen_x, trigger_screen_y))
        
        # Also show player's current cell position for debugging
        player_cell_x = (self.player_world_x + self.player_width // 2) // grid_size
        player_cell_y = (self.player_world_y + self.player_height // 2) // grid_size
        player_cell_world_x = player_cell_x * grid_size
        player_cell_world_y = player_cell_y * grid_size
        player_cell_screen_x = player_cell_world_x - self.camera_x
        player_cell_screen_y = player_cell_world_y - self.camera_y
        
        # Draw blue transparent rectangle for player's current cell
        if (player_cell_screen_x + grid_size > 0 and player_cell_screen_x < Config.SCREEN_WIDTH and
            player_cell_screen_y + grid_size > 0 and player_cell_screen_y < Config.SCREEN_HEIGHT):
            player_debug_rect = pygame.Rect(player_cell_screen_x, player_cell_screen_y, grid_size, grid_size)
            player_debug_surface = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
            player_debug_surface.fill((0, 0, 255, 128))  # Transparent blue
            screen.blit(player_debug_surface, (player_cell_screen_x, player_cell_screen_y))
        
        # Draw instructions (optional, can be removed) - only if dialog not showing
        if not self.dialog_visible:
            font = pygame.font.Font(None, 20)
            text = font.render(f"Use WASD or Arrow Keys to move | Cell: ({player_cell_x}, {player_cell_y})", True, (255, 255, 255))
            text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, 20))
            # Draw semi-transparent background for text
            bg_surface = pygame.Surface((text_rect.width + 10, text_rect.height + 4))
            bg_surface.set_alpha(128)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, (text_rect.x - 5, text_rect.y - 2))
            screen.blit(text, text_rect)
        
        # Draw dialog box with text (slides in and out together)
        if self.dialog_visible and self.fade_state != "faded":
            # Only draw if dialog is on screen
            if 0 <= self.dialog_slide_y < Config.SCREEN_HEIGHT:
                # Draw dialog image if available
                if self.dialog_image:
                    dialog_x = (Config.SCREEN_WIDTH - self.dialog_image.get_width()) // 2  # Center horizontally
                    dialog_y = self.dialog_slide_y
                    screen.blit(self.dialog_image, (dialog_x, dialog_y))
                    
                    # Draw text on top of dialog box (middle left aligned)
                    if self.dialog_text:
                        text_surface = self.dialog_font.render(self.dialog_text, True, (0, 0, 0))
                        # Text position: 48px from left, vertically centered in dialog box
                        text_x = 48  # 48px from left
                        dialog_height = self.dialog_image.get_height()
                        text_y = dialog_y + (dialog_height - text_surface.get_height()) // 2
                        screen.blit(text_surface, (text_x, text_y))
                else:
                    # Fallback: just draw text if no dialog image
                    if self.dialog_text:
                        text_surface = self.dialog_font.render(self.dialog_text, True, (0, 0, 0))
                        text_x = 48  # 48px from left
                        text_y = self.dialog_slide_y
                        screen.blit(text_surface, (text_x, text_y))
        
        # Draw fade transition to fighting background (crossfade)
        if self.fade_state == "fading" and self.fighting_background:
            # Scale fighting background to screen size
            scaled_bg = pygame.transform.scale(self.fighting_background, 
                                               (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            
            # Draw fighting background with increasing opacity (fades in)
            bg_opacity = min(255, int(self.fade_alpha))
            if bg_opacity > 0:
                temp_bg = scaled_bg.copy()
                temp_bg.set_alpha(bg_opacity)
                screen.blit(temp_bg, (0, 0))
        

