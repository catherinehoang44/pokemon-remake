"""
Pokemon Map Scene
Map exploration with scrolling camera, character movement, Lugia sequence, and dialog
"""

import pygame
import os
import math
import random
from config import Config
from utils import SpriteSheet, AnimatedSprite

try:
    from PIL import Image, ImageSequence
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available. GIF animations will not work. Install with: pip install Pillow")


class PokemonMapScene:
    def __init__(self, game):
        self.game = game
        
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
        ]
        # ============================================================================
        
        # ============================================================================
        # PROMPT PULSE SLIDE/FADE CONFIGURATION
        # Easy to adjust all prompt pulse animation settings here
        # ============================================================================
        self.prompt_pulse_fade_speed_multiplier = 2.0  # Multiplier for fade speed (2.0 = 2x faster)
        self.prompt_pulse_slide_fade_speed = None  # Uses battle_text_fade_speed if None
        # ============================================================================
        
        # ============================================================================
        # AUDIO CONFIGURATION
        # Easy to adjust all audio settings here
        # ============================================================================
        self.music_volume = 0.3  # Music volume (0.0 to 1.0, 0.7 = 70% volume, 30% reduction)
        self.sfx_volume = 0.6  # Sound effects volume (0.0 to 1.0, 1.0 = 100% volume)
        # ============================================================================
        
        # ============================================================================
        # UNIVERSAL FONT SIZE CONFIGURATION
        # Easy to adjust all font sizes here (universal across the game)
        # All fonts use this base size, with optional multipliers for specific UI elements
        # ============================================================================
        self.universal_font_size = 24  # Base font size for all text in the game (editable)
        self.dialog_font_size = self.universal_font_size  # Main dialog text size
        self.fight_ui_font_size = self.universal_font_size  # Fight UI button text size
        self.combat_ui_font_size = int(self.universal_font_size * 0.8)  # Combat UI text size (80% of base)
        self.screen_text_font_size = int(self.universal_font_size * 0.8)  # Screen text (bag/pokemon) size
        self.debug_font_size = int(self.universal_font_size * 0.8)  # Debug text size
        # ============================================================================
        
        # ============================================================================
        # DEBUGGING FEATURES CONFIGURATION
        # Set to True to enable all debugging features (hitboxes, cell location)
        # Set to False to hide all debugging features
        # Note: WASD instruction will always be visible regardless of this setting
        # ============================================================================
        self.enable_debugging_features = False  # Set to True to show debugging features
        # ============================================================================
        
        # ============================================================================
        # DEBUG START POSITION CONFIGURATION
        # Choose where the scene will begin:
        #   False = Start from the very beginning (normal gameplay)
        #   True = Start at attack sequence (when prompt pulse is used)
        # ============================================================================
        self.debug_start_at_attack_sequence = False  # Set to True to start at attack sequence
        # ============================================================================
        
        # ============================================================================
        # SPEED ADJUSTMENTS CONFIGURATION
        # The lower the number, the slower the animation.
        # ============================================================================
        # Lugia sequence speeds
        self.lugia_animation_speed = 0.1  # Animation speed for Lugia sprite
        self.lugia_fly_speed = 2.5  # Speed at which Lugia flies in
        
        # Dialog speeds
        self.dialog_slide_speed = 5  # Speed at which dialog slides up/down
        
        # Fade speeds
        self.fade_speed = 10  # Speed of fade transition to battle background
        self.battle_text_fade_speed = 5  # Speed of text fade transition (lower = slower)
        
        # Battle animation speeds
        self.battle_slide_speed_base = 8  # Base speed for battle UI slide animations
        self.battle_trainer_animation_speed = 0.15  # Speed of trainer sprite animation
        self.battle_lugia_animation_speed = 0.4  # Frame change speed for Lugia GIF
        self.battle_venu_animation_speed = 0.4  # Frame change speed for Venusaur GIF
        self.prompt_pulse_charge_animation_speed = 0.1  # Frame change speed for prompt pulse charge sprite (slower)
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
        
        # Initialize player position to a walkable area (cell 15, 11)
        grid_size = 32
        self.player_world_x = 15 * grid_size + grid_size // 2  # Center of cell 15
        self.player_world_y = 11 * grid_size + grid_size // 2   # Center of cell 11
        
        # Camera position (top-left corner of visible area)
        self.camera_x = 0
        self.camera_y = 0
        
        # Player dimensions
        self.player_width = 32
        self.player_height = 42
        
        # Load character sprite
        character_path = os.path.join(Config.SPRITES_PATH, "character_red.png")
        try:
            character_sheet = SpriteSheet(character_path, 32, 42, 128, 168)
            self.character_sprite = AnimatedSprite(character_sheet, num_frames=4)
        except Exception as e:
            print(f"Error loading character sprite: {e}")
            self.character_sprite = None
        
        # Movement state
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.current_direction = 1  # 0=down, 1=up, 2=right, 3=left (start facing up)
        
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
        # Move Lugia: originally half a cell right + one cell right, now 0.5 cell to the left from that position
        self.lugia_target_x = lugia_pixel_x + 16 + 32 - 16  # Half a cell (32/2 = 16px) + one cell to the right (32px) - 0.5 cell to the left (16px) = lugia_pixel_x + 32
        self.lugia_target_y = lugia_pixel_y
        
        # Start position (off-screen above and slightly to the right)
        self.lugia_x = self.lugia_target_x + 50  # Start slightly to the right
        self.lugia_start_x = self.lugia_x  # Store start position for smooth animation
        self.lugia_y = -200  # Off-screen above
        # Speed set in SPEED ADJUSTMENTS section above
        self.lugia_animation_complete = False
        
        # Load exclamation image (appears when character touches Lugia hitbox)
        exclamation_path = os.path.join(Config.IMAGES_PATH, "exclamation.png")
        try:
            self.exclamation_image = pygame.image.load(exclamation_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load exclamation image: {exclamation_path}")
            print(f"Error: {e}")
            self.exclamation_image = None
        
        # Exclamation animation state
        self.exclamation_visible = False
        self.exclamation_x = 0
        self.exclamation_y = 0
        self.exclamation_target_y = 0  # Target Y when sliding up
        self.exclamation_alpha = 255
        self.exclamation_state = "hidden"  # "hidden", "sliding_up", "showing", "sliding_down"
        self.exclamation_show_time = 0  # Time to show before sliding down
        self.exclamation_show_duration = 300  # Show for 300ms (faster)
        self.exclamation_slide_speed = 8  # Speed of slide animation (faster, only 1 cell)
        self.exclamation_fade_speed = 12  # Speed of fade out (faster)
        
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
            self.dialog_font = pygame.font.Font(font_path, self.dialog_font_size)
        except:
            print(f"Unable to load Pokemon pixel font: {font_path}")
            print("Using default font...")
            self.dialog_font = pygame.font.Font(None, self.dialog_font_size)
        
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
        
        # Music state
        self.battle_music_started = False  # Track if battle music has started
        
        # Initialize mixer and load music
        pygame.mixer.init()
        # Load map music
        map_music_path = os.path.join(Config.SOUNDS_PATH, "32 Mt. Moon.mp3")
        try:
            pygame.mixer.music.load(map_music_path)
            pygame.mixer.music.set_volume(self.music_volume)  # Set volume AFTER loading (fixes volume issue)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        except pygame.error as e:
            print(f"Unable to load map music: {map_music_path}")
            print(f"Error: {e}")
        
        # Load sound effects
        self.sfx_collision = None
        self.sfx_press_ab = None
        self.sfx_ball_toss = None
        self.sfx_ball_poof = None
        self.sfx_denied = None
        self.sfx_cry_17 = None
        self.sfx_spore = None
        self.sfx_spike_cannon = None
        
        try:
            collision_path = os.path.join(Config.SOUNDS_PATH, "SFX_COLLISION.wav")
            self.sfx_collision = pygame.mixer.Sound(collision_path)
            self.sfx_collision.set_volume(self.sfx_volume)
            print(f"Loaded collision sound: {collision_path}")
        except pygame.error as e:
            print(f"Unable to load collision sound: {e}")
        except Exception as e:
            print(f"Error loading collision sound: {e}")
        
        try:
            press_ab_path = os.path.join(Config.SOUNDS_PATH, "SFX_PRESS_AB.wav")
            self.sfx_press_ab = pygame.mixer.Sound(press_ab_path)
            self.sfx_press_ab.set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Unable to load press AB sound: {e}")
        
        try:
            ball_toss_path = os.path.join(Config.SOUNDS_PATH, "SFX_BALL_TOSS.wav")
            self.sfx_ball_toss = pygame.mixer.Sound(ball_toss_path)
            self.sfx_ball_toss.set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Unable to load ball toss sound: {e}")
        
        try:
            ball_poof_path = os.path.join(Config.SOUNDS_PATH, "SFX_BALL_POOF.wav")
            self.sfx_ball_poof = pygame.mixer.Sound(ball_poof_path)
            self.sfx_ball_poof.set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Unable to load ball poof sound: {e}")
        
        try:
            denied_path = os.path.join(Config.SOUNDS_PATH, "SFX_DENIED.wav")
            self.sfx_denied = pygame.mixer.Sound(denied_path)
            self.sfx_denied.set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Unable to load denied sound: {e}")
        
        try:
            cry_17_path = os.path.join(Config.SOUNDS_PATH, "SFX_CRY_17.wav")
            self.sfx_cry_17 = pygame.mixer.Sound(cry_17_path)
            self.sfx_cry_17.set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Unable to load cry 17 sound: {e}")
        
        try:
            spore_path = os.path.join(Config.SOUNDS_PATH, "Spore.mp3")
            self.sfx_spore = pygame.mixer.Sound(spore_path)
            self.sfx_spore.set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Unable to load Spore sound: {e}")
        
        try:
            spike_cannon_path = os.path.join(Config.SOUNDS_PATH, "SpikeCannon.mp3")
            self.sfx_spike_cannon = pygame.mixer.Sound(spike_cannon_path)
            self.sfx_spike_cannon.set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Unable to load SpikeCannon sound: {e}")
        
        # Track sound effect states to avoid playing multiple times
        self.exclamation_sound_played = False
        self.trainer_animation_sound_played = False
        self.venusaur_slide_sound_played = False
        self.spore_sound_played = False
        self.spike_cannon_sound_played = False
        self.collision_sound_playing = False  # Track if collision sound is currently playing
        
        # Audio mute state
        self.audio_muted = False
        self.original_music_volume = self.music_volume
        self.original_sfx_volume = self.sfx_volume
        self.lugia_cry_played = False  # Track if Lugia cry has been played
        self.fade_alpha = 0
        # Speed set in SPEED ADJUSTMENTS section above
        self.fade_complete = False  # Track when fade is done
        
        # Pause timer before battle fade (2 seconds after dialog appears)
        self.dialog_pause_start_time = None  # When dialog became fully visible (in ticks)
        self.dialog_pause_duration = 1800  # 1.8 seconds = 1800 milliseconds (increased by 1 second)
        
        # Battle UI elements - fly in animations
        self.battle_animations_started = False
        
        # Load battle dialog (fly in from right, center bottom)
        battle_dialog_path = os.path.join(Config.IMAGES_PATH, "battle_dialog.png")
        try:
            self.battle_dialog = pygame.image.load(battle_dialog_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load battle dialog: {battle_dialog_path}")
            self.battle_dialog = None
        
        # Load fight UI image (fades in with Venusaur text, bottom right, above dialog)
        fight_ui_path = os.path.join(Config.IMAGES_PATH, "fight_ui.png")
        try:
            self.fight_ui = pygame.image.load(fight_ui_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load fight UI: {fight_ui_path}")
            print(f"Error: {e}")
            self.fight_ui = None
        
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
        
        # Fight UI (fades in with Venusaur text, bottom right, above dialog)
        if self.fight_ui:
            self.fight_ui_x = Config.SCREEN_WIDTH - self.fight_ui.get_width()  # Bottom right
            self.fight_ui_y = Config.SCREEN_HEIGHT - self.fight_ui.get_height()  # Bottom right
            self.fight_ui_alpha = 0  # Start transparent, will fade in with Venusaur text
            # Create invisible 2x2 grid with 12px padding for hover zones
            self.fight_ui_padding = 12
            self.fight_ui_grid_cols = 2
            self.fight_ui_grid_rows = 2
            # Calculate cell dimensions
            usable_width = self.fight_ui.get_width() - (self.fight_ui_padding * 2)
            usable_height = self.fight_ui.get_height() - (self.fight_ui_padding * 2)
            self.fight_ui_cell_width = usable_width // self.fight_ui_grid_cols
            self.fight_ui_cell_height = usable_height // self.fight_ui_grid_rows
            # Store hover state for each cell (row, col)
            self.fight_ui_hovered_cell = None  # (row, col) or None
            # Store selected cell (for BAG and RUN buttons when text is showing)
            self.fight_ui_selected_cell = None  # (row, col) or None - stays highlighted when text is showing
            # Button labels in order: top-left, top-right, bottom-left, bottom-right
            self.fight_ui_labels = ["FIGHT", "BAG", "POKEMON", "RUN"]
            
            # Combat UI move labels (left grid, 2x2, top-left to bottom-right order)
            self.combat_ui_move_labels = ["Context Recall", "Syntax Slash", "Debug Dash", "Prompt Pulse"]
            
            # Move details (PP and Type for each move)
            self.combat_ui_move_details = {
                "Context Recall": {"pp": 20, "pp_max": 20, "type": "Psychic"},
                "Syntax Slash": {"pp": 10, "pp_max": 10, "type": "Steel"},
                "Debug Dash": {"pp": 15, "pp_max": 15, "type": "Steel"},
                "Prompt Pulse": {"pp": 5, "pp_max": 5, "type": "Psychic"}
            }
            # Load button font (uses configured font size)
            # Try to use the same font as dialog, but fallback to default
            try:
                font_path = os.path.join(Config.FONTS_PATH, "pokemon_pixel_font.ttf")
                self.fight_ui_font = pygame.font.Font(font_path, self.fight_ui_font_size)
            except:
                self.fight_ui_font = pygame.font.Font(None, self.fight_ui_font_size)
            
            # Load combat UI font (slightly smaller than dialog)
            try:
                font_path = os.path.join(Config.FONTS_PATH, "pokemon_pixel_font.ttf")
                self.combat_ui_font = pygame.font.Font(font_path, self.combat_ui_font_size)
                # Create bold version for move names
                self.combat_ui_font_bold = pygame.font.Font(font_path, self.combat_ui_font_size)
                self.combat_ui_font_bold.set_bold(True)
            except:
                self.combat_ui_font = pygame.font.Font(None, self.combat_ui_font_size)
                # Create bold version for move names
                self.combat_ui_font_bold = pygame.font.Font(None, self.combat_ui_font_size)
                self.combat_ui_font_bold.set_bold(True)
        else:
            self.fight_ui_x = 0
            self.fight_ui_y = 0
            self.fight_ui_alpha = 0
            self.fight_ui_hovered_cell = None
            self.fight_ui_selected_cell = None
            self.fight_ui_labels = []
        
        # Load bag and pokemon screen images
        bag_screen_path = os.path.join(Config.IMAGES_PATH, "screen-bag.png")
        try:
            self.bag_screen = pygame.image.load(bag_screen_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load bag screen: {bag_screen_path}")
            print(f"Error: {e}")
            self.bag_screen = None
        
        pokemon_screen_path = os.path.join(Config.IMAGES_PATH, "screen-party.jpg")
        try:
            self.pokemon_screen = pygame.image.load(pokemon_screen_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load pokemon screen: {pokemon_screen_path}")
            print(f"Error: {e}")
            self.pokemon_screen = None
        
        # Load combat UI image (shown when FIGHT button is clicked)
        combat_ui_path = os.path.join(Config.IMAGES_PATH, "combat-ui.png")
        try:
            self.combat_ui = pygame.image.load(combat_ui_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load combat UI: {combat_ui_path}")
            print(f"Error: {e}")
            self.combat_ui = None
        
        # Screen state management
        self.current_screen = "battle"  # "battle", "bag", "pokemon"
        self.run_text_visible = False  # Whether "You can't run away!" text is shown
        self.run_text_alpha = 0  # Alpha for fade in/out animation
        self.run_text_fade_speed = 10  # Speed of fade animation
        self.combat_ui_visible = False  # Whether combat UI is shown
        self.full_hp_text_visible = False  # Whether "Your Cursorsaur already has full HP!" text is shown
        self.full_hp_text_alpha = 0  # Alpha for fade in/out animation
        
        # Move used sequence state (for Prompt Pulse)
        self.move_used_state = "none"  # "none", "sliding_down", "dialog_showing", "fading_black"
        self.move_used_ui_slide_y = 0  # Current Y position of UI during slide down
        self.move_used_ui_target_y = Config.SCREEN_HEIGHT  # Target Y (off-screen bottom)
        self.move_used_dialog_text = ""  # Dialog text to show ("Cursaur used Prompt Pulse!")
        self.move_used_wait_timer = 0  # Timer for waiting 1.5 seconds after dialog shows
        self.move_used_wait_duration = 1500  # 1.5 seconds in milliseconds
        self.battle_slide_out = False  # Track if battle elements should slide out
        self.prompt_pulse_fade_out = False  # Track if text/UI should fade out for prompt pulse
        self.background_black_alpha = 0  # Alpha for black background overlay (0 = transparent, 255 = fully black)
        self.black_block_alpha = 0  # Alpha for black block that covers screen during prompt pulse
        self.assets_hidden = False  # Track if assets should be hidden (once black block is fully faded in)
        
        self.venusaur_centered = False  # Track if venusaur has reached center
        self.prompt_pulse_charge_complete = False  # Track if prompt pulse charge animation has completed once
        self.venusaur_original_x = 0  # Store venusaur's original X position before moving to center
        self.venusaur_original_y = 0  # Store venusaur's original Y position before moving to center
        self.venusaur_move_back = False  # Flag to move venusaur back to original position
        self.venusaur_move_back_timer = 0  # Timer for smooth move-back animation
        self.venusaur_move_back_duration = 500  # 0.5 seconds for move-back animation
        self.lugia_original_x = 0  # Store lugia's original X position
        self.lugia_original_y = 0  # Store lugia's original Y position
        self.lugia_move_back = False  # Flag to move lugia back to original position
        self.lugia_move_back_timer = 0  # Timer for lugia move-back animation
        self.lugia_move_back_duration = 500  # 0.5 seconds for lugia move-back animation
        self.battle_lugia_alpha = 255  # Alpha for lugia fade-in during move-back
        
        # Screen shake effect (when lugia is attacked after Prompt Pulse PNG fades in)
        self.screen_shake_active = False
        self.screen_shake_timer = 0
        self.screen_shake_duration = 1000  # 1 second in milliseconds
        self.screen_shake_offset_x = 0
        self.screen_shake_offset_y = 0
        self.screen_shake_intensity = 5  # Pixels of shake
        self.lugia_rotation_angle = 0  # Rotation angle for lugia during shake
        self.lugia_slide_in_complete = False  # Track when lugia finishes sliding in
        self.screen_shake_triggered_after_pulse = False  # Track if screen shake has been triggered after Prompt Pulse PNG
        
        # End scene animation state (after prompt pulse attack completes)
        self.end_scene_active = False  # Track if end scene animation is active
        self.end_scene_health_bar_timer = 0  # Timer for health bar animation
        self.end_scene_health_bar_duration = 2000  # 2 seconds for health bar to decrease
        self.end_scene_health_bar_width = 96  # Current width of health bar (starts at 96, decreases to 0)
        self.end_scene_health_bar_initial_width = 96  # Initial width of health bar
        self.end_scene_health_bar_pause_timer = 0  # Timer for pause after health bar reaches 0
        self.end_scene_health_bar_pause_duration = 500  # 0.5 second pause before Lugia faints
        self.end_scene_health_bar_cry_played = False  # Flag to play cry sound only once when HP hits 0
        self.end_scene_music_played = False  # Flag to play end scene music only once when black bg appears
        self.end_scene_lugia_fall_timer = 0  # Timer for Lugia fall animation
        self.end_scene_lugia_fall_duration = 1000  # 1 second for Lugia to fall
        self.end_scene_lugia_fall_start_x = 0  # Starting X position for Lugia fall
        self.end_scene_lugia_fall_start_y = 0  # Starting Y position for Lugia fall
        self.end_scene_lugia_fall_alpha = 255  # Alpha for Lugia fade-out (starts at 255, fades to 0)
        self.end_scene_lugia_fall_distance = 40  # Distance to fall down (40px)
        # "Bugia fainted!" text display after Lugia faints
        self.end_scene_fainted_text_active = False  # Track if "Bugia fainted!" text should be shown
        self.end_scene_fainted_text_timer = 0  # Timer for showing "Bugia fainted!" text
        self.end_scene_fainted_text_duration = 1000  # Duration to show "Bugia fainted!" text (1 second)
        # Black background fade-in after Lugia faints
        self.end_scene_black_bg_delay_timer = 0  # Timer for delay after Lugia faints
        self.end_scene_black_bg_delay_duration = 1000  # 1 second delay before black background appears
        self.end_scene_black_bg_active = False  # Track if black background fade should start
        self.end_scene_black_bg_alpha = 0  # Alpha for black background (0 = transparent, 255 = fully black)
        self.end_scene_black_bg_timer = 0  # Timer for black background fade-in
        self.end_scene_black_bg_duration = 1000  # 1 second for black background to fade in
        self.end_scene_elements_fade_alpha = 255  # Alpha for all other elements (starts at 255, fades to 0)
        # End Venusaur image animation (after black background appears)
        self.end_scene_venusaur_active = False  # Track if end Venusaur animation should start
        self.end_scene_venusaur_image = None  # The end_venusaur.png image
        self.end_scene_venusaur_fade_timer = 0  # Timer for fade-in animation
        self.end_scene_venusaur_fade_duration = 2000  # 2 seconds for fade-in
        self.end_scene_venusaur_fade_alpha = 0  # Alpha for fade-in (0 to 255)
        self.end_scene_venusaur_slide_timer = 0  # Timer for slide animation
        self.end_scene_venusaur_slide_duration = 500  # 0.5 seconds for slide
        self.end_scene_venusaur_x = 0  # Current X position
        self.end_scene_venusaur_y = 0  # Current Y position (centered vertically)
        self.end_scene_venusaur_fade_x = 0  # X position during fade-in (centered)
        self.end_scene_venusaur_start_x = 0  # Starting X position for slide (144px from right)
        self.end_scene_venusaur_end_x = 0  # Ending X position for slide (32px from right)
        # Pokemon shine sprite animation (fades in when end_venusaur moves right)
        self.end_scene_pokemon_shine_active = False  # Track if pokemon shine animation should start
        self.end_scene_pokemon_shine_frames = []  # Frames for pokemon shine animation
        self.end_scene_pokemon_shine_current_frame = 0  # Current frame index
        self.end_scene_pokemon_shine_animation_time = 0  # Animation timer
        self.end_scene_pokemon_shine_animation_speed = 50  # Animation speed (milliseconds per frame, lower = faster)
        self.end_scene_pokemon_shine_fade_timer = 0  # Timer for fade-in animation
        self.end_scene_pokemon_shine_fade_duration = 500  # Fade-in duration (same as slide)
        self.end_scene_pokemon_shine_fade_alpha = 0  # Alpha for fade-in (0 to 255)
        self.end_scene_pokemon_shine_x = 39  # X position (39px from left)
        self.end_scene_pokemon_shine_y = 92  # Y position (92px from top)
        self.end_scene_pokemon_shine_width = 175  # Width
        self.end_scene_pokemon_shine_height = 76.37  # Height
        # End background image animation (slides in after pokemon shine fades in)
        self.end_scene_bg_active = False  # Track if end background animation should start
        self.end_scene_bg_image = None  # The end_bg.png image
        self.end_scene_bg_x = 0  # Current X position
        self.end_scene_bg_y = 0  # Current Y position (centered vertically)
        self.end_scene_bg_start_x = 0  # Starting X position (right side at left edge of screen)
        self.end_scene_bg_end_x = 0  # Ending X position (right side at right edge of screen)
        self.end_scene_bg_slide_timer = 0  # Timer for slide animation
        self.end_scene_bg_slide_duration = 1000  # Duration for slide (1 second, can be adjusted)
        # Cursor version SVG animation (fades in after end_bg, centered under pokemon shine)
        self.end_scene_cursor_active = False  # Track if cursor animation should start
        self.end_scene_cursor_image = None  # The cursor-version.svg image (converted to surface)
        self.end_scene_cursor_x = 0  # Current X position (centered horizontally)
        self.end_scene_cursor_y = 0  # Current Y position (under pokemon shine)
        self.end_scene_cursor_fade_timer = 0  # Timer for fade-in animation
        self.end_scene_cursor_fade_duration = 500  # Fade-in duration (0.5 seconds)
        self.end_scene_cursor_fade_alpha = 0  # Alpha for fade-in (0 to 255)
        self.end_scene_cursor_start_y = 0  # Starting Y position (25px below target)
        self.end_scene_cursor_target_y = 0  # Target Y position (final position)
        self.end_scene_cursor_slide_offset = 25  # Slide up distance (25px)
        # Press-r SVG animation (fades in after end_bg, centered x-wise, 10px under end_bg, blinks)
        self.end_scene_press_r_active = False  # Track if press-r animation should start
        self.end_scene_press_r_image = None  # The press-r.svg image (converted to surface)
        self.end_scene_press_r_x = 0  # Current X position (centered horizontally)
        self.end_scene_press_r_y = 0  # Current Y position (10px under end_bg)
        self.end_scene_press_r_fade_timer = 0  # Timer for fade-in animation
        self.end_scene_press_r_fade_duration = 500  # Fade-in duration (0.5 seconds)
        self.end_scene_press_r_fade_alpha = 0  # Alpha for fade-in (0 to 255)
        self.end_scene_press_r_blink_timer = 0  # Timer for blink animation
        self.end_scene_press_r_blink_fade_in_duration = 1000  # Fade in duration (1 second)
        self.end_scene_press_r_blink_hold_duration = 1000  # Hold duration (1 second)
        self.end_scene_press_r_blink_fade_out_duration = 1000  # Fade out duration (1 second)
        self.end_scene_press_r_blink_total_duration = 3000  # Total cycle duration (3 seconds)
        self.end_scene_press_r_blink_alpha = 255  # Alpha for blink (255 to 0 and back)
        self.end_scene_press_r_fade_complete = False  # Track when fade-in is complete
        
        # Load attack pulse end image (replaces black background after move-back)
        attack_pulse_end_path = os.path.join(Config.IMAGES_PATH, "attack_pulse_end.png")
        try:
            self.attack_pulse_end_image = pygame.image.load(attack_pulse_end_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load attack pulse end: {attack_pulse_end_path}")
            print(f"Error: {e}")
            self.attack_pulse_end_image = None
        
        # Load end Venusaur image (shown after black background appears)
        end_venusaur_path = os.path.join(Config.IMAGES_PATH, "end_venusaur.png")
        try:
            self.end_scene_venusaur_image = pygame.image.load(end_venusaur_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load end Venusaur image: {end_venusaur_path}")
            print(f"Error: {e}")
            self.end_scene_venusaur_image = None
        
        # Load pokemon shine sprite sheet (PNG with multiple sprites in order, 175x76.37px each)
        pokemon_shine_path = os.path.join(Config.SPRITES_PATH, "pokemon-shine.png")
        self.end_scene_pokemon_shine_frames = []
        self.end_scene_pokemon_shine_current_frame = 0
        self.end_scene_pokemon_shine_animation_time = 0
        pokemon_shine_sprite_width = 175
        pokemon_shine_sprite_height = 76  # Round 76.37 to 76 pixels
        try:
            shine_sheet = SpriteSheet(pokemon_shine_path, pokemon_shine_sprite_width, pokemon_shine_sprite_height)
            # Extract all frames from the sprite sheet (sprites are in order, likely in a single row)
            for row in range(shine_sheet.rows):
                for col in range(shine_sheet.cols):
                    frame = shine_sheet.get_sprite(row, col)
                    if frame:
                        # Scale to exact size 175x76.37px (height rounded to 76)
                        scaled_frame = pygame.transform.scale(frame, (175, 76))
                        self.end_scene_pokemon_shine_frames.append(scaled_frame)
            if self.end_scene_pokemon_shine_frames:
                self.end_scene_pokemon_shine_image = self.end_scene_pokemon_shine_frames[0]  # Use first frame as default
            else:
                print(f"Warning: No frames extracted from pokemon shine sprite sheet")
                self.end_scene_pokemon_shine_image = None
                self.end_scene_pokemon_shine_frames = []
        except Exception as e:
            print(f"Unable to load pokemon shine sprite sheet: {pokemon_shine_path}")
            print(f"Error: {e}")
            self.end_scene_pokemon_shine_image = None
            self.end_scene_pokemon_shine_frames = []
        
        # Load end background image (slides in after pokemon shine fades in)
        end_bg_path = os.path.join(Config.IMAGES_PATH, "end_bg.png")
        try:
            self.end_scene_bg_image = pygame.image.load(end_bg_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load end background image: {end_bg_path}")
            print(f"Error: {e}")
            self.end_scene_bg_image = None
        
        # Load cursor-version PNG (fades in after end_bg, centered under pokemon shine)
        cursor_png_path = os.path.join(Config.IMAGES_PATH, "cursor-version.png")
        try:
            cursor_image = pygame.image.load(cursor_png_path).convert_alpha()
            # Scale to 100px width (maintain aspect ratio)
            original_width = cursor_image.get_width()
            original_height = cursor_image.get_height()
            if original_width > 0:
                scale_factor = 100.0 / original_width
                new_height = int(original_height * scale_factor)
                self.end_scene_cursor_image = pygame.transform.scale(cursor_image, (100, new_height))
                print(f"Successfully loaded cursor-version.png: {self.end_scene_cursor_image.get_width()}x{self.end_scene_cursor_image.get_height()}")
            else:
                self.end_scene_cursor_image = cursor_image
        except pygame.error as e:
            print(f"Unable to load cursor PNG: {cursor_png_path}")
            print(f"Error: {e}")
            self.end_scene_cursor_image = None
        
        # Load press-r PNG (fades in after end_bg, centered x-wise, 10px under end_bg, blinks)
        press_r_png_path = os.path.join(Config.IMAGES_PATH, "press-r.png")
        try:
            self.end_scene_press_r_image = pygame.image.load(press_r_png_path).convert_alpha()
            print(f"Successfully loaded press-r.png: {self.end_scene_press_r_image.get_width()}x{self.end_scene_press_r_image.get_height()}")
        except pygame.error as e:
            print(f"Unable to load press-r PNG: {press_r_png_path}")
            print(f"Error: {e}")
            self.end_scene_press_r_image = None
        
        self.move_back_complete = False  # Track when venusaur and lugia move-back is complete
        
        # Fade-out after screen shake (for Prompt Pulse PNG and black background)
        self.fade_out_after_shake = False  # Track if fade-out should start after screen shake
        self.attack_pulse_end_alpha = 255  # Alpha for attack_pulse_end.png fade-out (starts at 255, fades to 0)
        self.black_block_fade_out_alpha = 255  # Alpha for black background fade-out (starts at 255, fades to 0)
        self.fade_out_timer = 0  # Timer for fade-out animation
        self.fade_out_duration = 500  # 0.5 seconds for fade-out
        
        # Fade-in after attack sequence (for dialog box and fighting background)
        self.fade_in_after_attack = False  # Track if fade-in should start after attack sequence
        self.fade_in_after_attack_alpha = 0  # Alpha for dialog and fighting background fade-in (starts at 0, fades to 255)
        self.fade_in_after_attack_timer = 0  # Timer for fade-in animation
        self.fade_in_after_attack_duration = 500  # 0.5 seconds for fade-in
        
        # Timer for prompt pulse animation (all animations complete in 1 second)
        self.prompt_pulse_animation_timer = 0  # Elapsed time for prompt pulse animations
        self.prompt_pulse_animation_duration = 1000  # 1 second total duration
        
        # Initialize alpha values for battle elements (for fade/slide animations)
        self.battle_grass_alpha = 255
        self.battle_pokemonstat_alpha = 255
        self.battle_water_alpha = 255
        self.battle_lugia_alpha = 255
        self.battle_venu_stat_alpha = 255
        self.battle_background_alpha = 255
        self.battle_dialog_alpha_slide_out = 255
        
        # Bag/Pokemon screen text box settings
        self.screen_text_box_width = 96
        self.screen_text_box_height = 21
        self.screen_text_box_bottom_offset = 22  # 22px from bottom
        self.screen_text_box_right_offset = 8  # 8px from right
        self.screen_text_hovered = False  # Whether text box is hovered
        # Load font for screen text (uses configured font size)
        try:
            font_path = os.path.join(Config.FONTS_PATH, "pokemon_pixel_font.ttf")
            self.screen_text_font = pygame.font.Font(font_path, self.screen_text_font_size)
        except:
            self.screen_text_font = pygame.font.Font(None, self.screen_text_font_size)
        
        # Combat UI grid configuration (2 grids: left and right, each 2x2 = 4 cells each, total 8 cells)
        if self.combat_ui:
            self.combat_ui_padding = 12  # Padding from edge of combat UI image (12px on each side)
            # Left grid: 2x2, 320px wide total (includes 12px padding on each side)
            # Actual grid content area = 320 - (12 * 2) = 296px
            self.combat_ui_left_grid_total_width = 320
            self.combat_ui_left_grid_content_width = self.combat_ui_left_grid_total_width - (self.combat_ui_padding * 2)
            self.combat_ui_left_grid_cols = 2
            self.combat_ui_left_grid_rows = 2
            self.combat_ui_left_cell_width = self.combat_ui_left_grid_content_width // self.combat_ui_left_grid_cols
            self.combat_ui_left_cell_height = (self.combat_ui.get_height() - (self.combat_ui_padding * 2)) // self.combat_ui_left_grid_rows
            
            # Right grid: 2x2, 160px wide total (includes 12px padding on each side)
            # Actual grid content area = 160 - (12 * 2) = 136px
            self.combat_ui_right_grid_total_width = 160
            # Verify padding matches: 12px on each side = 24px total, so content = 160 - 24 = 136px
            self.combat_ui_right_grid_content_width = self.combat_ui_right_grid_total_width - (self.combat_ui_padding * 2)
            # Ensure content width is correct (should be 136px)
            if self.combat_ui_right_grid_content_width != 136:
                print(f"Warning: Right grid content width is {self.combat_ui_right_grid_content_width}, expected 136px")
            self.combat_ui_right_grid_cols = 2
            self.combat_ui_right_grid_rows = 2
            self.combat_ui_right_cell_width = self.combat_ui_right_grid_content_width // self.combat_ui_right_grid_cols
            self.combat_ui_right_cell_height = (self.combat_ui.get_height() - (self.combat_ui_padding * 2)) // self.combat_ui_right_grid_rows
            
            # Store hover state for each grid cell
            self.combat_ui_hovered_cell = None  # ("left"/"right", row, col) or None
        else:
            self.combat_ui_hovered_cell = None
        
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
            # Position directly on top of water (centered horizontally)
            self.battle_lugia_x = Config.SCREEN_WIDTH  # Start off-screen right (same as water)
            # Center Lugia horizontally on water (account for 1.5x scale)
            water_center_x = self.battle_water_target_x + (self.battle_water.get_width() // 2)
            scaled_lugia_width = int(self.battle_lugia.get_width() * 1.5)
            self.battle_lugia_target_x = water_center_x - (scaled_lugia_width // 2)  # Centered on water (accounting for scale)
            # Position Lugia on top of water: bottom of Lugia aligns with bottom of water
            scaled_lugia_height = int(self.battle_lugia.get_height() * 1.5)
            self.battle_lugia_y = self.battle_water_y + self.battle_water.get_height() - scaled_lugia_height
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
        
        # Load prompt pulse charge sprite sheet (88x88px frames)
        prompt_pulse_charge_path = os.path.join(Config.SPRITES_PATH, "prompt_pulse_charge.png")
        self.prompt_pulse_charge_frames = []
        self.prompt_pulse_charge_current_frame = 0
        self.prompt_pulse_charge_animation_time = 0
        try:
            charge_sheet = SpriteSheet(prompt_pulse_charge_path, 88, 88)
            # Extract all frames from the sprite sheet
            for row in range(charge_sheet.rows):
                for col in range(charge_sheet.cols):
                    frame = charge_sheet.get_sprite(row, col)
                    if frame:
                        self.prompt_pulse_charge_frames.append(frame)
            if not self.prompt_pulse_charge_frames:
                print(f"Warning: No frames extracted from prompt pulse charge sprite sheet")
                self.prompt_pulse_charge_frames = []
        except Exception as e:
            print(f"Unable to load prompt pulse charge sprite: {prompt_pulse_charge_path}")
            print(f"Error: {e}")
            self.prompt_pulse_charge_frames = []
        
        # Battle venusaur GIF animation state (slides in from under dialog box)
        if self.battle_venu:
            # Start under dialog box (below screen)
            if self.battle_dialog:
                self.battle_venu_y = Config.SCREEN_HEIGHT  # Start off-screen below
                # Target Y: above dialog, but 30px lower so bottom is partially cut off
                scaled_height = int(self.battle_venu.get_height() * 2.0)  # Account for 2x scale
                self.battle_venu_target_y = Config.SCREEN_HEIGHT - self.battle_dialog.get_height() - scaled_height + 30  # 30px lower
            else:
                self.battle_venu_y = Config.SCREEN_HEIGHT
                self.battle_venu_target_y = Config.SCREEN_HEIGHT - 200
            # Position will be centered on grass (calculated when grass is positioned)
            self.battle_venu_x = 0  # Will be updated when grass is positioned
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
        # Reset player position to a walkable area (cell 15, 11)
        grid_size = 32
        self.player_world_x = 15 * grid_size + grid_size // 2  # Center of cell 15
        self.player_world_y = 11 * grid_size + grid_size // 2   # Center of cell 11
        
        # Reset camera
        self.update_camera()
        
        # Reset movement state
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.current_direction = 1  # Start facing up
        
        # Restore map music when entering the scene
        map_music_path = os.path.join(Config.SOUNDS_PATH, "32 Mt. Moon.mp3")
        try:
            pygame.mixer.music.load(map_music_path)
            pygame.mixer.music.set_volume(self.music_volume)  # Set volume AFTER loading
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            self.battle_music_started = False  # Reset flag so battle music can play again
        except pygame.error as e:
            print(f"Unable to load map music: {map_music_path}")
            print(f"Error: {e}")
        # Reset sound effect flags
        self.exclamation_sound_played = False
        self.trainer_animation_sound_played = False
        self.venusaur_slide_sound_played = False
        
        # Debug: Start at attack sequence if enabled
        if self.debug_start_at_attack_sequence:
            # Set up battle scene state
            self.fade_state = "faded"
            self.fade_alpha = 255
            self.battle_animations_started = True
            self.battle_dialog_visible = True
            self.battle_dialog_alpha = 255
            self.battle_grass_visible = True
            self.battle_pokemonstat_visible = True
            self.battle_water_visible = True
            self.battle_lugia_visible = True
            # Trainer sprite should NOT be visible when debugging starts midway (only shows at start of battle)
            self.battle_trainer_visible = False
            self.battle_venu_stat_visible = True
            self.battle_venu_visible = True
            self.combat_ui_visible = False
            self.lugia_animation_complete = True
            self.dialog_visible = False
            self.dialog_fully_visible = True
            # Position battle elements at their final positions
            if self.battle_grass:
                self.battle_grass_left_x = 0
            if self.battle_pokemonstat:
                self.battle_pokemonstat_x = 0
            if self.battle_water:
                self.battle_water_x = Config.SCREEN_WIDTH - self.battle_water.get_width()
            if self.battle_lugia_visible and self.battle_lugia and self.battle_water:
                scaled_lugia_width = int(self.battle_lugia.get_width() * 1.5)
                water_center_x = self.battle_water_x + (self.battle_water.get_width() // 2)
                self.battle_lugia_x = water_center_x - (scaled_lugia_width // 2)
                scaled_lugia_height = int(self.battle_lugia.get_height() * 1.5)
                self.battle_lugia_y = self.battle_water_y + self.battle_water.get_height() - scaled_lugia_height
            if self.battle_venu_visible and self.battle_venu and self.battle_grass:
                self.battle_venu_y = self.battle_venu_target_y
                grass_center_x = self.battle_grass_left_x + (self.battle_grass.get_width() // 2)
                scaled_venu_width = int(self.battle_venu.get_width() * 2.0)
                self.battle_venu_x = grass_center_x - (scaled_venu_width // 2)
            # Start attack sequence (Prompt Pulse used)
            self.move_used_state = "sliding_down"
            self.move_used_dialog_text = "Cursaur used Prompt Pulse!"
            # Hide fight UI (will stay hidden until game is restarted)
            if self.fight_ui:
                self.fight_ui_alpha = 0
            # Start battle music
            battle_music_path = os.path.join(Config.SOUNDS_PATH, "14 Battle! (Wild Pokémon).mp3")
            try:
                pygame.mixer.music.load(battle_music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.battle_music_started = True
            except pygame.error as e:
                print(f"Unable to load battle music: {battle_music_path}")
                print(f"Error: {e}")
    
    def handle_event(self, event):
        """Handle input for movement"""
        # Handle R key to restart scene
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                # Toggle mute/unmute all audio
                self.audio_muted = not self.audio_muted
                if self.audio_muted:
                    # Mute: set all volumes to 0
                    pygame.mixer.music.set_volume(0.0)
                    # Set all sound effects to 0 volume
                    if self.sfx_collision:
                        self.sfx_collision.set_volume(0.0)
                    if self.sfx_press_ab:
                        self.sfx_press_ab.set_volume(0.0)
                    if self.sfx_ball_toss:
                        self.sfx_ball_toss.set_volume(0.0)
                    if self.sfx_ball_poof:
                        self.sfx_ball_poof.set_volume(0.0)
                    if self.sfx_denied:
                        self.sfx_denied.set_volume(0.0)
                    if self.sfx_cry_17:
                        self.sfx_cry_17.set_volume(0.0)
                    if self.sfx_spore:
                        self.sfx_spore.set_volume(0.0)
                    if self.sfx_spike_cannon:
                        self.sfx_spike_cannon.set_volume(0.0)
                else:
                    # Unmute: restore original volumes
                    pygame.mixer.music.set_volume(self.original_music_volume)
                    # Restore all sound effects volumes
                    if self.sfx_collision:
                        self.sfx_collision.set_volume(self.original_sfx_volume)
                    if self.sfx_press_ab:
                        self.sfx_press_ab.set_volume(self.original_sfx_volume)
                    if self.sfx_ball_toss:
                        self.sfx_ball_toss.set_volume(self.original_sfx_volume)
                    if self.sfx_ball_poof:
                        self.sfx_ball_poof.set_volume(self.original_sfx_volume)
                    if self.sfx_denied:
                        self.sfx_denied.set_volume(self.original_sfx_volume)
                    if self.sfx_cry_17:
                        self.sfx_cry_17.set_volume(self.original_sfx_volume)
                    if self.sfx_spore:
                        self.sfx_spore.set_volume(self.original_sfx_volume)
                    if self.sfx_spike_cannon:
                        self.sfx_spike_cannon.set_volume(self.original_sfx_volume)
            elif event.key == pygame.K_r:
                # Restart the scene from the beginning
                if self.sfx_press_ab:
                    self.sfx_press_ab.play()
                self.on_enter()
                # Reset Lugia state
                self.lugia_state = "hidden"
                self.lugia_y = -200
                self.lugia_current_frame = 0  # Reset to first frame
                self.lugia_cry_played = False  # Reset cry flag so audio can play again
                # Reset move used state
                self.move_used_state = "none"
                self.move_used_ui_slide_y = 0
                self.move_used_dialog_text = ""
                # Reset combat UI
                self.combat_ui_visible = False
                self.lugia_animation_complete = False
                self.dialog_visible = False
                self.dialog_fully_visible = False
                self.dialog_slide_y = Config.SCREEN_HEIGHT
                self.fade_state = "none"
                self.fade_alpha = 0
                # Reset prompt pulse fade out and black background
                self.prompt_pulse_fade_out = False
                self.background_black_alpha = 0
                # Reset prompt pulse animation state
                self.black_block_alpha = 0
                self.battle_slide_out = False
                # Reset fade-out after shake state
                self.fade_out_after_shake = False
                self.attack_pulse_end_alpha = 255
                self.black_block_fade_out_alpha = 255
                self.fade_out_timer = 0
                # Reset fade-in after attack state
                self.fade_in_after_attack = False
                self.fade_in_after_attack_alpha = 0
                self.fade_in_after_attack_timer = 0
                self.prompt_pulse_animation_timer = 0
                self.assets_hidden = False
                self.venusaur_centered = False
                self.prompt_pulse_charge_complete = False
                # Reset prompt pulse charge animation
                self.prompt_pulse_charge_current_frame = 0
                self.prompt_pulse_charge_animation_time = 0
                self.venusaur_original_x = 0
                self.venusaur_original_y = 0
                self.venusaur_move_back = False
                self.venusaur_move_back_timer = 0
                self.lugia_move_back = False
                self.lugia_move_back_timer = 0
                self.battle_lugia_alpha = 255
                self.move_back_complete = False
                # Reset screen shake state
                self.screen_shake_active = False
                self.screen_shake_timer = 0
                self.screen_shake_offset_x = 0
                self.screen_shake_offset_y = 0
                self.lugia_rotation_angle = 0
                self.lugia_slide_in_complete = False
                self.screen_shake_triggered_after_pulse = False
                # Reset lugia position attributes if they exist
                if hasattr(self, 'lugia_black_box_x'):
                    delattr(self, 'lugia_black_box_x')
                if hasattr(self, 'lugia_black_box_y'):
                    delattr(self, 'lugia_black_box_y')
                if hasattr(self, 'lugia_move_back_target_x'):
                    delattr(self, 'lugia_move_back_target_x')
                if hasattr(self, 'lugia_move_back_target_y'):
                    delattr(self, 'lugia_move_back_target_y')
                if hasattr(self, 'lugia_move_back_start_x'):
                    delattr(self, 'lugia_move_back_start_x')
                if hasattr(self, 'lugia_move_back_start_y'):
                    delattr(self, 'lugia_move_back_start_y')
                # Reset lugia position to original (so it can animate again)
                # Reset to target position (where lugia normally is)
                if self.battle_lugia_visible and hasattr(self, 'battle_lugia_target_x'):
                    # Reset x to target (original position)
                    self.battle_lugia_x = Config.SCREEN_WIDTH  # Start off-screen right (so it can slide in again)
                    # Reset y to the position it should be at (on top of water)
                    if self.battle_water and self.battle_lugia:
                        scaled_lugia_height = int(self.battle_lugia.get_height() * 1.5)
                        self.battle_lugia_y = self.battle_water_y + self.battle_water.get_height() - scaled_lugia_height
                    # Reset visibility so it can animate in again
                    self.battle_lugia_visible = False
                # Reset venusaur position attributes if they exist
                if hasattr(self, 'battle_venu_x'):
                    delattr(self, 'battle_venu_x')
                if hasattr(self, 'battle_venu_y'):
                    delattr(self, 'battle_venu_y')
                if hasattr(self, 'battle_venu_start_x'):
                    delattr(self, 'battle_venu_start_x')
                if hasattr(self, 'battle_venu_start_y'):
                    delattr(self, 'battle_venu_start_y')
                if hasattr(self, 'battle_venu_center_target_x'):
                    delattr(self, 'battle_venu_center_target_x')
                if hasattr(self, 'battle_venu_center_target_y'):
                    delattr(self, 'battle_venu_center_target_y')
                
                # Switch back to map music when returning to map
                if self.battle_music_started:
                    map_music_path = os.path.join(Config.SOUNDS_PATH, "32 Mt. Moon.mp3")
                    try:
                        pygame.mixer.music.load(map_music_path)
                        pygame.mixer.music.set_volume(self.music_volume)  # Set volume AFTER loading
                        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                        self.battle_music_started = False  # Reset flag so battle music can play again
                    except pygame.error as e:
                        print(f"Unable to load map music: {map_music_path}")
                        print(f"Error: {e}")
                # Reset sound effect flags when restarting
                self.exclamation_sound_played = False
                self.trainer_animation_sound_played = False
                self.venusaur_slide_sound_played = False
                self.spore_sound_played = False
                self.spike_cannon_sound_played = False
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
                # Reset fight UI
                if self.fight_ui:
                    self.fight_ui_alpha = 0
                    self.fight_ui_hovered_cell = None
                    self.fight_ui_selected_cell = None
                # Reset screen state
                self.current_screen = "battle"
                self.run_text_visible = False
                self.run_text_alpha = 0
                self.combat_ui_visible = False
                if self.combat_ui:
                    self.combat_ui_hovered_cell = None
                # Reset dialog pause timer
                self.dialog_pause_start_time = None
                # Reset end scene animation state (fully restart everything)
                self.end_scene_active = False
                self.end_scene_health_bar_timer = 0
                self.end_scene_health_bar_width = 96
                self.end_scene_health_bar_pause_timer = 0
                self.end_scene_health_bar_cry_played = False
                self.end_scene_lugia_fall_timer = 0
                self.end_scene_lugia_fall_alpha = 255
                self.end_scene_fainted_text_active = False
                self.end_scene_fainted_text_timer = 0
                self.end_scene_black_bg_delay_timer = 0
                self.end_scene_black_bg_active = False
                self.end_scene_black_bg_alpha = 0
                self.end_scene_black_bg_timer = 0
                self.end_scene_elements_fade_alpha = 255
                self.end_scene_music_played = False
                self.end_scene_venusaur_active = False
                self.end_scene_venusaur_fade_timer = 0
                self.end_scene_venusaur_fade_alpha = 0
                self.end_scene_venusaur_slide_timer = 0
                self.end_scene_pokemon_shine_active = False
                self.end_scene_pokemon_shine_fade_timer = 0
                self.end_scene_pokemon_shine_fade_alpha = 0
                self.end_scene_pokemon_shine_current_frame = 0
                self.end_scene_pokemon_shine_animation_time = 0
                self.end_scene_bg_active = False
                self.end_scene_bg_slide_timer = 0
                self.end_scene_bg_x = 0
                self.end_scene_bg_y = 0
                self.end_scene_cursor_active = False
                self.end_scene_cursor_fade_timer = 0
                self.end_scene_cursor_fade_alpha = 0
                self.end_scene_cursor_x = 0
                self.end_scene_cursor_y = 0
                self.end_scene_press_r_active = False
                self.end_scene_press_r_fade_timer = 0
                self.end_scene_press_r_fade_alpha = 0
                self.end_scene_press_r_blink_timer = 0
                self.end_scene_press_r_blink_alpha = 255
                self.end_scene_press_r_fade_complete = False
                self.end_scene_press_r_x = 0
                self.end_scene_press_r_y = 0
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
        
        # Handle bag/pokemon screen text box hover detection
        if event.type == pygame.MOUSEMOTION and self.fade_state == "faded":
            mouse_x, mouse_y = event.pos
            if self.current_screen in ["bag", "pokemon"]:
                # Calculate text box position (22px from bottom, 8px from right)
                text_box_x = Config.SCREEN_WIDTH - self.screen_text_box_right_offset - self.screen_text_box_width
                text_box_y = Config.SCREEN_HEIGHT - self.screen_text_box_bottom_offset - self.screen_text_box_height
                
                # Check if mouse is over text box
                if (text_box_x <= mouse_x <= text_box_x + self.screen_text_box_width and
                    text_box_y <= mouse_y <= text_box_y + self.screen_text_box_height):
                    self.screen_text_hovered = True
                else:
                    self.screen_text_hovered = False
            else:
                self.screen_text_hovered = False
        
        # Handle combat UI hover detection (only when combat UI is visible)
        if event.type == pygame.MOUSEMOTION and self.combat_ui_visible and self.combat_ui and self.fade_state == "faded":
            mouse_x, mouse_y = event.pos
            combat_ui_x = 0
            combat_ui_y = Config.SCREEN_HEIGHT - self.combat_ui.get_height()
            
            # Check if mouse is over combat UI
            if (combat_ui_x <= mouse_x <= combat_ui_x + self.combat_ui.get_width() and
                combat_ui_y <= mouse_y <= combat_ui_y + self.combat_ui.get_height()):
                
                # Check left grid (320px total width including 12px padding on each side)
                left_grid_x = combat_ui_x + self.combat_ui_padding
                left_grid_y = combat_ui_y + self.combat_ui_padding
                if (left_grid_x <= mouse_x <= left_grid_x + self.combat_ui_left_grid_content_width and
                    left_grid_y <= mouse_y <= left_grid_y + (self.combat_ui_left_grid_rows * self.combat_ui_left_cell_height)):
                    relative_x = mouse_x - left_grid_x
                    relative_y = mouse_y - left_grid_y
                    col = int(relative_x // self.combat_ui_left_cell_width)
                    row = int(relative_y // self.combat_ui_left_cell_height)
                    col = max(0, min(col, self.combat_ui_left_grid_cols - 1))
                    row = max(0, min(row, self.combat_ui_left_grid_rows - 1))
                    self.combat_ui_hovered_cell = ("left", row, col)
                # Right grid has no hover - it only displays info based on left grid hover
                else:
                    self.combat_ui_hovered_cell = None
            else:
                self.combat_ui_hovered_cell = None
        
        # Handle fight UI hover detection (only when battle is active and UI is visible, and not sliding out)
        if event.type == pygame.MOUSEMOTION and self.fight_ui and self.fade_state == "faded" and not self.combat_ui_visible and self.move_used_state == "none":
            mouse_x, mouse_y = event.pos
            # Check if mouse is over fight UI
            if (self.fight_ui_x <= mouse_x <= self.fight_ui_x + self.fight_ui.get_width() and
                self.fight_ui_y <= mouse_y <= self.fight_ui_y + self.fight_ui.get_height()):
                # Calculate which cell the mouse is over (accounting for padding)
                relative_x = mouse_x - self.fight_ui_x - self.fight_ui_padding
                relative_y = mouse_y - self.fight_ui_y - self.fight_ui_padding
                # Check if within usable area (excluding padding)
                if (0 <= relative_x < self.fight_ui.get_width() - (self.fight_ui_padding * 2) and
                    0 <= relative_y < self.fight_ui.get_height() - (self.fight_ui_padding * 2)):
                    # Determine which cell (row, col)
                    col = int(relative_x // self.fight_ui_cell_width)
                    row = int(relative_y // self.fight_ui_cell_height)
                    # Clamp to valid range
                    col = max(0, min(col, self.fight_ui_grid_cols - 1))
                    row = max(0, min(row, self.fight_ui_grid_rows - 1))
                    self.fight_ui_hovered_cell = (row, col)
                else:
                    self.fight_ui_hovered_cell = None
            else:
                self.fight_ui_hovered_cell = None
        
        # Handle fight UI button clicks (only when battle is active)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # First check if clicking to dismiss "You can't run away!" or "Your Cursorsaur already has full HP!" text
            if self.run_text_visible:
                # Click anywhere to dismiss (no sound)
                self.run_text_visible = False
                self.fight_ui_selected_cell = None  # Remove highlight when text is dismissed
                return  # Don't process other clicks
            if self.full_hp_text_visible:
                # Click anywhere to dismiss (no sound)
                self.full_hp_text_visible = False
                self.fight_ui_selected_cell = None  # Remove highlight when text is dismissed
                return  # Don't process other clicks
            
            # Check if clicking on combat UI left grid (move selection)
            if self.combat_ui_visible and self.combat_ui and self.fade_state == "faded":
                combat_ui_x = 0  # At bottom, full width
                combat_ui_y = Config.SCREEN_HEIGHT - self.combat_ui.get_height()
                # Check left grid (320px total width including 12px padding on each side)
                left_grid_x = combat_ui_x + self.combat_ui_padding
                left_grid_y = combat_ui_y + self.combat_ui_padding
                if (left_grid_x <= mouse_x <= left_grid_x + self.combat_ui_left_grid_content_width and
                    left_grid_y <= mouse_y <= left_grid_y + (self.combat_ui_left_grid_rows * self.combat_ui_left_cell_height)):
                    relative_x = mouse_x - left_grid_x
                    relative_y = mouse_y - left_grid_y
                    col = int(relative_x // self.combat_ui_left_cell_width)
                    row = int(relative_y // self.combat_ui_left_cell_height)
                    col = max(0, min(col, self.combat_ui_left_grid_cols - 1))
                    row = max(0, min(row, self.combat_ui_left_grid_rows - 1))
                    move_index = row * self.combat_ui_left_grid_cols + col
                    if move_index < len(self.combat_ui_move_labels):
                        move_name = self.combat_ui_move_labels[move_index]
                        # Play denied sound for greyed out moves, press AB for Prompt Pulse
                        if move_name in ["Context Recall", "Syntax Slash", "Debug Dash"]:
                            # Greyed out moves - play denied sound
                            if self.sfx_denied:
                                self.sfx_denied.play()
                        else:
                            # Prompt Pulse - play press AB sound
                            if self.sfx_press_ab:
                                self.sfx_press_ab.play()
                        # Handle Prompt Pulse click
                        if move_name == "Prompt Pulse":
                            # Start move used sequence - slide UI down and show dialog
                            self.move_used_state = "sliding_down"  # Start sliding UI down
                            self.move_used_ui_slide_y = 0  # Start at current position
                            self.move_used_dialog_text = "Cursaur used Prompt Pulse!"
                            # Hide combat UI
                            self.combat_ui_visible = False
                            # Hide fight UI (will stay hidden until game is restarted)
                            if self.fight_ui:
                                self.fight_ui_alpha = 0
                            return  # Don't process other clicks
                # Check if clicking outside combat UI (hide it)
                if not (combat_ui_x <= mouse_x <= combat_ui_x + self.combat_ui.get_width() and
                        combat_ui_y <= mouse_y <= combat_ui_y + self.combat_ui.get_height()):
                    # Clicked outside combat UI, hide it
                    # Play click sound for closing combat UI
                    if self.sfx_press_ab:
                        self.sfx_press_ab.play()
                    self.combat_ui_visible = False
                    return  # Don't process other clicks
            
            # Then check if clicking on bag/pokemon screen
            if self.fade_state == "faded" and self.current_screen in ["bag", "pokemon"]:
                # Calculate text box position
                text_box_x = Config.SCREEN_WIDTH - self.screen_text_box_right_offset - self.screen_text_box_width
                text_box_y = Config.SCREEN_HEIGHT - self.screen_text_box_bottom_offset - self.screen_text_box_height
                # Check if clicking on the text box (USE button)
                clicking_on_text_box = (text_box_x <= mouse_x <= text_box_x + self.screen_text_box_width and
                                        text_box_y <= mouse_y <= text_box_y + self.screen_text_box_height)
                
                if self.current_screen == "bag":
                    if clicking_on_text_box:
                        # Clicking on USE button - show "Your Cursorsaur already has full HP!" text - play denied sound
                        if self.sfx_denied:
                            self.sfx_denied.play()
                        self.full_hp_text_visible = True
                        self.full_hp_text_alpha = 255  # Show immediately at full opacity
                        # Hide bag bg img and return to battle scene
                        self.current_screen = "battle"
                        # Keep BAG cell highlighted (find BAG button position)
                        for row in range(self.fight_ui_grid_rows):
                            for col in range(self.fight_ui_grid_cols):
                                button_index = row * self.fight_ui_grid_cols + col
                                if button_index < len(self.fight_ui_labels):
                                    if self.fight_ui_labels[button_index] == "BAG":
                                        self.fight_ui_selected_cell = (row, col)
                                        break
                        return  # Don't process other clicks
                    else:
                        # Clicking anywhere outside USE button - return to battle
                        if self.sfx_press_ab:
                            self.sfx_press_ab.play()
                        self.current_screen = "battle"
                        return  # Don't process other clicks
                else:
                    # Pokemon screen - clicking anywhere returns to battle
                    if clicking_on_text_box:
                        # Clicking on text box - play press AB sound
                        if self.sfx_press_ab:
                            self.sfx_press_ab.play()
                    self.current_screen = "battle"
                    return  # Don't process other clicks
            
            # Then check if clicking on fight UI buttons
            # Disable buttons when combat UI (moves dialog) is visible or when sliding out
            if self.fight_ui and self.fade_state == "faded" and self.current_screen == "battle" and not self.combat_ui_visible and self.move_used_state == "none":
                # Check if click is over fight UI
                if (self.fight_ui_x <= mouse_x <= self.fight_ui_x + self.fight_ui.get_width() and
                    self.fight_ui_y <= mouse_y <= self.fight_ui_y + self.fight_ui.get_height()):
                    # Calculate which cell was clicked (accounting for padding)
                    relative_x = mouse_x - self.fight_ui_x - self.fight_ui_padding
                    relative_y = mouse_y - self.fight_ui_y - self.fight_ui_padding
                    # Check if within usable area (excluding padding)
                    if (0 <= relative_x < self.fight_ui.get_width() - (self.fight_ui_padding * 2) and
                        0 <= relative_y < self.fight_ui.get_height() - (self.fight_ui_padding * 2)):
                        # Determine which cell (row, col)
                        col = int(relative_x // self.fight_ui_cell_width)
                        row = int(relative_y // self.fight_ui_cell_height)
                        # Clamp to valid range
                        col = max(0, min(col, self.fight_ui_grid_cols - 1))
                        row = max(0, min(row, self.fight_ui_grid_rows - 1))
                        # Calculate button index (top-left=0, top-right=1, bottom-left=2, bottom-right=3)
                        button_index = row * self.fight_ui_grid_cols + col
                        
                        if button_index < len(self.fight_ui_labels):
                            button_label = self.fight_ui_labels[button_index]
                            
                            if button_label == "BAG":
                                # Show bag screen - play press AB sound
                                if self.sfx_press_ab:
                                    self.sfx_press_ab.play()
                                if self.bag_screen:
                                    self.current_screen = "bag"
                                    # Keep BAG cell highlighted
                                    self.fight_ui_selected_cell = (row, col)
                            elif button_label == "POKEMON":
                                # Show pokemon screen
                                if self.sfx_press_ab:
                                    self.sfx_press_ab.play()
                                if self.pokemon_screen:
                                    self.current_screen = "pokemon"
                                    # Keep POKEMON cell highlighted
                                    self.fight_ui_selected_cell = (row, col)
                            elif button_label == "FIGHT":
                                # Show combat UI
                                if self.sfx_press_ab:
                                    self.sfx_press_ab.play()
                                if self.combat_ui:
                                    self.combat_ui_visible = True
                            elif button_label == "RUN":
                                # Show "You can't run away!" text with fade in - play denied sound
                                if self.sfx_denied:
                                    self.sfx_denied.play()
                                if self.current_screen == "battle":
                                    self.run_text_visible = True
                                    self.run_text_alpha = 255  # Show immediately at full opacity
                                    # Keep RUN cell highlighted
                                    self.fight_ui_selected_cell = (row, col)
        
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
        # Ensure map music is playing when not in battle (safety check)
        if self.fade_state == "none" and self.battle_music_started:
            # We're back on the map but battle music is still playing - switch back
            map_music_path = os.path.join(Config.SOUNDS_PATH, "32 Mt. Moon.mp3")
            try:
                pygame.mixer.music.load(map_music_path)
                pygame.mixer.music.set_volume(self.music_volume)  # Set volume AFTER loading
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                self.battle_music_started = False  # Reset flag
            except pygame.error as e:
                print(f"Unable to load map music: {map_music_path}")
                print(f"Error: {e}")
        
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
            # Grid/cells are 32x32
            grid_size = 32
            
            # Helper function to check if a cell is walkable
            def is_cell_walkable_check(cell_x, cell_y):
                # Check rectangles
                for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                    if min_x <= cell_x <= max_x and min_y <= cell_y <= max_y:
                        return True
                # Check individual cells
                for cell_x_check, cell_y_check in self.walkable_cells:
                    if cell_x == cell_x_check and cell_y == cell_y_check:
                        return True
                return False
            
            # Check current position (before movement)
            current_center_x = self.player_world_x + self.player_width // 2
            current_center_y = self.player_world_y + self.player_height // 2
            current_cell_x = current_center_x // grid_size
            current_cell_y = current_center_y // grid_size
            
            # Calculate new position
            new_x = self.player_world_x + dx
            new_y = self.player_world_y + dy
            
            # Keep player within map bounds (with some margin for character size)
            margin = 10
            new_x = max(margin, min(new_x, self.map_width - self.player_width - margin))
            new_y = max(margin, min(new_y, self.map_height - self.player_height - margin))
            
            # Check if the new position is in a walkable area
            player_center_x = new_x + self.player_width // 2
            player_center_y = new_y + self.player_height // 2
            player_cell_x = player_center_x // grid_size
            player_cell_y = player_center_y // grid_size
            
            # Check if current cell is walkable and new cell is not walkable - play collision sound
            current_is_walkable = is_cell_walkable_check(current_cell_x, current_cell_y)
            new_is_walkable = is_cell_walkable_check(player_cell_x, player_cell_y)
            
            if current_is_walkable and not new_is_walkable:
                # Player is on walkable cell at edge, trying to move to non-walkable cell
                if self.sfx_collision:
                    self.sfx_collision.play()
            
            # Check if player is in a walkable cell
            is_walkable = new_is_walkable
            
            # Only update position if in a walkable area
            if is_walkable:
                # Helper function to check if a cell is walkable (for edge detection)
                def is_cell_walkable_for_edge(cell_x, cell_y):
                    # Check rectangles
                    for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                        if min_x <= cell_x <= max_x and min_y <= cell_y <= max_y:
                            return True
                    # Check individual cells
                    for cell_x_check, cell_y_check in self.walkable_cells:
                        if cell_x == cell_x_check and cell_y == cell_y_check:
                            return True
                    return False
                
                # Check if current cell is an edge (has at least one non-walkable neighbor)
                is_edge = False
                neighbors = [
                    (player_cell_x, player_cell_y - 1),  # Up
                    (player_cell_x, player_cell_y + 1),  # Down
                    (player_cell_x - 1, player_cell_y),  # Left
                    (player_cell_x + 1, player_cell_y),  # Right
                ]
                for nx, ny in neighbors:
                    if not is_cell_walkable_for_edge(nx, ny):
                        is_edge = True
                        break
                
                # Individual cells are always edges
                if (player_cell_x, player_cell_y) in self.walkable_cells:
                    is_edge = True
                
                # Play collision sound only when:
                # 1. Walking on edge cells (yellow squares)
                # 2. AND moving towards a direction that does not have a pink square (non-walkable)
                if is_edge and self.sfx_collision and not self.collision_sound_playing:
                    # Check the direction we're moving towards
                    direction_cell_x = player_cell_x
                    direction_cell_y = player_cell_y
                    
                    # Determine which direction we're moving
                    if dx > 0:  # Moving right
                        direction_cell_x = player_cell_x + 1
                    elif dx < 0:  # Moving left
                        direction_cell_x = player_cell_x - 1
                    if dy > 0:  # Moving down
                        direction_cell_y = player_cell_y + 1
                    elif dy < 0:  # Moving up
                        direction_cell_y = player_cell_y - 1
                    
                    # Check if the direction cell is non-walkable (no pink square)
                    direction_is_walkable = is_cell_walkable_for_edge(direction_cell_x, direction_cell_y)
                    
                    # Only play sound if moving towards a non-walkable cell
                    if not direction_is_walkable:
                        self.sfx_collision.play()
                        self.collision_sound_playing = True
                        # Reset flag when sound finishes (approximate duration check)
                        # We'll reset it in update() after checking if sound is still playing
                
                # Helper function to check if a cell is walkable
                def is_cell_walkable(cell_x, cell_y):
                    # Check rectangles
                    for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                        if min_x <= cell_x <= max_x and min_y <= cell_y <= max_y:
                            return True
                    # Check individual cells
                    for cell_x_check, cell_y_check in self.walkable_cells:
                        if cell_x == cell_x_check and cell_y == cell_y_check:
                            return True
                    return False
                
                # Constrain sprite to stay within cell boundaries ONLY at walkable area edges
                # Get sprite dimensions (accounting for centering)
                current_sprite = self.character_sprite.get_current_sprite() if self.character_sprite else None
                if current_sprite:
                    sprite_width = current_sprite.get_width()
                    sprite_height = current_sprite.get_height()
                    # Calculate sprite position (centered horizontally relative to player position)
                    sprite_left = new_x - (sprite_width - self.player_width) // 2
                    sprite_right = sprite_left + sprite_width
                    sprite_top = new_y
                    sprite_bottom = new_y + sprite_height
                    
                    # Get the cell boundaries for the cell the player center is in
                    cell_left = player_cell_x * grid_size
                    cell_right = (player_cell_x + 1) * grid_size
                    cell_top = player_cell_y * grid_size
                    cell_bottom = (player_cell_y + 1) * grid_size
                    
                    # Check adjacent cells to see if edges should be constrained
                    # Left edge: constrain only if left cell is not walkable
                    if sprite_left < cell_left:
                        left_cell_x = player_cell_x - 1
                        if not is_cell_walkable(left_cell_x, player_cell_y):
                            new_x += (cell_left - sprite_left)
                    
                    # Right edge: constrain only if right cell is not walkable
                    if sprite_right > cell_right:
                        right_cell_x = player_cell_x + 1
                        if not is_cell_walkable(right_cell_x, player_cell_y):
                            new_x -= (sprite_right - cell_right)
                    
                    # Top edge: constrain only if top cell is not walkable
                    if sprite_top < cell_top:
                        top_cell_y = player_cell_y - 1
                        if not is_cell_walkable(player_cell_x, top_cell_y):
                            new_y += (cell_top - sprite_top)
                    
                    # Bottom edge: constrain only if bottom cell is not walkable
                    if sprite_bottom > cell_bottom:
                        bottom_cell_y = player_cell_y + 1
                        if not is_cell_walkable(player_cell_x, bottom_cell_y):
                            new_y -= (sprite_bottom - cell_bottom)
                    
                    # Re-check if the constrained position is still in a walkable cell
                    constrained_center_x = new_x + self.player_width // 2
                    constrained_center_y = new_y + self.player_height // 2
                    constrained_cell_x = constrained_center_x // grid_size
                    constrained_cell_y = constrained_center_y // grid_size
                    
                    # Check if constrained position is still walkable
                    if is_cell_walkable(constrained_cell_x, constrained_cell_y):
                        self.player_world_x = new_x
                        self.player_world_y = new_y
                else:
                    # No sprite, just update position
                    self.player_world_x = new_x
                    self.player_world_y = new_y
                # Fallback: constrain player position to cell boundaries only at walkable area edges
                    def is_cell_walkable_fallback(cell_x, cell_y):
                        for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                            if min_x <= cell_x <= max_x and min_y <= cell_y <= max_y:
                                return True
                        for cell_x_check, cell_y_check in self.walkable_cells:
                            if cell_x == cell_x_check and cell_y == cell_y_check:
                                return True
                        return False
                    
                    cell_left = player_cell_x * grid_size
                    cell_right = (player_cell_x + 1) * grid_size
                    cell_top = player_cell_y * grid_size
                    cell_bottom = (player_cell_y + 1) * grid_size
                    
                    # Only constrain at edges where adjacent cell is not walkable
                    if new_x < cell_left and not is_cell_walkable_fallback(player_cell_x - 1, player_cell_y):
                        new_x = max(cell_left, new_x)
                    if new_x + self.player_width > cell_right and not is_cell_walkable_fallback(player_cell_x + 1, player_cell_y):
                        new_x = min(cell_right - self.player_width, new_x)
                    if new_y < cell_top and not is_cell_walkable_fallback(player_cell_x, player_cell_y - 1):
                        new_y = max(cell_top, new_y)
                    if new_y + self.player_height > cell_bottom and not is_cell_walkable_fallback(player_cell_x, player_cell_y + 1):
                        new_y = min(cell_bottom - self.player_height, new_y)
                    
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
        
        # Update exclamation animation
        if self.exclamation_visible and self.exclamation_image:
            current_time = pygame.time.get_ticks()
            if self.exclamation_state == "sliding_up":
                # Slide up to target position
                if self.exclamation_y > self.exclamation_target_y:
                    self.exclamation_y -= self.exclamation_slide_speed
                    if self.exclamation_y <= self.exclamation_target_y:
                        self.exclamation_y = self.exclamation_target_y
                        self.exclamation_state = "showing"
                        self.exclamation_show_time = current_time
                else:
                    self.exclamation_state = "showing"
                    self.exclamation_show_time = current_time
            elif self.exclamation_state == "showing":
                # Show for brief moment
                if current_time - self.exclamation_show_time >= self.exclamation_show_duration:
                    self.exclamation_state = "sliding_down"
            elif self.exclamation_state == "sliding_down":
                # Slide down and fade out
                self.exclamation_y += self.exclamation_slide_speed
                self.exclamation_alpha = max(0, self.exclamation_alpha - self.exclamation_fade_speed)
                if self.exclamation_alpha <= 0:
                    self.exclamation_visible = False
                    self.exclamation_state = "hidden"
        
        # Update Lugia state machine
        if self.lugia_state == "hidden" and under_lugia:
            # Player reached bridge end - start Lugia flying in
            self.lugia_state = "flying_in"
            # Start exclamation animation
            if self.exclamation_image:
                # Position exclamation centered above character red image (not cell)
                player_center_x = self.player_world_x + (self.player_width // 2)
                player_top_y = self.player_world_y
                # Start one cell below character top, slide up one cell
                self.exclamation_x = player_center_x - (self.exclamation_image.get_width() // 2)  # Centered on character
                self.exclamation_y = player_top_y + grid_size  # Start one cell below character top
                self.exclamation_target_y = player_top_y - grid_size  # Target is one cell above character top
                self.exclamation_visible = True
                self.exclamation_state = "sliding_up"
                self.exclamation_alpha = 255
                self.exclamation_show_time = 0
                # Play exclamation sound when it starts sliding up
                if self.sfx_press_ab and not self.exclamation_sound_played:
                    self.sfx_press_ab.play()
                    self.exclamation_sound_played = True
        
        elif self.lugia_state == "flying_in":
            # Move Lugia down and slightly left (from right) towards target position
            if self.lugia_y < self.lugia_target_y:
                self.lugia_y += self.lugia_fly_speed
                # Move horizontally from right to target (smooth diagonal movement)
                if self.lugia_x > self.lugia_target_x:
                    # Calculate horizontal movement based on vertical progress
                    vertical_progress = (self.lugia_target_y - self.lugia_y) / (self.lugia_target_y - (-200))
                    horizontal_distance = self.lugia_start_x - self.lugia_target_x
                    self.lugia_x = self.lugia_start_x - (horizontal_distance * (1 - vertical_progress))
                else:
                    self.lugia_x = self.lugia_target_x
            else:
                # Reached target position - start animation
                self.lugia_y = self.lugia_target_y
                self.lugia_x = self.lugia_target_x
                self.lugia_state = "animating"
                self.lugia_current_frame = 0  # Start from first frame
        
        elif self.lugia_state == "animating":
            # Play animation once end to end
            if len(self.lugia_sprites) > 0:
                # Check if we're on the second-to-last frame
                second_to_last_frame = len(self.lugia_sprites) - 2
                if self.lugia_current_frame == second_to_last_frame:
                    # Hold second-to-last frame longer (slower animation speed)
                    hold_speed = self.lugia_animation_speed * 0.3  # Much slower
                    self.lugia_animation_time += hold_speed
                else:
                    # Normal animation speed for other frames
                    self.lugia_animation_time += self.lugia_animation_speed
                
                if self.lugia_animation_time >= 1.0:
                    self.lugia_animation_time = 0
                    self.lugia_current_frame += 1
                    
                    # Check if animation completed (reached last frame)
                    if self.lugia_current_frame >= len(self.lugia_sprites):
                        # End at last frame of sprite sheet (not first frame)
                        self.lugia_current_frame = len(self.lugia_sprites) - 1
                        self.lugia_state = "stopped"
                        self.lugia_animation_complete = True
                        # Start showing dialog when animation completes
                        self.dialog_visible = True
                        self.dialog_fully_visible = False
                        # Start dialog at bottom of screen
                        self.dialog_slide_y = Config.SCREEN_HEIGHT
                        # Set dialog text (you can customize this)
                        self.dialog_text = "Bugia wants to battle!"
                
                # Play cry sound when Lugia reaches last frame
                if self.lugia_current_frame == len(self.lugia_sprites) - 1 and not self.lugia_cry_played:
                    if self.sfx_cry_17:
                        self.sfx_cry_17.play()
                        self.lugia_cry_played = True
        
        elif self.lugia_state == "stopped":
            # Animation complete - stay on last frame, dialog will show
            if len(self.lugia_sprites) > 0:
                self.lugia_current_frame = len(self.lugia_sprites) - 1
                # Play cry sound when on last frame (if not already played)
                if not self.lugia_cry_played:
                    if self.sfx_cry_17:
                        self.sfx_cry_17.play()
                        self.lugia_cry_played = True
        
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
                    if self.lugia_animation_complete and self.fade_state == "none" and self.dialog_pause_start_time is None:
                        self.dialog_pause_start_time = pygame.time.get_ticks()  # Record start time
            else:
                self.dialog_fully_visible = True
                # Start pause timer when dialog becomes fully visible
                if self.lugia_animation_complete and self.fade_state == "none" and self.dialog_pause_start_time is None:
                    self.dialog_pause_start_time = pygame.time.get_ticks()  # Record start time
            
            # Check if 2 seconds have passed and start fade
            if self.dialog_pause_start_time is not None:
                elapsed_time = pygame.time.get_ticks() - self.dialog_pause_start_time
                if elapsed_time >= self.dialog_pause_duration:
                    # 2 seconds have passed, start fade
                    if self.fighting_background and self.fade_state == "none":
                        self.fade_state = "fading"
                        self.fade_alpha = 0
                        self.dialog_pause_start_time = None  # Reset timer
        
        # Handle fade transition to fighting background
        if self.fade_state == "fading":
            # Start battle music when map starts fading away
            if not self.battle_music_started:
                battle_music_path = os.path.join(Config.SOUNDS_PATH, "14 Battle! (Wild Pokémon).mp3")
                try:
                    print(f"Loading battle music: {battle_music_path}")
                    pygame.mixer.music.load(battle_music_path)
                    pygame.mixer.music.set_volume(self.music_volume)  # Set volume AFTER loading
                    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                    self.battle_music_started = True
                    print(f"Battle music started playing")
                except pygame.error as e:
                    print(f"Unable to load battle music: {battle_music_path}")
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error loading battle music: {e}")
            
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_state = "faded"
                self.fade_complete = True
                # Reset Lugia sprite to starting frame when battle fades in
                if hasattr(self, 'battle_lugia_frames') and self.battle_lugia_frames:
                    self.battle_lugia_current_frame = 0
                    self.battle_lugia_animation_time = 0
                    # Set initial frame
                    if len(self.battle_lugia_frames) > 0:
                        self.battle_lugia = self.battle_lugia_frames[0]
                # Start battle slide animations when fade is complete
                # This is the INITIAL battle scene (BEFORE prompt pulse is used)
                # All elements should slide in and remain visible before prompt pulse:
                # - Grass: slides in from left
                # - Lugia stat container (pokemonstat): slides in from left
                # - Water: slides in from right
                # - Lugia GIF: slides in from right with water
                # - Battle trainer sprite: slides in from right, animates, then slides out
                # - Venusaur stat container (venu_stat): always visible, no sliding
                # - Venusaur GIF: becomes visible after trainer animation completes, slides in from under dialog
                # - Fight UI: fades in with Venusaur text
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
                    # Note: battle_venu_visible is set to True later when trainer animation completes
                    # (see line ~2148 where trainer reaches last frame)
        
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
            # Only slide in if not in sliding_out state (sliding_out is handled in move_used_state handler)
            
            if self.move_used_state == "none":
                # Battle grass: fly in from left (with calculated speed)
                # Grass should remain in place during prompt pulse attack (move_used_state != "none")
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
                            # Lugia finished sliding in
                            if not self.lugia_slide_in_complete:
                                self.lugia_slide_in_complete = True
                
                # Battle trainer: slide in from right, same location as grass but higher z-index (with calculated speed)
                if self.battle_trainer_visible and self.battle_trainer_sprites:
                    if self.battle_trainer_x > self.battle_trainer_target_x:
                        self.battle_trainer_x -= self.battle_trainer_speed
                        if self.battle_trainer_x <= self.battle_trainer_target_x:
                            self.battle_trainer_x = self.battle_trainer_target_x
            else:
                # During prompt pulse attack (move_used_state != "none"), keep all elements in place
                # Ensure grass stays at target position and remains visible
                if self.battle_grass_visible and self.battle_grass:
                    self.battle_grass_left_x = self.battle_grass_left_target_x  # Lock position
                # Lock other element positions during prompt pulse
                if self.battle_pokemonstat_visible and self.battle_pokemonstat:
                    if hasattr(self, 'battle_pokemonstat_target_x'):
                        self.battle_pokemonstat_x = self.battle_pokemonstat_target_x
                if self.battle_water_visible and self.battle_water:
                    if hasattr(self, 'battle_water_target_x'):
                        self.battle_water_x = self.battle_water_target_x
                if self.battle_lugia_visible and self.battle_lugia:
                    # Don't move lugia during black box fade (it stays in place during fade)
                    if self.move_used_state != "fading_black":
                        if hasattr(self, 'battle_lugia_target_x'):
                            self.battle_lugia_x = self.battle_lugia_target_x
                if self.battle_trainer_visible and self.battle_trainer_sprites:
                    if hasattr(self, 'battle_trainer_target_x'):
                        self.battle_trainer_x = self.battle_trainer_target_x
            
            # Animate Lugia GIF (always animate, never stops)
            if self.battle_lugia_visible and self.battle_lugia and self.battle_lugia_frames:
                if len(self.battle_lugia_frames) > 1:
                    self.battle_lugia_animation_time += self.battle_lugia_animation_speed
                    if self.battle_lugia_animation_time >= 1.0:
                        self.battle_lugia_animation_time = 0
                        self.battle_lugia_current_frame = (self.battle_lugia_current_frame + 1) % len(self.battle_lugia_frames)
                        self.battle_lugia = self.battle_lugia_frames[self.battle_lugia_current_frame]
            
            # Check if all slide animations are complete before animating trainer sprite
            # Only check if not in sliding_out state
            if self.battle_trainer_visible and self.battle_trainer_sprites:
                all_animations_complete = True
                if self.move_used_state == "none":
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
                else:
                    # In sliding_out state, don't animate trainer
                    all_animations_complete = False
                
                # Enable trainer sprite animation only when all slide animations are done
                if all_animations_complete and not self.battle_trainer_can_animate:
                    # This is the first frame when animations complete
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
                            # Play ball toss sound when trainer reaches 2nd sprite (frame index 1)
                            if self.battle_trainer_current_frame == 1 and self.sfx_ball_toss and not self.trainer_animation_sound_played:
                                self.sfx_ball_toss.play()
                                self.trainer_animation_sound_played = True
                        else:
                            # Reached last frame - start venusaur GIF slide in, then slide out
                            # Start venusaur GIF sliding in from under dialog (before trainer fades)
                            self.battle_venu_visible = True
                            # Initialize Venusaur text fade (will be controlled by slide progress)
                            self.battle_text_venusaur_alpha = 0
                            self.battle_text_lugia_alpha = 255
                            # Initialize fight UI fade (will fade in with Venusaur text)
                            if self.fight_ui:
                                self.fight_ui_alpha = 0
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
            # Don't move during prompt pulse animation (stays in place)
            if self.battle_venu_visible and self.battle_venu and self.battle_venu_frames:
                # Check if we need to move venusaur back to original position (after charge animation completes)
                if hasattr(self, 'venusaur_move_back') and self.venusaur_move_back and self.move_used_state == "none":
                    # Smooth move-back animation with ease-in-out
                    self.venusaur_move_back_timer += self.game.clock.get_time()
                    move_back_progress = min(1.0, self.venusaur_move_back_timer / self.venusaur_move_back_duration)
                    # Ease-in-out function for smooth animation
                    def ease_in_out(t):
                        return t * t * (3.0 - 2.0 * t)
                    eased_progress = ease_in_out(move_back_progress)
                    
                    if hasattr(self, 'venusaur_move_back_start_y') and hasattr(self, 'venusaur_original_y'):
                        # Interpolate Y position smoothly
                        start_y = self.venusaur_move_back_start_y
                        target_y = self.venusaur_original_y
                        self.battle_venu_y = start_y + (target_y - start_y) * eased_progress
                    
                    if move_back_progress >= 1.0:
                        # Move-back complete
                        if hasattr(self, 'venusaur_original_y'):
                            self.battle_venu_y = self.venusaur_original_y
                        self.venusaur_move_back = False
                        # Check if lugia is also done moving back
                        if not (hasattr(self, 'lugia_move_back') and self.lugia_move_back):
                            self.move_back_complete = True
                
                # Move lugia down to center of screen (when charge completes, before prompt pulse fades)
                # This happens during the attack sequence
                if hasattr(self, 'lugia_move_back') and self.lugia_move_back and self.battle_lugia_visible and self.battle_lugia and not self.fade_out_after_shake:
                    self.lugia_move_back_timer += self.game.clock.get_time()
                    lugia_move_back_progress = min(1.0, self.lugia_move_back_timer / self.lugia_move_back_duration)
                    # Ease-in-out function for smooth animation
                    def ease_in_out(t):
                        return t * t * (3.0 - 2.0 * t)
                    eased_lugia_progress = ease_in_out(lugia_move_back_progress)
                    
                    if hasattr(self, 'lugia_move_back_start_x') and hasattr(self, 'lugia_move_back_start_y') and hasattr(self, 'lugia_move_back_target_x') and hasattr(self, 'lugia_move_back_target_y'):
                        # Interpolate from current position (above screen) to target (center of screen)
                        # X stays the same, Y moves from above screen to center
                        self.battle_lugia_x = self.lugia_move_back_start_x + (self.lugia_move_back_target_x - self.lugia_move_back_start_x) * eased_lugia_progress
                        self.battle_lugia_y = self.lugia_move_back_start_y + (self.lugia_move_back_target_y - self.lugia_move_back_start_y) * eased_lugia_progress
                        # Fade in lugia as it moves
                        self.battle_lugia_alpha = int(255 * eased_lugia_progress)
                    
                    if lugia_move_back_progress >= 1.0:
                        # Move-back complete - lugia is now centered on screen
                        if hasattr(self, 'lugia_move_back_target_x') and hasattr(self, 'lugia_move_back_target_y'):
                            self.battle_lugia_x = self.lugia_move_back_target_x
                            self.battle_lugia_y = self.lugia_move_back_target_y
                        self.battle_lugia_alpha = 255
                        self.lugia_move_back = False
                        # Trigger screen shake after Lugia finishes sliding down
                        if not self.screen_shake_triggered_after_pulse:
                            self.screen_shake_triggered_after_pulse = True
                            self.screen_shake_active = True
                            # Play SpikeCannon.mp3 when Lugia starts rotating side to side
                            if self.sfx_spike_cannon and not self.spike_cannon_sound_played:
                                self.sfx_spike_cannon.play()
                                self.spike_cannon_sound_played = True
                            self.screen_shake_timer = 0
                            self.lugia_rotation_angle = 0
                        # Check if venusaur is also done moving back
                        if not (hasattr(self, 'venusaur_move_back') and self.venusaur_move_back):
                            self.move_back_complete = True
                # Only slide in when move_used_state is "none" (not during prompt pulse)
                elif self.move_used_state == "none" and self.battle_venu_y > self.battle_venu_target_y:
                    self.battle_venu_y -= self.battle_trainer_speed  # Slide up from under dialog
                    if self.battle_venu_y <= self.battle_venu_target_y:
                        self.battle_venu_y = self.battle_venu_target_y
                    
                    # Calculate Venusaur slide progress (0.0 to 1.0)
                    # Use the initial Y position (Config.SCREEN_HEIGHT) and target Y
                    venusaur_start_y = Config.SCREEN_HEIGHT
                    venusaur_total_distance = venusaur_start_y - self.battle_venu_target_y
                    venusaur_current_distance = venusaur_start_y - self.battle_venu_y
                    if venusaur_total_distance > 0:
                        venusaur_slide_progress = min(1.0, venusaur_current_distance / venusaur_total_distance)
                        # Play ball poof sound when venusaur is halfway through the slide (0.5 progress)
                        if self.sfx_ball_poof and not self.venusaur_slide_sound_played:
                            if venusaur_slide_progress >= 0.5:
                                self.sfx_ball_poof.play()
                                self.venusaur_slide_sound_played = True
                        # Only update text alpha if not in prompt pulse (don't override fade out)
                        if self.move_used_state == "none":
                            # Keep showing Lugia text during slide (no fade during slide)
                            self.battle_text_venusaur_alpha = 0
                            self.battle_text_lugia_alpha = 255
                            # Don't show fight UI during slide
                            if self.fight_ui and not self.move_used_dialog_text:
                                self.fight_ui_alpha = 0
                    else:
                        # Already at target, fully show Venusaur text (only if not in prompt pulse)
                        # But if we have move_used_dialog_text, keep showing it (will fade later)
                        if self.move_used_state == "none":
                            if not self.move_used_dialog_text:
                                # No move used text, show Cursorsaur text normally
                                self.battle_text_venusaur_alpha = 255
                                self.battle_text_lugia_alpha = 0
                            # If move_used_dialog_text exists, keep showing it (battle_text_lugia_alpha stays at 255)
                            # Don't show fight UI if Prompt Pulse has been used
                            if self.fight_ui and not self.move_used_dialog_text:
                                self.fight_ui_alpha = 255
                elif self.move_used_state == "none":
                    # Venusaur has reached target
                    # But if we have move_used_dialog_text, keep showing it (will fade later)
                    if not self.move_used_dialog_text:
                        # No move used text, show Cursorsaur text normally
                        self.battle_text_venusaur_alpha = 255
                        self.battle_text_lugia_alpha = 0
                        self.battle_text_state = "venusaur"
                    # If move_used_dialog_text exists, keep showing it (battle_text_lugia_alpha stays at 255)
                    # Don't show fight UI if Prompt Pulse has been used
                    if self.fight_ui and not self.move_used_dialog_text:
                        self.fight_ui_alpha = 255
                # During prompt pulse (sliding_down, dialog_showing, sliding_out), keep venusaur in place
                # Don't let it move at all during these states
                
                # Animate Venusaur GIF
                if len(self.battle_venu_frames) > 1:
                    self.battle_venu_animation_time += self.battle_venu_animation_speed
                    if self.battle_venu_animation_time >= 1.0:
                        self.battle_venu_animation_time = 0
                        self.battle_venu_current_frame = (self.battle_venu_current_frame + 1) % len(self.battle_venu_frames)
                        self.battle_venu = self.battle_venu_frames[self.battle_venu_current_frame]
            
            # Animate prompt pulse charge sprite (when attack sequence begins - venusaur is centered)
            if self.venusaur_centered and not self.prompt_pulse_charge_complete and len(self.prompt_pulse_charge_frames) > 1:
                self.prompt_pulse_charge_animation_time += self.prompt_pulse_charge_animation_speed
                if self.prompt_pulse_charge_animation_time >= 1.0:
                    self.prompt_pulse_charge_animation_time = 0
                    self.prompt_pulse_charge_current_frame += 1
                    # Check if animation has completed once (played through all frames)
                    if self.prompt_pulse_charge_current_frame >= len(self.prompt_pulse_charge_frames):
                        self.prompt_pulse_charge_complete = True
                        # Move venusaur back to original position (will be handled with smooth easing)
                        self.venusaur_centered = False
                        # Set flags to move both back (venusaur immediately, lugia slides to center during attack)
                        self.venusaur_move_back = True
                        self.lugia_move_back = True
                        # Initialize move-back timers
                        self.venusaur_move_back_timer = 0
                        self.lugia_move_back_timer = 0
                        # Store current positions as start positions for move-back
                        if hasattr(self, 'battle_venu_x') and hasattr(self, 'battle_venu_y'):
                            self.venusaur_move_back_start_x = self.battle_venu_x
                            self.venusaur_move_back_start_y = self.battle_venu_y
                        if self.battle_lugia_visible and hasattr(self, 'battle_lugia_x'):
                            # Start from current position (above screen during black box fade)
                            self.lugia_move_back_start_x = self.battle_lugia_x
                            self.lugia_move_back_start_y = self.battle_lugia_y
                            # Target is center of screen (set when black box started)
                            if hasattr(self, 'lugia_move_back_target_x') and hasattr(self, 'lugia_move_back_target_y'):
                                # Target is already set: center of screen
                                pass
                        # Reset lugia alpha for fade-in
                        self.battle_lugia_alpha = 0
            
            # Handle text transition (immediate switch, no fade animation)
            if self.battle_text_fading and not self.battle_venu_visible and self.move_used_state == "none":
                # Immediately switch from Lugia text to Venusaur text (no fade)
                self.battle_text_lugia_alpha = 0
                self.battle_text_venusaur_alpha = 255
                self.battle_text_state = "venusaur"
                self.battle_text_fading = False
            
        # Update screen shake effect (when lugia is attacked after sliding down)
        # Screen shake happens after Lugia finishes sliding down (lugia_move_back is False and was triggered)
        if self.screen_shake_active:
            self.screen_shake_timer += self.game.clock.get_time()
            if self.screen_shake_timer < self.screen_shake_duration:
                # Calculate shake progress (0 to 1)
                shake_progress = self.screen_shake_timer / self.screen_shake_duration
                # Random shake offset (decreases over time)
                shake_factor = 1.0 - shake_progress  # Decrease shake intensity over time
                self.screen_shake_offset_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity) * shake_factor
                self.screen_shake_offset_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity) * shake_factor
                # Rotate lugia side to side (oscillating rotation)
                # Rotate between -15 and +15 degrees, oscillating faster as shake progresses
                rotation_speed = 0.3 + (shake_progress * 0.2)  # Speed up rotation
                self.lugia_rotation_angle = 15 * math.sin(self.screen_shake_timer * rotation_speed * 0.01)
            else:
                # Shake complete
                self.screen_shake_active = False
                self.screen_shake_offset_x = 0
                self.screen_shake_offset_y = 0
                self.lugia_rotation_angle = 0
                # Start fade-out sequence after screen shake completes
                if not self.fade_out_after_shake and self.move_back_complete:
                    self.fade_out_after_shake = True
                    self.fade_out_timer = 0
                    # Initialize fade-out alphas (start at 255, will fade to 0)
                    self.attack_pulse_end_alpha = 255
                    self.black_block_fade_out_alpha = 255
                    # Start Lugia move-back to original Y position when prompt pulse fades away
                    if self.battle_lugia_visible and hasattr(self, 'battle_lugia_x') and hasattr(self, 'lugia_original_y'):
                        self.lugia_move_back = True
                        self.lugia_move_back_timer = 0
                        # Store current position (center during attack) as start position
                        self.lugia_move_back_start_x = self.battle_lugia_x
                        self.lugia_move_back_start_y = self.battle_lugia_y
                        # Target is original Y position on water
                        self.lugia_move_back_target_x = self.battle_lugia_x
                        self.lugia_move_back_target_y = self.lugia_original_y
        
        # Handle fade-out after screen shake (Prompt Pulse PNG and black background)
        if self.fade_out_after_shake:
            self.fade_out_timer += self.game.clock.get_time()
            fade_progress = min(1.0, self.fade_out_timer / self.fade_out_duration)
            # Ease-in-out for smooth fade
            eased_progress = fade_progress * fade_progress * (3.0 - 2.0 * fade_progress)
            # Fade from 255 to 0
            self.attack_pulse_end_alpha = int(255 * (1.0 - eased_progress))
            self.black_block_fade_out_alpha = int(255 * (1.0 - eased_progress))
            # When fade is complete, immediately revert to original battle scene (no wait period)
            if fade_progress >= 1.0:
                self.attack_pulse_end_alpha = 0
                self.black_block_fade_out_alpha = 0
                # Ensure battle elements are visible again
                self.assets_hidden = False
                # Immediately revert to original battle scene (no fade-in animation, no wait)
                self.fade_in_after_attack = True
                self.fade_in_after_attack_alpha = 255  # Set to full opacity immediately
                self.fade_in_after_attack_timer = self.fade_in_after_attack_duration  # Set to complete immediately
        
        # Handle fade-in after attack sequence (dialog box and fighting background)
        # IMMEDIATELY revert to original battle state (no wait period, no fade-in)
        if self.fade_in_after_attack:
            # Immediately complete fade-in and reset everything
            self.fade_in_after_attack_alpha = 255
            self.fade_in_after_attack = False
            # Reset move_used_state to restore normal battle state
            self.move_used_state = "none"
            # Reset all battle scene positions to normal state
            # Ensure Venusaur is at its original position (above dialog)
            if self.battle_venu_visible and hasattr(self, 'battle_venu_target_y'):
                self.battle_venu_y = self.battle_venu_target_y
                # Reset venusaur position attributes if they exist
                if hasattr(self, 'battle_venu_x'):
                    # Calculate normal X position based on grass
                    if self.battle_grass and self.battle_venu:
                        scaled_venu_width = int(self.battle_venu.get_width() * 2.0)
                        grass_center_x = self.battle_grass_left_x + (self.battle_grass.get_width() // 2)
                        self.battle_venu_x = grass_center_x - (scaled_venu_width // 2)
            # Ensure Lugia is at its original position (on water)
            if self.battle_lugia_visible and hasattr(self, 'lugia_original_y'):
                self.battle_lugia_y = self.lugia_original_y
                # Reset lugia X position to target if it exists
                if hasattr(self, 'battle_lugia_target_x'):
                    self.battle_lugia_x = self.battle_lugia_target_x
            # Reset all move-back flags and states
            self.venusaur_move_back = False
            self.lugia_move_back = False
            self.venusaur_centered = False
            self.move_back_complete = False
            self.venusaur_move_back_timer = 0
            self.lugia_move_back_timer = 0
            # Reset lugia moved above screen flag
            if hasattr(self, 'lugia_moved_above_screen'):
                self.lugia_moved_above_screen = False
            # Reset prompt pulse charge animation state
            self.prompt_pulse_charge_complete = False
            self.prompt_pulse_charge_current_frame = 0
            self.prompt_pulse_charge_animation_time = 0
            # Reset fade-out state
            self.fade_out_after_shake = False
            self.fade_out_timer = 0
            # Reset battle slide out flag
            self.battle_slide_out = False
            # Reset screen shake state
            self.screen_shake_active = False
            self.screen_shake_triggered_after_pulse = False
            self.screen_shake_offset_x = 0
            self.screen_shake_offset_y = 0
            self.lugia_rotation_angle = 0
            # Reset black block and attack pulse end alpha
            self.black_block_alpha = 0
            self.attack_pulse_end_alpha = 0
            self.black_block_fade_out_alpha = 0
            self.assets_hidden = False
            # Ensure battle elements are fully visible
            if hasattr(self, 'battle_lugia_alpha'):
                self.battle_lugia_alpha = 255
            # Skip trainer sprite animation - make it invisible immediately (no trainer animation)
            # Trainer should be invisible after it slides out (as it was before prompt pulse)
            self.battle_trainer_visible = False
            self.battle_trainer_can_animate = False
            self.battle_trainer_slide_out = False
            # Ensure grass is visible and positioned correctly immediately (no wait period)
            self.battle_grass_visible = True
            if self.battle_grass:
                self.battle_grass_left_x = self.battle_grass_left_target_x  # Immediately at target position
            # Ensure Venusaur is visible and positioned correctly immediately (no wait period)
            self.battle_venu_visible = True
            if self.battle_venu_visible and hasattr(self, 'battle_venu_target_y'):
                self.battle_venu_y = self.battle_venu_target_y  # Immediately at target position
            # Ensure Lugia is visible and positioned correctly
            if hasattr(self, 'battle_lugia_visible'):
                self.battle_lugia_visible = True
            # Ensure Lugia stat container (pokemonstat) is visible
            if hasattr(self, 'battle_pokemonstat_visible'):
                self.battle_pokemonstat_visible = True
            # Ensure Venusaur stat container is visible
            if hasattr(self, 'battle_venu_stat_visible'):
                self.battle_venu_stat_visible = True
            # Ensure fight UI is visible (but only if move_used_dialog_text doesn't exist)
            # After prompt pulse, fight UI should remain hidden (as it was before prompt pulse)
            # Note: fight UI is hidden when move_used_dialog_text exists, which is correct
            # After attack sequence, show the move used text in dialog instead of Bugia text
            # Set battle_text_lugia_alpha to show the move used text
            if self.move_used_dialog_text:
                self.battle_text_lugia_alpha = 255
                self.battle_text_venusaur_alpha = 0
                # Set a timer to fade to Cursorsaur text after showing move used text
                # This will be handled in the update loop
                if not hasattr(self, 'move_used_text_display_timer'):
                    self.move_used_text_display_timer = 0
                self.move_used_text_display_timer = 0  # Reset timer
                self.move_used_text_fade_duration = 2000  # Show for 2 seconds before fading
                # Start end scene animation after prompt pulse attack completes
                self.end_scene_active = True
                self.end_scene_health_bar_timer = 0
                self.end_scene_health_bar_width = 96  # Start at full width
                self.end_scene_health_bar_pause_timer = 0  # Reset pause timer
                self.end_scene_health_bar_cry_played = False  # Reset cry flag
                self.end_scene_lugia_fall_timer = 0
                self.end_scene_lugia_fall_alpha = 255  # Start at full opacity
                # Store Lugia's starting position for fall animation
                if self.battle_lugia_visible and hasattr(self, 'battle_lugia_x') and hasattr(self, 'battle_lugia_y'):
                    self.end_scene_lugia_fall_start_x = self.battle_lugia_x
                    self.end_scene_lugia_fall_start_y = self.battle_lugia_y
                # Initialize black background fade state
                self.end_scene_black_bg_active = False
                self.end_scene_black_bg_alpha = 0
                self.end_scene_black_bg_timer = 0
                self.end_scene_elements_fade_alpha = 255  # Start at full opacity
                self.end_scene_music_played = False  # Flag to play end scene music only once when black bg appears
        
        # Handle end scene animation (health bar decrease and Lugia fall)
        if self.end_scene_active:
            # Phase 1: Health bar animation (2 seconds)
            if self.end_scene_health_bar_timer < self.end_scene_health_bar_duration:
                self.end_scene_health_bar_timer += self.game.clock.get_time()
                # Calculate progress (0.0 to 1.0)
                health_bar_progress = min(1.0, self.end_scene_health_bar_timer / self.end_scene_health_bar_duration)
                # Decrease width from 96 to 0
                self.end_scene_health_bar_width = int(self.end_scene_health_bar_initial_width * (1.0 - health_bar_progress))
                # Play cry sound when health bar reaches 0
                if self.end_scene_health_bar_width <= 0 and not self.end_scene_health_bar_cry_played:
                    if self.sfx_cry_17:
                        self.sfx_cry_17.play()
                    self.end_scene_health_bar_cry_played = True
            else:
                # Health bar has reached 0 - play cry sound if not already played
                if not self.end_scene_health_bar_cry_played:
                    if self.sfx_cry_17:
                        self.sfx_cry_17.play()
                    self.end_scene_health_bar_cry_played = True
                # Phase 1.5: Pause after health bar reaches 0 (0.5 seconds)
                if self.end_scene_health_bar_pause_timer < self.end_scene_health_bar_pause_duration:
                    self.end_scene_health_bar_pause_timer += self.game.clock.get_time()
                else:
                    # Phase 2: Lugia fall animation (1 second) - starts after pause
                    if self.end_scene_lugia_fall_timer < self.end_scene_lugia_fall_duration:
                        self.end_scene_lugia_fall_timer += self.game.clock.get_time()
                        # Calculate progress (0.0 to 1.0)
                        fall_progress = min(1.0, self.end_scene_lugia_fall_timer / self.end_scene_lugia_fall_duration)
                        # Fade Lugia to 0 opacity (255 to 0)
                        self.end_scene_lugia_fall_alpha = int(255 * (1.0 - fall_progress))
                        # Move Lugia down the Y axis by 40px (no rotation, no horizontal movement)
                        if hasattr(self, 'battle_lugia_y'):
                            self.battle_lugia_y = self.end_scene_lugia_fall_start_y + (self.end_scene_lugia_fall_distance * fall_progress)
                    else:
                        # Phase 2.5: Show "Bugia fainted!" text (1 second) - starts after Lugia fall completes
                        if not self.end_scene_fainted_text_active:
                            # Update text to "Bugia fainted!"
                            self.move_used_dialog_text = "Bugia fainted!"
                            self.end_scene_fainted_text_active = True
                            self.end_scene_fainted_text_timer = 0
                            # Play press AB sound when "Bugia fainted!" text shows
                            if self.sfx_press_ab:
                                self.sfx_press_ab.play()
                        else:
                            # Show "Bugia fainted!" text for 1 second
                            if self.end_scene_fainted_text_timer < self.end_scene_fainted_text_duration:
                                self.end_scene_fainted_text_timer += self.game.clock.get_time()
                            else:
                                # Phase 3: Delay before black background (1 second delay after "Bugia fainted!" text)
                                if self.end_scene_black_bg_delay_timer < self.end_scene_black_bg_delay_duration:
                                    self.end_scene_black_bg_delay_timer += self.game.clock.get_time()
                                else:
                                    # Phase 4: Black background fade-in and elements fade-out (starts after delay)
                                    if not self.end_scene_black_bg_active:
                                        self.end_scene_black_bg_active = True
                                        self.end_scene_black_bg_timer = 0
                                        self.end_scene_black_bg_alpha = 0
                                        self.end_scene_elements_fade_alpha = 255
                                        # Switch to end scene music when black background appears
                                        if not self.end_scene_music_played:
                                            end_scene_music_path = os.path.join(Config.SOUNDS_PATH, "01. Opening Movie (Red, Green & Blue Version).mp3")
                                            try:
                                                pygame.mixer.music.load(end_scene_music_path)
                                                pygame.mixer.music.set_volume(self.music_volume)  # Set volume AFTER loading
                                                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                                                self.end_scene_music_played = True
                                            except pygame.error as e:
                                                print(f"Unable to load end scene music: {end_scene_music_path}")
                                                print(f"Error: {e}")
                            
                            if self.end_scene_black_bg_active:
                                self.end_scene_black_bg_timer += self.game.clock.get_time()
                                # Calculate progress (0.0 to 1.0)
                                black_bg_progress = min(1.0, self.end_scene_black_bg_timer / self.end_scene_black_bg_duration)
                                # Fade in black background (0 to 255)
                                self.end_scene_black_bg_alpha = int(255 * black_bg_progress)
                                # Fade out all other elements (255 to 0)
                                self.end_scene_elements_fade_alpha = int(255 * (1.0 - black_bg_progress))
                                
                                # Start end Venusaur animation when black background is fully faded in
                                if black_bg_progress >= 1.0 and not self.end_scene_venusaur_active:
                                    self.end_scene_venusaur_active = True
                                    self.end_scene_venusaur_fade_timer = 0
                                    self.end_scene_venusaur_fade_alpha = 0
                                    self.end_scene_venusaur_slide_timer = 0
                                    # Calculate positions: fade in centered, then slide from 144px from right to 32px from right
                                    if self.end_scene_venusaur_image:
                                        # Fade in centered (horizontally and vertically)
                                        self.end_scene_venusaur_fade_x = (Config.SCREEN_WIDTH - self.end_scene_venusaur_image.get_width()) // 2
                                        # Slide animation: from 144px from right to 32px from right
                                        self.end_scene_venusaur_start_x = Config.SCREEN_WIDTH - 144 - self.end_scene_venusaur_image.get_width()  # 144px from right
                                        self.end_scene_venusaur_end_x = Config.SCREEN_WIDTH - 32 - self.end_scene_venusaur_image.get_width()  # 32px from right
                                        # Start at fade position (centered)
                                        self.end_scene_venusaur_x = self.end_scene_venusaur_fade_x
                                        self.end_scene_venusaur_y = (Config.SCREEN_HEIGHT - self.end_scene_venusaur_image.get_height()) // 2
                                
                                # Handle end Venusaur animation
                                if self.end_scene_venusaur_active and self.end_scene_venusaur_image:
                                    # Phase 1: Fade in centered (2 seconds)
                                    if self.end_scene_venusaur_fade_timer < self.end_scene_venusaur_fade_duration:
                                        self.end_scene_venusaur_fade_timer += self.game.clock.get_time()
                                        fade_progress = min(1.0, self.end_scene_venusaur_fade_timer / self.end_scene_venusaur_fade_duration)
                                        self.end_scene_venusaur_fade_alpha = int(255 * fade_progress)
                                        # Keep centered during fade-in
                                        self.end_scene_venusaur_x = self.end_scene_venusaur_fade_x
                                    else:
                                        # Phase 2: Slide to the right (0.5 seconds) - from 144px from right to 32px from right
                                        if self.end_scene_venusaur_slide_timer < self.end_scene_venusaur_slide_duration:
                                            self.end_scene_venusaur_slide_timer += self.game.clock.get_time()
                                            slide_progress = min(1.0, self.end_scene_venusaur_slide_timer / self.end_scene_venusaur_slide_duration)
                                            # Slide from 144px from right to 32px from right
                                            self.end_scene_venusaur_x = self.end_scene_venusaur_start_x + (self.end_scene_venusaur_end_x - self.end_scene_venusaur_start_x) * slide_progress
                                            
                                            # Start pokemon shine fade-in when slide starts
                                            if not self.end_scene_pokemon_shine_active and self.end_scene_venusaur_slide_timer > 0:
                                                self.end_scene_pokemon_shine_active = True
                                                self.end_scene_pokemon_shine_fade_timer = 0
                                                self.end_scene_pokemon_shine_fade_alpha = 0
                                                self.end_scene_pokemon_shine_current_frame = 0
                                                self.end_scene_pokemon_shine_animation_time = 0
                                        else:
                                            # Slide complete - stay at final position (32px from right)
                                            self.end_scene_venusaur_x = self.end_scene_venusaur_end_x
                                        # Keep at full opacity during slide
                                        self.end_scene_venusaur_fade_alpha = 255
                                
                                # Handle pokemon shine animation (fades in and animates when end_venusaur moves right)
                                if self.end_scene_pokemon_shine_active and self.end_scene_pokemon_shine_frames:
                                    # Animate pokemon shine sprite
                                    if len(self.end_scene_pokemon_shine_frames) > 1:
                                        self.end_scene_pokemon_shine_animation_time += self.game.clock.get_time()
                                        if self.end_scene_pokemon_shine_animation_time >= self.end_scene_pokemon_shine_animation_speed:
                                            self.end_scene_pokemon_shine_animation_time = 0
                                            self.end_scene_pokemon_shine_current_frame = (self.end_scene_pokemon_shine_current_frame + 1) % len(self.end_scene_pokemon_shine_frames)
                                    
                                    # Fade in pokemon shine
                                    if self.end_scene_pokemon_shine_fade_timer < self.end_scene_pokemon_shine_fade_duration:
                                        self.end_scene_pokemon_shine_fade_timer += self.game.clock.get_time()
                                        fade_progress = min(1.0, self.end_scene_pokemon_shine_fade_timer / self.end_scene_pokemon_shine_fade_duration)
                                        self.end_scene_pokemon_shine_fade_alpha = int(255 * fade_progress)
                                    else:
                                        # Keep at full opacity after fade completes
                                        self.end_scene_pokemon_shine_fade_alpha = 255
                                        # Start end background slide animation when pokemon shine fade completes
                                        if not self.end_scene_bg_active and self.end_scene_bg_image:
                                            self.end_scene_bg_active = True
                                            self.end_scene_bg_slide_timer = 0
                                            # Calculate positions: start with right side at left edge (x = -width), end with right side at right edge (x = screen_width - width)
                                            bg_width = self.end_scene_bg_image.get_width()
                                            self.end_scene_bg_start_x = -bg_width  # Right side at x=0 (left edge of screen)
                                            self.end_scene_bg_end_x = Config.SCREEN_WIDTH - bg_width  # Right side at x=screen_width (right edge of screen)
                                            self.end_scene_bg_x = self.end_scene_bg_start_x
                                            # Center vertically
                                            self.end_scene_bg_y = (Config.SCREEN_HEIGHT - self.end_scene_bg_image.get_height()) // 2
                                
                                # Handle end background slide animation
                                if self.end_scene_bg_active and self.end_scene_bg_image:
                                    if self.end_scene_bg_slide_timer < self.end_scene_bg_slide_duration:
                                        self.end_scene_bg_slide_timer += self.game.clock.get_time()
                                        slide_progress = min(1.0, self.end_scene_bg_slide_timer / self.end_scene_bg_slide_duration)
                                        # Apply ease-in-out easing function for smooth animation
                                        def ease_in_out(t):
                                            return t * t * (3.0 - 2.0 * t)
                                        eased_progress = ease_in_out(slide_progress)
                                        # Slide from start to end position with easing
                                        self.end_scene_bg_x = self.end_scene_bg_start_x + (self.end_scene_bg_end_x - self.end_scene_bg_start_x) * eased_progress
                                    else:
                                        # Slide complete - stay at final position
                                        self.end_scene_bg_x = self.end_scene_bg_end_x
                                        # Start cursor and press-r fade-in when end_bg slide completes
                                        if not self.end_scene_cursor_active and self.end_scene_cursor_image:
                                            self.end_scene_cursor_active = True
                                            self.end_scene_cursor_fade_timer = 0
                                            self.end_scene_cursor_fade_alpha = 0
                                            # Position: centered x-wise relative to pokemon shine, directly under pokemon shine
                                            if self.end_scene_pokemon_shine_active and self.end_scene_pokemon_shine_frames:
                                                # Calculate pokemon shine center x
                                                if len(self.end_scene_pokemon_shine_frames) > 0:
                                                    pokemon_shine_width = self.end_scene_pokemon_shine_frames[0].get_width()
                                                    pokemon_shine_center_x = self.end_scene_pokemon_shine_x + (pokemon_shine_width // 2)
                                                    # Center cursor version on pokemon shine center, then move right by 10px
                                                    self.end_scene_cursor_x = pokemon_shine_center_x - (self.end_scene_cursor_image.get_width() // 2) + 10
                                                    # Position directly under pokemon shine (use actual frame height), then move up by 20px, then lower by 5px
                                                    pokemon_shine_height = self.end_scene_pokemon_shine_frames[0].get_height()
                                                    self.end_scene_cursor_target_y = self.end_scene_pokemon_shine_y + pokemon_shine_height - 20 + 5
                                                    # Start 25px below target, slide up to target
                                                    self.end_scene_cursor_start_y = self.end_scene_cursor_target_y + self.end_scene_cursor_slide_offset
                                                    self.end_scene_cursor_y = self.end_scene_cursor_start_y
                                                else:
                                                    # Fallback: center on screen
                                                    self.end_scene_cursor_x = (Config.SCREEN_WIDTH - self.end_scene_cursor_image.get_width()) // 2
                                                    self.end_scene_cursor_target_y = Config.SCREEN_HEIGHT // 2
                                                    self.end_scene_cursor_start_y = self.end_scene_cursor_target_y + self.end_scene_cursor_slide_offset
                                                    self.end_scene_cursor_y = self.end_scene_cursor_start_y
                                            else:
                                                # Fallback: center on screen
                                                self.end_scene_cursor_x = (Config.SCREEN_WIDTH - self.end_scene_cursor_image.get_width()) // 2
                                                self.end_scene_cursor_target_y = Config.SCREEN_HEIGHT // 2
                                                self.end_scene_cursor_start_y = self.end_scene_cursor_target_y + self.end_scene_cursor_slide_offset
                                                self.end_scene_cursor_y = self.end_scene_cursor_start_y
                                        
                                        if not self.end_scene_press_r_active and self.end_scene_press_r_image:
                                            self.end_scene_press_r_active = True
                                            self.end_scene_press_r_fade_timer = 0
                                            self.end_scene_press_r_fade_alpha = 0
                                            self.end_scene_press_r_fade_complete = False
                                            self.end_scene_press_r_blink_timer = 0
                                            self.end_scene_press_r_blink_alpha = 255
                                            # Position: centered horizontally, 10px under end_bg
                                            self.end_scene_press_r_x = (Config.SCREEN_WIDTH - self.end_scene_press_r_image.get_width()) // 2
                                            if self.end_scene_bg_image:
                                                self.end_scene_press_r_y = self.end_scene_bg_y + self.end_scene_bg_image.get_height() + 10
                                            else:
                                                # Fallback: center on screen
                                                self.end_scene_press_r_y = Config.SCREEN_HEIGHT // 2
        
        # Handle cursor and press-r animations independently (outside black_bg_active block)
        # Handle cursor fade-in and slide-up animation
        if self.end_scene_cursor_active and self.end_scene_cursor_image:
            if self.end_scene_cursor_fade_timer < self.end_scene_cursor_fade_duration:
                self.end_scene_cursor_fade_timer += self.game.clock.get_time()
                fade_progress = min(1.0, self.end_scene_cursor_fade_timer / self.end_scene_cursor_fade_duration)
                self.end_scene_cursor_fade_alpha = int(255 * fade_progress)
                # Slide up from start_y to target_y during fade-in
                self.end_scene_cursor_y = self.end_scene_cursor_start_y - (self.end_scene_cursor_slide_offset * fade_progress)
            else:
                # Keep at full opacity and target position after fade completes
                self.end_scene_cursor_fade_alpha = 255
                self.end_scene_cursor_y = self.end_scene_cursor_target_y
        
        # Handle press-r fade-in and blink animation
        if self.end_scene_press_r_active and self.end_scene_press_r_image:
            # Skip fade-in phase, immediately start blinking
            if not self.end_scene_press_r_fade_complete:
                # Immediately complete fade-in and start blinking
                self.end_scene_press_r_fade_alpha = 255
                self.end_scene_press_r_fade_complete = True
                self.end_scene_press_r_blink_timer = 0
            
            # Phase 2: Blink cycle: 1sec fade in, 1sec hold, 1sec fade out, repeat
            self.end_scene_press_r_blink_timer += self.game.clock.get_time()
            # Get cycle progress (0.0 to 1.0) within total duration
            cycle_progress = (self.end_scene_press_r_blink_timer % self.end_scene_press_r_blink_total_duration) / self.end_scene_press_r_blink_total_duration
            
            # Determine which phase of the cycle we're in
            fade_in_end = self.end_scene_press_r_blink_fade_in_duration / self.end_scene_press_r_blink_total_duration
            hold_end = fade_in_end + (self.end_scene_press_r_blink_hold_duration / self.end_scene_press_r_blink_total_duration)
            
            if cycle_progress < fade_in_end:
                # Fade in phase (0 to fade_in_end)
                phase_progress = cycle_progress / fade_in_end
                self.end_scene_press_r_blink_alpha = int(255 * phase_progress)
            elif cycle_progress < hold_end:
                # Hold phase (fade_in_end to hold_end)
                self.end_scene_press_r_blink_alpha = 255
            else:
                # Fade out phase (hold_end to 1.0)
                phase_progress = (cycle_progress - hold_end) / (1.0 - hold_end)
                self.end_scene_press_r_blink_alpha = int(255 * (1.0 - phase_progress))
        
        # Handle fade from move used text to Cursorsaur text (after attack sequence)
        if self.move_used_dialog_text and self.move_used_state == "none" and hasattr(self, 'move_used_text_display_timer'):
            self.move_used_text_display_timer += self.game.clock.get_time()
            if self.move_used_text_display_timer >= self.move_used_text_fade_duration:
                # Start fading from move used text to Cursorsaur text
                fade_speed = 3  # Fade speed (pixels per frame equivalent)
                if self.battle_text_lugia_alpha > 0:
                    self.battle_text_lugia_alpha = max(0, self.battle_text_lugia_alpha - fade_speed)
                if self.battle_text_lugia_alpha == 0 and self.battle_text_venusaur_alpha < 255:
                    self.battle_text_venusaur_alpha = min(255, self.battle_text_venusaur_alpha + fade_speed)
                    if self.battle_text_venusaur_alpha >= 255:
                        # Fade complete, keep move used dialog text visible (don't clear it)
                        # self.move_used_dialog_text = ""  # Keep it so it shows instead of Bugia text
                        self.battle_text_state = "venusaur"
        
        # Handle "You can't run away!" text - show immediately (no fade animation)
        if self.run_text_visible:
            self.run_text_alpha = 255  # Show immediately at full opacity
        else:
            self.run_text_alpha = 0  # Hide immediately
        
        # Handle "Your Cursorsaur already has full HP!" text - show immediately (no fade animation)
        if self.full_hp_text_visible:
            self.full_hp_text_alpha = 255  # Show immediately at full opacity
        else:
            self.full_hp_text_alpha = 0  # Hide immediately
        
        # Reset collision sound flag when sound finishes (check if sound is still playing)
        if self.collision_sound_playing and self.sfx_collision:
            # Check if sound is still playing (get_num_channels returns active channels)
            # We'll use a simple timer approach - reset after a short delay
            # Actually, pygame doesn't have a direct way to check if a sound is playing
            # So we'll use a timer approach - reset after 0.1 seconds (sound should be short)
            if not hasattr(self, 'collision_sound_timer'):
                self.collision_sound_timer = 0
            self.collision_sound_timer += self.game.clock.get_time()
            if self.collision_sound_timer >= 750:  # 0.75 second stagger between collision sounds
                self.collision_sound_playing = False
                self.collision_sound_timer = 0
        
        # ============================================================================
        # PROMPT PULSE ANIMATION HANDLER
        # ============================================================================
        if self.move_used_state == "sliding_down":
            # Slide combat UI and fight UI down
            slide_speed = 8
            if self.move_used_ui_slide_y < self.move_used_ui_target_y:
                self.move_used_ui_slide_y += slide_speed
                if self.move_used_ui_slide_y >= self.move_used_ui_target_y:
                    self.move_used_ui_slide_y = self.move_used_ui_target_y
                    # UI has slid down, show dialog and start wait timer
                    self.move_used_state = "dialog_showing"
                    self.move_used_wait_timer = 0
        elif self.move_used_state == "dialog_showing":
            # Wait 1.5 seconds after dialog shows, then start fading to black (and all animations)
            self.move_used_wait_timer += self.game.clock.get_time()
            if self.move_used_wait_timer >= self.move_used_wait_duration:
                # 1.5 seconds have passed, start fading to black and all slide/fade animations
                self.move_used_state = "fading_black"
        elif self.move_used_state == "fading_black":
            # ============================================================================
            # PROMPT PULSE ANIMATION SECTION
            # Easy to edit: All animations complete in 1 second total
            # ============================================================================
            
            # Initialize animations on first frame
            if not self.battle_slide_out:
                self.battle_slide_out = True
                # Initialize black block alpha (starts at 0, fades in)
                self.black_block_alpha = 0
                # Initialize venusaur center position for straight line slide
                if self.battle_venu_visible and self.battle_venu and self.battle_grass:
                    scaled_venu_width = int(self.battle_venu.get_width() * 2.0)
                    grass_center_x = self.battle_grass_left_x + (self.battle_grass.get_width() // 2)
                    self.battle_venu_start_x = grass_center_x - (scaled_venu_width // 2)
                    self.battle_venu_start_y = self.battle_venu_y
                    # Store original position before moving to center (normal position above dialog)
                    self.venusaur_original_x = self.battle_venu_start_x
                    self.venusaur_original_y = self.battle_venu_target_y  # Use target Y (normal position above dialog)
                    # Store lugia's position when black box starts (lugia stays on water until black block fades in)
                    if self.battle_lugia_visible and self.battle_lugia:
                        # Store current position (Lugia stays on water during black block fade-in)
                        self.lugia_black_box_x = self.battle_lugia_x
                        self.lugia_black_box_y = self.battle_lugia_y
                        # Store original position (for reset)
                        self.lugia_original_x = self.battle_lugia_target_x
                        self.lugia_original_y = self.battle_lugia_y
                        # Calculate position above screen (will be used once black block fades in)
                        scaled_lugia_height = int(self.battle_lugia.get_height() * 1.5)
                        self.lugia_above_screen_y = -scaled_lugia_height  # Position above screen, out of view
                        # Target position for first move-back (when charge completes): center of screen
                        self.lugia_move_back_target_x = self.battle_lugia_x  # Same x coordinate
                        # During attack sequence, Lugia slides to center of screen
                        # Slide down by 1 lugia height + 40px additional
                        self.lugia_move_back_target_y = (Config.SCREEN_HEIGHT // 2) - scaled_lugia_height + 40
                        # Store the position above screen as the start position for move-back
                        self.lugia_move_back_start_x = self.battle_lugia_x
                        self.lugia_move_back_start_y = self.lugia_above_screen_y
                        # Flag to track if Lugia has been moved above screen
                        self.lugia_moved_above_screen = False
                    # Calculate center target
                    self.battle_venu_center_target_x = (Config.SCREEN_WIDTH // 2) - (scaled_venu_width // 2)
                    self.battle_venu_center_target_y = (Config.SCREEN_HEIGHT // 2) - (int(self.battle_venu.get_height() * 2.0) // 2)
                    # Initialize battle_venu_x and battle_venu_y for movement
                    self.battle_venu_x = self.battle_venu_start_x
                    self.battle_venu_y = self.battle_venu_start_y
                    self.venusaur_centered = False
                    # Reset prompt pulse charge animation
                    self.prompt_pulse_charge_complete = False
                    self.prompt_pulse_charge_current_frame = 0
                    self.prompt_pulse_charge_animation_time = 0
                    # Reset move-back timers
                    self.venusaur_move_back_timer = 0
                    self.lugia_move_back_timer = 0
                    self.lugia_move_back = False
                    # Keep lugia visible during attack sequence (will fade in during move-back)
                    self.battle_lugia_alpha = 255
                    # Reset move-back complete flag
                    self.move_back_complete = False
                # Initialize animation timer
                self.prompt_pulse_animation_timer = 0
                # Track if assets should be hidden (once black block is fully faded in)
                self.assets_hidden = False
            
            # Update animation timer (all animations complete in 1 second)
            self.prompt_pulse_animation_timer += self.game.clock.get_time()
            progress = min(1.0, self.prompt_pulse_animation_timer / self.prompt_pulse_animation_duration)
            
            # ============================================================================
            # EDITABLE ANIMATION TIMING PARAMETERS
            # ============================================================================
            # Black block fade in duration: How long it takes for black block to fully fade in (0.0 to 1.0)
            # 0.3 = fades in over first 30% of animation (0.3 seconds)
            # 0.5 = fades in over first 50% of animation (0.5 seconds)
            # 1.0 = fades in over the full animation duration (1.0 seconds)
            black_block_fade_duration = 1.0  # EDIT THIS: How long black block takes to fade in (0.0 to 1.0)
            
            # Venusaur movement speed: Lower value = slower movement (0.0 to 1.0)
            # 0.25 = reaches center at 25% of animation (0.25 seconds)
            # 0.5 = reaches center at 50% of animation (0.5 seconds)
            # 1.0 = reaches center instantly
            venusaur_center_progress = 0.5  # EDIT THIS: When venusaur reaches center (0.0 to 1.0)
            
            # Prompt pulse charge animation speed: Frame change speed for prompt pulse charge sprite
            # Lower value = slower animation (same as other sprite speeds)
            # 0.2 = slower than venusaur (0.4), 0.4 = same speed as venusaur
            prompt_pulse_charge_animation_speed = self.prompt_pulse_charge_animation_speed  # EDIT THIS: Animation speed (default: 0.2)
            # ============================================================================
            
            # Ease-in-out function (smoothstep) for smooth animations
            def ease_in_out(t):
                """Ease-in-out easing function (smoothstep)"""
                return t * t * (3.0 - 2.0 * t)
            
            # Fade in black block (covers whole screen, above all assets except venusaur)
            if progress <= black_block_fade_duration:
                # Fade in black block with ease-in-out
                black_block_progress = min(1.0, progress / black_block_fade_duration)
                eased_progress = ease_in_out(black_block_progress)
                self.black_block_alpha = int(255 * eased_progress)
                # Hide assets when fully faded (alpha = 255)
                self.assets_hidden = (self.black_block_alpha >= 255)
            else:
                # Black block is fully faded in, hide all assets under it
                self.black_block_alpha = 255
                self.assets_hidden = True
            
            # Slide venusaur to center in a straight line with ease-in-out
            # Venusaur reaches center based on venusaur_center_progress
            if self.battle_venu_visible and self.battle_venu and hasattr(self, 'battle_venu_center_target_x'):
                # Check if we need to move venusaur back to original position (after charge animation completes)
                if hasattr(self, 'venusaur_move_back') and self.venusaur_move_back:
                    # Smooth move-back animation with ease-in-out
                    self.venusaur_move_back_timer += self.game.clock.get_time()
                    move_back_progress = min(1.0, self.venusaur_move_back_timer / self.venusaur_move_back_duration)
                    eased_move_back_progress = ease_in_out(move_back_progress)
                    
                    if hasattr(self, 'venusaur_move_back_start_x') and hasattr(self, 'venusaur_move_back_start_y') and hasattr(self, 'venusaur_original_x') and hasattr(self, 'venusaur_original_y'):
                        # Interpolate from current position (center) back to original position
                        self.battle_venu_x = self.venusaur_move_back_start_x + (self.venusaur_original_x - self.venusaur_move_back_start_x) * eased_move_back_progress
                        self.battle_venu_y = self.venusaur_move_back_start_y + (self.venusaur_original_y - self.venusaur_move_back_start_y) * eased_move_back_progress
                    
                    if move_back_progress >= 1.0:
                        # Move-back complete
                        if hasattr(self, 'venusaur_original_x') and hasattr(self, 'venusaur_original_y'):
                            self.battle_venu_x = self.venusaur_original_x
                            self.battle_venu_y = self.venusaur_original_y
                        self.venusaur_move_back = False
                        # Check if lugia is also done moving back
                        if not (hasattr(self, 'lugia_move_back') and self.lugia_move_back):
                            self.move_back_complete = True
                elif not self.prompt_pulse_charge_complete:
                    # Interpolate from start to center based on progress with ease-in-out
                    # Use venusaur_center_progress to control when venusaur reaches center
                    venusaur_progress = min(1.0, progress / venusaur_center_progress) if progress <= venusaur_center_progress else 1.0
                    eased_venusaur_progress = ease_in_out(venusaur_progress)
                    self.battle_venu_x = self.battle_venu_start_x + (self.battle_venu_center_target_x - self.battle_venu_start_x) * eased_venusaur_progress
                    self.battle_venu_y = self.battle_venu_start_y + (self.battle_venu_center_target_y - self.battle_venu_start_y) * eased_venusaur_progress
                    # Check if venusaur has reached center
                    if progress >= venusaur_center_progress and not self.venusaur_centered:
                        self.venusaur_centered = True
                        # Play Spore.mp3 when prompt pulse charge begins
                        if self.sfx_spore and not self.spore_sound_played:
                            self.sfx_spore.play()
                            self.spore_sound_played = True
                        # Move Lugia above screen when Prompt Pulse Charge starts (venusaur reaches center)
                        if hasattr(self, 'lugia_moved_above_screen') and not self.lugia_moved_above_screen:
                            if self.battle_lugia_visible and self.battle_lugia and hasattr(self, 'lugia_above_screen_y'):
                                self.battle_lugia_y = self.lugia_above_screen_y
                                self.lugia_moved_above_screen = True
            
                # Move lugia back to original Y position when prompt pulse background fades away
                if hasattr(self, 'lugia_move_back') and self.lugia_move_back and self.battle_lugia_visible and self.battle_lugia and self.fade_out_after_shake:
                    self.lugia_move_back_timer += self.game.clock.get_time()
                    lugia_move_back_progress = min(1.0, self.lugia_move_back_timer / self.lugia_move_back_duration)
                    # Ease-in-out function for smooth animation
                    def ease_in_out(t):
                        return t * t * (3.0 - 2.0 * t)
                    eased_lugia_progress = ease_in_out(lugia_move_back_progress)
                    
                    if hasattr(self, 'lugia_move_back_start_x') and hasattr(self, 'lugia_move_back_start_y') and hasattr(self, 'lugia_move_back_target_x') and hasattr(self, 'lugia_move_back_target_y'):
                        # Interpolate from current position (center) to target (original Y on water)
                        self.battle_lugia_x = self.lugia_move_back_start_x + (self.lugia_move_back_target_x - self.lugia_move_back_start_x) * eased_lugia_progress
                        self.battle_lugia_y = self.lugia_move_back_start_y + (self.lugia_move_back_target_y - self.lugia_move_back_start_y) * eased_lugia_progress
                    
                    if lugia_move_back_progress >= 1.0:
                        # Move-back complete - lugia is now at original Y position on water
                        if hasattr(self, 'lugia_move_back_target_x') and hasattr(self, 'lugia_move_back_target_y'):
                            self.battle_lugia_x = self.lugia_move_back_target_x
                            self.battle_lugia_y = self.lugia_move_back_target_y
                        self.lugia_move_back = False
            
            # ============================================================================
            
    
    def render(self, screen):
        """Render house/village scene with scrolling map"""
        # Helper function to apply shake offset to positions
        def apply_shake_offset(x, y):
            if self.screen_shake_active:
                return (x + int(self.screen_shake_offset_x), y + int(self.screen_shake_offset_y))
            return (x, y)
        
        # If fully faded, show battle screen with animations
        if self.fade_state == "faded" and self.fighting_background:
            # Draw fighting background (always visible during battle)
            scaled_bg = pygame.transform.scale(self.fighting_background, 
                                             (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            # Apply fade-out alpha during black background fade-in
            if self.end_scene_black_bg_active and self.end_scene_elements_fade_alpha < 255:
                scaled_bg.set_alpha(self.end_scene_elements_fade_alpha)
            screen.blit(scaled_bg, apply_shake_offset(0, 0))
            
            # Draw stat containers (always visible during battle)
            # Draw battle pokemonstat (top left - Lugia stat)
            if self.battle_pokemonstat_visible and self.battle_pokemonstat:
                # Apply fade-out alpha during black background fade-in
                if self.end_scene_black_bg_active and self.end_scene_elements_fade_alpha < 255:
                    temp_pokemonstat = self.battle_pokemonstat.copy()
                    temp_pokemonstat.set_alpha(self.end_scene_elements_fade_alpha)
                    screen.blit(temp_pokemonstat, (self.battle_pokemonstat_x, self.battle_pokemonstat_y))
                else:
                    screen.blit(self.battle_pokemonstat, (self.battle_pokemonstat_x, self.battle_pokemonstat_y))
                # Draw health bar rectangle on stat PNG: 96x6px (width decreases during end scene), 78px from left, 34px from top
                rect_height = 6
                rect_x = self.battle_pokemonstat_x + 78  # 78px from left
                rect_y = self.battle_pokemonstat_y + 34  # 34px from top
                # Use animated width during end scene, otherwise use full width
                if self.end_scene_active:
                    rect_width = self.end_scene_health_bar_width
                    # Color transitions from green (#70F8A8) to red (#F85838) during end scene
                    health_bar_progress = min(1.0, self.end_scene_health_bar_timer / self.end_scene_health_bar_duration)
                    # Interpolate between green and red
                    green_color = (0x70, 0xF8, 0xA8)  # #70F8A8
                    red_color = (0xF8, 0x58, 0x38)  # #F85838
                    rect_color = (
                        int(green_color[0] + (red_color[0] - green_color[0]) * health_bar_progress),
                        int(green_color[1] + (red_color[1] - green_color[1]) * health_bar_progress),
                        int(green_color[2] + (red_color[2] - green_color[2]) * health_bar_progress)
                    )
                else:
                    rect_width = 96
                    rect_color = (0x70, 0xF8, 0xA8)  # #70F8A8 (green)
                # Only draw if width is greater than 0
                if rect_width > 0:
                    pygame.draw.rect(screen, rect_color, (rect_x, rect_y, rect_width, rect_height))
            
            # Draw battle water (always visible during battle)
            if self.battle_water_visible and self.battle_water:
                # Apply fade-out alpha during black background fade-in
                if self.end_scene_black_bg_active and self.end_scene_elements_fade_alpha < 255:
                    temp_water = self.battle_water.copy()
                    temp_water.set_alpha(self.end_scene_elements_fade_alpha)
                    screen.blit(temp_water, apply_shake_offset(self.battle_water_x, self.battle_water_y))
                else:
                    screen.blit(self.battle_water, apply_shake_offset(self.battle_water_x, self.battle_water_y))
            
            # Draw battle UI elements (order matters - draw in correct z-order)
            # Hide assets if black block is fully faded in
            # Draw battle grass (left side only, above dialog) - lower z-index
            # ALWAYS draw grass - it should remain visible during prompt pulse attack
            if self.battle_grass_visible and self.battle_grass:
                # Apply fade-out alpha during black background fade-in
                if self.end_scene_black_bg_active and self.end_scene_elements_fade_alpha < 255:
                    temp_grass = self.battle_grass.copy()
                    temp_grass.set_alpha(self.end_scene_elements_fade_alpha)
                    screen.blit(temp_grass, apply_shake_offset(self.battle_grass_left_x, self.battle_grass_y))
                else:
                    screen.blit(self.battle_grass, apply_shake_offset(self.battle_grass_left_x, self.battle_grass_y))
            
            # Draw battle venusaur stat PNG (separate image, stays in place on right side - Cursorsaur stat)
            # Drawn after grass so it appears above (higher z-index)
            if self.battle_venu_stat_visible and self.battle_venu_stat:
                # Apply fade-out alpha during black background fade-in
                if self.end_scene_black_bg_active and self.end_scene_elements_fade_alpha < 255:
                    temp_venu_stat = self.battle_venu_stat.copy()
                    temp_venu_stat.set_alpha(self.end_scene_elements_fade_alpha)
                    screen.blit(temp_venu_stat, (self.battle_venu_stat_x, self.battle_venu_stat_y))
                else:
                    screen.blit(self.battle_venu_stat, (self.battle_venu_stat_x, self.battle_venu_stat_y))
                # Draw rectangle on stat PNG: 96x6px, color #70F8A8, 94px from left, 34px from top
                rect_width = 96
                rect_height = 6
                rect_x = self.battle_venu_stat_x + 94  # 94px from left
                rect_y = self.battle_venu_stat_y + 34  # 34px from top
                rect_color = (0x70, 0xF8, 0xA8)  # #70F8A8
                pygame.draw.rect(screen, rect_color, (rect_x, rect_y, rect_width, rect_height))
            
            if not (self.move_used_state == "fading_black" and self.assets_hidden):
            
                # Draw battle trainer (on top of grass, same location, higher z-index)
                # Trainer is directly above dialog, same X position as grass
                if self.battle_trainer_visible and self.battle_trainer_sprites and self.battle_trainer_alpha > 0:
                    frame = min(self.battle_trainer_current_frame, len(self.battle_trainer_sprites) - 1)
                    current_trainer_sprite = self.battle_trainer_sprites[frame]
                    screen.blit(current_trainer_sprite, apply_shake_offset(self.battle_trainer_x, self.battle_trainer_y))
                
                # Draw battle Lugia (on top of water, lower z-index than black box until Y coordinate is updated)
                # Scale by 1.5x, centered left/right on water
                # Draw here when NOT during fading_black, OR during fading_black but Y hasn't been updated yet (below black box)
                if self.battle_lugia_visible and self.battle_lugia and self.battle_water:
                    # Draw Lugia below black box: normal state OR fading_black but Y not updated yet
                    should_draw_below_black = (self.move_used_state != "fading_black") or \
                                             (self.move_used_state == "fading_black" and 
                                              (not hasattr(self, 'lugia_moved_above_screen') or not self.lugia_moved_above_screen))
                    if should_draw_below_black:
                        scaled_lugia = pygame.transform.scale(self.battle_lugia, 
                            (int(self.battle_lugia.get_width() * 1.5), int(self.battle_lugia.get_height() * 1.5)))
                        # Use battle_lugia_x and battle_lugia_y directly (slides in from right, positioned on water)
                        lugia_x = self.battle_lugia_x
                        scaled_lugia_y = self.battle_lugia_y
                        # Store center point for rotation (only used for screen shake)
                        lugia_center_x = lugia_x + scaled_lugia.get_width() // 2
                        lugia_center_y = scaled_lugia_y + scaled_lugia.get_height() // 2
                        # Rotate lugia during shake (side to side) - after Lugia finishes sliding down
                        # No rotation during end scene fall (just slides down and fades)
                        if self.screen_shake_active and abs(self.lugia_rotation_angle) > 0.1 and not (self.end_scene_active and self.end_scene_health_bar_timer >= self.end_scene_health_bar_duration):
                            scaled_lugia = pygame.transform.rotate(scaled_lugia, self.lugia_rotation_angle)
                            # Adjust position to keep center point after rotation
                            rotated_rect = scaled_lugia.get_rect(center=(lugia_center_x, lugia_center_y))
                            lugia_x = rotated_rect.x
                            scaled_lugia_y = rotated_rect.y
                        # Apply alpha for end scene fade-out or fade-in during move-back
                        if self.end_scene_active and self.end_scene_health_bar_timer >= self.end_scene_health_bar_duration:
                            # Use end scene fade-out alpha
                            scaled_lugia.set_alpha(self.end_scene_lugia_fall_alpha)
                        elif self.battle_lugia_alpha < 255:
                            scaled_lugia.set_alpha(self.battle_lugia_alpha)
                        else:
                            scaled_lugia.set_alpha(255)
                        # Apply shake offset after Lugia finishes sliding down (but not during end scene fall)
                        if self.screen_shake_active and not (self.end_scene_active and self.end_scene_health_bar_timer >= self.end_scene_health_bar_duration):
                            screen.blit(scaled_lugia, apply_shake_offset(lugia_x, scaled_lugia_y))
                        else:
                            screen.blit(scaled_lugia, (lugia_x, scaled_lugia_y))
                
            # Z-INDEX ORDER (from lowest to highest):
            # 1. Venusaur GIF (drawn first)
            # 2. Dialog Box (drawn second)
            # 3. Fight UI (drawn third, highest z-index)
            
            # Draw battle venusaur GIF (lowest z-index - under dialog and fight UI)
            # Only draw here if NOT during black box fade-in (will be drawn again after black box during fade-in)
            # Same render order as when battle first starts: venusaur before dialog
            if self.battle_venu_visible and self.battle_venu and self.battle_grass:
                # Draw venusaur before dialog when not during fading_black (same as initial battle state)
                if self.move_used_state != "fading_black":
                    # Normal rendering: draw venusaur before dialog (so it's under dialog)
                    # This is the same behavior as when battle first starts
                    scaled_venu = pygame.transform.scale(self.battle_venu, 
                        (int(self.battle_venu.get_width() * 2.0), int(self.battle_venu.get_height() * 2.0)))
                    # Normal: center on current grass position
                    grass_center_x = self.battle_grass_left_x + (self.battle_grass.get_width() // 2)
                    venu_x = grass_center_x - (scaled_venu.get_width() // 2)
                    # Apply fade-out alpha during black background fade-in
                    if self.end_scene_black_bg_active and self.end_scene_elements_fade_alpha < 255:
                        scaled_venu.set_alpha(self.end_scene_elements_fade_alpha)
                    screen.blit(scaled_venu, (venu_x, self.battle_venu_y))
                    
                    # Draw prompt pulse charge sprite above venusaur (when attack sequence begins, higher z-index)
                    if self.venusaur_centered and not self.prompt_pulse_charge_complete and len(self.prompt_pulse_charge_frames) > 0:
                        charge_frame = self.prompt_pulse_charge_frames[self.prompt_pulse_charge_current_frame]
                        # Position above venusaur (centered horizontally, 40px down from top of venusaur)
                        charge_x = venu_x + (scaled_venu.get_width() // 2) - (charge_frame.get_width() // 2)
                        charge_y = self.battle_venu_y - charge_frame.get_height() + 40  # 40px down from above venusaur
                        screen.blit(charge_frame, (charge_x, charge_y))
            
            # Draw battle dialog (middle z-index - above venusaur, below fight UI)
            # Show move used dialog if sliding down, in dialog_showing state, or showing "Bugia fainted!" text
            if ((self.move_used_state == "sliding_down" or self.move_used_state == "dialog_showing") and self.move_used_dialog_text) or \
               (self.end_scene_fainted_text_active and self.move_used_dialog_text):
                # Show dialog with move used text
                screen.blit(self.battle_dialog, (self.battle_dialog_x, self.battle_dialog_y))
                # Draw dialog text - left aligned like other dialog texts (32px from left, vertically centered)
                dialog_text_surface = self.dialog_font.render(self.move_used_dialog_text, True, (255, 255, 255))  # White text
                text_x = self.battle_dialog_x + 32  # 32px from left of dialog
                text_y = self.battle_dialog_y + (self.battle_dialog.get_height() - dialog_text_surface.get_height()) // 2  # Vertically centered
                screen.blit(dialog_text_surface, (text_x, text_y))
            elif self.battle_dialog_visible and self.battle_dialog:
                # Draw battle dialog (always visible during battle)
                # Apply fade alpha to dialog (for initial fade in or end scene fade-out)
                dialog_alpha = int(self.battle_dialog_alpha)
                if self.end_scene_black_bg_active and self.end_scene_elements_fade_alpha < 255:
                    # Use end scene fade-out alpha (overrides initial fade-in alpha)
                    dialog_alpha = min(dialog_alpha, self.end_scene_elements_fade_alpha)
                if dialog_alpha < 255:
                    temp_dialog = self.battle_dialog.copy()
                    temp_dialog.set_alpha(dialog_alpha)
                    screen.blit(temp_dialog, (self.battle_dialog_x, self.battle_dialog_y))
                else:
                    screen.blit(self.battle_dialog, (self.battle_dialog_x, self.battle_dialog_y))
                
                # Draw battle dialog text
                # Starts with "A wild Bugia appeared!" then fades to "What should Venusaur do?" when venusaur slides in
                # Same font/size as Lugia text (32px Pokemon pixel font)
                # Width: half of dialog box/screen, closer to left, white text
                # Check if dialog is fully visible
                dialog_fully_visible = self.battle_dialog_alpha >= 255
                if dialog_fully_visible:  # Only draw text when dialog is fully visible
                    # Text width should be half of dialog box/screen
                    max_text_width = Config.SCREEN_WIDTH // 2
                    
                    # Position: slightly to the right (32px from left), vertically centered
                    text_x = 32  # Slightly to the right
                    dialog_height = self.battle_dialog.get_height()
                    
                    # Show "A wild Bugia appeared!" initially, or "Cursaur used Prompt Pulse!" after attack is used
                    # Only show move used text if it's set (after Prompt Pulse is used)
                    if self.move_used_dialog_text:
                        # Show move used text after Prompt Pulse is used (stays until reset)
                        bugia_line1_text = self.move_used_dialog_text
                        bugia_line2_text = ""  # Empty for single line
                    else:
                        # Show "A wild Bugia appeared!" initially (before attack is used)
                        bugia_line1_text = "A wild Bugia"
                        bugia_line2_text = "appeared!"
                    
                    bugia_line1_surface = self.dialog_font.render(bugia_line1_text, True, (255, 255, 255))  # White text
                    # Only render line2 if it's not empty (for single line move used text)
                    if bugia_line2_text:
                        bugia_line2_surface = self.dialog_font.render(bugia_line2_text, True, (255, 255, 255))  # White text
                    else:
                        bugia_line2_surface = None
                    
                    # Scale down if needed
                    if bugia_line1_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / bugia_line1_surface.get_width()
                        new_width = int(bugia_line1_surface.get_width() * scale_factor)
                        new_height = int(bugia_line1_surface.get_height() * scale_factor)
                        bugia_line1_surface = pygame.transform.scale(bugia_line1_surface, (new_width, new_height))
                    
                    if bugia_line2_surface and bugia_line2_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / bugia_line2_surface.get_width()
                        new_width = int(bugia_line2_surface.get_width() * scale_factor)
                        new_height = int(bugia_line2_surface.get_height() * scale_factor)
                        bugia_line2_surface = pygame.transform.scale(bugia_line2_surface, (new_width, new_height))
                    
                    # Render Cursorsaur text ("What should Cursorsaur do?", "You can't run away!", or "Your Cursorsaur already has full HP!")
                    if self.full_hp_text_visible or self.full_hp_text_alpha > 0:
                        # Show "Your Cursorsaur already has full HP!" text
                        cursorsaur_line1_text = "Your Cursorsaur"
                        cursorsaur_line2_text = "already has full HP!"
                    elif self.run_text_visible or self.run_text_alpha > 0:
                        # Show "You can't run away!" text
                        cursorsaur_line1_text = "You can't"
                        cursorsaur_line2_text = "run away!"
                    else:
                        # Normal text
                        cursorsaur_line1_text = "What should"
                        cursorsaur_line2_text = "Cursorsaur do?"
                    cursorsaur_line1_surface = self.dialog_font.render(cursorsaur_line1_text, True, (255, 255, 255))  # White text
                    cursorsaur_line2_surface = self.dialog_font.render(cursorsaur_line2_text, True, (255, 255, 255))  # White text
                    
                    # Scale down if needed
                    if cursorsaur_line1_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / cursorsaur_line1_surface.get_width()
                        new_width = int(cursorsaur_line1_surface.get_width() * scale_factor)
                        new_height = int(cursorsaur_line1_surface.get_height() * scale_factor)
                        cursorsaur_line1_surface = pygame.transform.scale(cursorsaur_line1_surface, (new_width, new_height))
                    
                    if cursorsaur_line2_surface.get_width() > max_text_width:
                        scale_factor = max_text_width / cursorsaur_line2_surface.get_width()
                        new_width = int(cursorsaur_line2_surface.get_width() * scale_factor)
                        new_height = int(cursorsaur_line2_surface.get_height() * scale_factor)
                        cursorsaur_line2_surface = pygame.transform.scale(cursorsaur_line2_surface, (new_width, new_height))
                    
                    # Calculate total height (single line or two lines)
                    if bugia_line2_surface:
                        total_text_height = bugia_line1_surface.get_height() + bugia_line2_surface.get_height()
                    else:
                        total_text_height = bugia_line1_surface.get_height()
                    line1_y = self.battle_dialog_y + (dialog_height - total_text_height) // 2
                    line2_y = line1_y + bugia_line1_surface.get_height()
                    
                    # Only show ONE text at a time in the dialog box
                    # Priority: move_used_dialog_text (if set) > normal battle text
                    if self.move_used_dialog_text:
                        # Show "Cursaur used Prompt Pulse!" at full opacity (stays until reset)
                        screen.blit(bugia_line1_surface, (text_x, line1_y))
                        if bugia_line2_surface:
                            screen.blit(bugia_line2_surface, (text_x, line2_y))
                    else:
                        # Show normal battle text (either Bugia or Cursaur text based on alpha)
                        # Draw Bugia text with fade
                        if self.battle_text_lugia_alpha > 0:
                            # Show text with fade
                            temp_bugia_line1 = bugia_line1_surface.copy()
                            temp_bugia_line1.set_alpha(int(self.battle_text_lugia_alpha))
                            screen.blit(temp_bugia_line1, (text_x, line1_y))
                            
                            # Only draw line2 if it exists
                            if bugia_line2_surface:
                                temp_bugia_line2 = bugia_line2_surface.copy()
                                temp_bugia_line2.set_alpha(int(self.battle_text_lugia_alpha))
                                screen.blit(temp_bugia_line2, (text_x, line2_y))
                        
                        # Draw Cursorsaur text with fade (only if Bugia text is not showing)
                        if self.battle_text_venusaur_alpha > 0 or self.run_text_alpha > 0 or self.full_hp_text_alpha > 0:
                            # Use appropriate alpha based on which text is showing
                            if self.full_hp_text_visible or self.full_hp_text_alpha > 0:
                                # Show "Your Cursorsaur already has full HP!" with fade animation
                                text_alpha = int(self.full_hp_text_alpha)
                            elif self.run_text_visible or self.run_text_alpha > 0:
                                # Show "You can't run away!" with fade animation
                                text_alpha = int(self.run_text_alpha)
                            else:
                                # Normal Cursorsaur text
                                text_alpha = int(self.battle_text_venusaur_alpha)
                            
                            if text_alpha > 0:
                                temp_cursorsaur_line1 = cursorsaur_line1_surface.copy()
                                temp_cursorsaur_line1.set_alpha(text_alpha)
                                screen.blit(temp_cursorsaur_line1, (text_x, line1_y))
                                
                                temp_cursorsaur_line2 = cursorsaur_line2_surface.copy()
                                temp_cursorsaur_line2.set_alpha(text_alpha)
                                screen.blit(temp_cursorsaur_line2, (text_x, line2_y))
            
            # Draw combat UI (above battle dialog, highest z-index)
            if self.combat_ui_visible and self.combat_ui and self.current_screen == "battle":
                combat_ui_x = 0  # Full width at bottom
                combat_ui_y = Config.SCREEN_HEIGHT - self.combat_ui.get_height()
                screen.blit(self.combat_ui, (combat_ui_x, combat_ui_y))
            
            # Draw fight UI (highest z-index - above dialog and venusaur, drawn LAST)
            # Hide fight UI if move is being used (sliding down or dialog showing) or after Prompt Pulse is used
            if (self.move_used_state == "sliding_down" or 
                self.move_used_state == "dialog_showing" or 
                self.move_used_dialog_text):
                # Don't draw fight UI during move used sequence or after Prompt Pulse is used
                pass
            elif self.fight_ui and self.fight_ui_alpha > 0 and self.current_screen == "battle":
                # Draw fight UI image with fade (animates in when Venusaur section animates in)
                if self.fight_ui_alpha < 255:
                    temp_fight_ui = self.fight_ui.copy()
                    temp_fight_ui.set_alpha(self.fight_ui_alpha)
                    screen.blit(temp_fight_ui, (self.fight_ui_x, self.fight_ui_y))
                else:
                    screen.blit(self.fight_ui, (self.fight_ui_x, self.fight_ui_y))
                
                # Draw hover highlight on hovered cell (light blue) or selected cell (when text is showing)
                # Priority: selected cell (when text is showing) > hovered cell
                # Draw highlight BEFORE text so it appears under the text
                cell_to_highlight = None
                if self.fight_ui_selected_cell is not None:
                    # Check if text is still showing for selected cell
                    selected_row, selected_col = self.fight_ui_selected_cell
                    selected_button_index = selected_row * self.fight_ui_grid_cols + selected_col
                    if selected_button_index < len(self.fight_ui_labels):
                        selected_label = self.fight_ui_labels[selected_button_index]
                        # Keep highlighted if RUN text is showing or BAG screen is active (full HP text will be shown)
                        if (selected_label == "RUN" and (self.run_text_visible or self.run_text_alpha > 0)) or \
                           (selected_label == "BAG" and (self.full_hp_text_visible or self.full_hp_text_alpha > 0)):
                            cell_to_highlight = self.fight_ui_selected_cell
                        else:
                            # Text is gone, clear selection
                            self.fight_ui_selected_cell = None
                
                if cell_to_highlight is None:
                    cell_to_highlight = self.fight_ui_hovered_cell
                
                if cell_to_highlight is not None:
                    row, col = cell_to_highlight
                    # Calculate cell position within the image (accounting for padding)
                    cell_x = self.fight_ui_x + self.fight_ui_padding + (col * self.fight_ui_cell_width)
                    cell_y = self.fight_ui_y + self.fight_ui_padding + (row * self.fight_ui_cell_height)
                    # Draw light blue highlight overlay (under the text)
                    highlight_surface = pygame.Surface((self.fight_ui_cell_width, self.fight_ui_cell_height), pygame.SRCALPHA)
                    highlight_surface.fill((173, 216, 230, 128))  # Light blue with transparency
                    screen.blit(highlight_surface, (cell_x, cell_y))
                
                # Draw button labels in each cell (AFTER highlight so text appears on top)
                for row in range(self.fight_ui_grid_rows):
                    for col in range(self.fight_ui_grid_cols):
                        button_index = row * self.fight_ui_grid_cols + col
                        if button_index < len(self.fight_ui_labels):
                            label_text = self.fight_ui_labels[button_index]
                            # Calculate cell center position
                            cell_x = self.fight_ui_x + self.fight_ui_padding + (col * self.fight_ui_cell_width)
                            cell_y = self.fight_ui_y + self.fight_ui_padding + (row * self.fight_ui_cell_height)
                            cell_center_x = cell_x + (self.fight_ui_cell_width // 2)
                            cell_center_y = cell_y + (self.fight_ui_cell_height // 2)
                            
                            # Render label text
                            label_surface = self.fight_ui_font.render(label_text, True, (0, 0, 0))  # Black text
                            label_rect = label_surface.get_rect(center=(cell_center_x, cell_center_y))
                            screen.blit(label_surface, label_rect)
            
            # Draw combat UI (bottom of window, above fight UI and battle dialog, highest z-index)
            # Slide down if move is being used
            if False:  # Removed slide/fade animations
                combat_ui_x = 0  # Full width at bottom
                combat_ui_y = Config.SCREEN_HEIGHT - self.combat_ui.get_height() + self.move_used_ui_slide_y
                if combat_ui_y < Config.SCREEN_HEIGHT and self.combat_ui:  # Only draw if still visible
                    screen.blit(self.combat_ui, (combat_ui_x, combat_ui_y))
            elif self.combat_ui_visible and self.combat_ui and self.current_screen == "battle":
                combat_ui_x = 0  # Full width at bottom
                combat_ui_y = Config.SCREEN_HEIGHT - self.combat_ui.get_height()
                screen.blit(self.combat_ui, (combat_ui_x, combat_ui_y))
                
                # Left grid: Draw move labels and hover highlights
                left_grid_x = combat_ui_x + self.combat_ui_padding
                left_grid_y = combat_ui_y + self.combat_ui_padding
                
                # Draw move labels in left grid
                for row in range(self.combat_ui_left_grid_rows):
                    for col in range(self.combat_ui_left_grid_cols):
                        move_index = row * self.combat_ui_left_grid_cols + col
                        if move_index < len(self.combat_ui_move_labels):
                            move_name = self.combat_ui_move_labels[move_index]
                            # Calculate cell center position
                            cell_x = left_grid_x + (col * self.combat_ui_left_cell_width)
                            cell_y = left_grid_y + (row * self.combat_ui_left_cell_height)
                            cell_center_x = cell_x + (self.combat_ui_left_cell_width // 2)
                            cell_center_y = cell_y + (self.combat_ui_left_cell_height // 2)
                            
                            # Render move name text (all caps) with outline for visibility
                            move_text_upper = move_name.upper()
                            # Determine text color (grey for first 3 moves, black for Prompt Pulse)
                            if move_name in ["Context Recall", "Syntax Slash", "Debug Dash"]:
                                text_color = (128, 128, 128)  # Grey
                            else:
                                text_color = (0, 0, 0)  # Black
                            
                            # Render text with outline (white outline for visibility)
                            outline_color = (255, 255, 255)  # White outline
                            outline_width = 2
                            # Create a larger surface to accommodate outline
                            temp_surface = pygame.Surface((self.combat_ui_font.size(move_text_upper)[0] + outline_width * 2,
                                                          self.combat_ui_font.size(move_text_upper)[1] + outline_width * 2), pygame.SRCALPHA)
                            # Render outline by drawing text in multiple positions
                            for dx in range(-outline_width, outline_width + 1):
                                for dy in range(-outline_width, outline_width + 1):
                                    if dx != 0 or dy != 0:
                                        outline_surface = self.combat_ui_font.render(move_text_upper, True, outline_color)
                                        temp_surface.blit(outline_surface, (outline_width + dx, outline_width + dy))
                            # Render main text on top
                            main_surface = self.combat_ui_font.render(move_text_upper, True, text_color)
                            temp_surface.blit(main_surface, (outline_width, outline_width))
                            # Center and blit
                            move_text_rect = temp_surface.get_rect(center=(cell_center_x, cell_center_y))
                            screen.blit(temp_surface, move_text_rect)
                
                # Draw hover highlight on left grid (only left grid has hover)
                if self.combat_ui_hovered_cell is not None:
                    grid_side, row, col = self.combat_ui_hovered_cell
                    if grid_side == "left":
                        cell_x = left_grid_x + (col * self.combat_ui_left_cell_width)
                        cell_y = left_grid_y + (row * self.combat_ui_left_cell_height)
                        highlight_surface = pygame.Surface((self.combat_ui_left_cell_width, self.combat_ui_left_cell_height), pygame.SRCALPHA)
                        highlight_surface.fill((173, 216, 230, 128))  # Light blue with transparency
                        screen.blit(highlight_surface, (cell_x, cell_y))
                
                # Right grid: Draw move details (updates based on left grid hover)
                right_grid_x = combat_ui_x + self.combat_ui.get_width() - self.combat_ui_padding - self.combat_ui_right_grid_content_width
                right_grid_y = combat_ui_y + self.combat_ui_padding
                
                # Get selected move from left grid hover
                selected_move = None
                if self.combat_ui_hovered_cell is not None:
                    grid_side, row, col = self.combat_ui_hovered_cell
                    if grid_side == "left":
                        move_index = row * self.combat_ui_left_grid_cols + col
                        if move_index < len(self.combat_ui_move_labels):
                            selected_move = self.combat_ui_move_labels[move_index]
                
                # Draw right grid text
                if selected_move and selected_move in self.combat_ui_move_details:
                    move_details = self.combat_ui_move_details[selected_move]
                    
                    # Helper function to render text with white outline
                    def render_text_with_outline(text, color, x, y, align_right=False):
                        outline_color = (255, 255, 255)  # White outline
                        outline_width = 2
                        text_surface = self.combat_ui_font.render(text, True, color)
                        # Create surface with outline
                        temp_surface = pygame.Surface((text_surface.get_width() + outline_width * 2,
                                                      text_surface.get_height() + outline_width * 2), pygame.SRCALPHA)
                        # Render outline
                        for dx in range(-outline_width, outline_width + 1):
                            for dy in range(-outline_width, outline_width + 1):
                                if dx != 0 or dy != 0:
                                    outline_surface = self.combat_ui_font.render(text, True, outline_color)
                                    temp_surface.blit(outline_surface, (outline_width + dx, outline_width + dy))
                        # Render main text
                        temp_surface.blit(text_surface, (outline_width, outline_width))
                        # Calculate position
                        if align_right:
                            text_rect = temp_surface.get_rect()
                            blit_x = x - text_rect.width
                            blit_y = y - (text_rect.height // 2)
                        else:
                            blit_y = y - (temp_surface.get_height() // 2)
                            blit_x = x
                        screen.blit(temp_surface, (blit_x, blit_y))
                    
                    # Top left cell: "PP" (left aligned, 8px from left, center height)
                    top_left_cell_x = right_grid_x + 8  # 8px from left
                    top_left_cell_y = right_grid_y
                    top_left_cell_center_y = top_left_cell_y + (self.combat_ui_right_cell_height // 2)
                    render_text_with_outline("PP", (0, 0, 0), top_left_cell_x, top_left_cell_center_y)
                    
                    # Top right cell: "# / #" (right aligned, 8px from right, center height)
                    # Top right cell is in column 1 (second column)
                    # Column 1 starts at: right_grid_x + self.combat_ui_right_cell_width
                    # Right edge of column 1: right_grid_x + 2 * self.combat_ui_right_cell_width
                    # 8px from right edge: right_grid_x + 2 * self.combat_ui_right_cell_width - 8
                    top_right_cell_x = right_grid_x + (2 * self.combat_ui_right_cell_width) - 8
                    top_right_cell_y = right_grid_y
                    top_right_cell_center_y = top_right_cell_y + (self.combat_ui_right_cell_height // 2)
                    # PP should be 0 / # for all moves except Prompt Pulse which is 1 / #
                    if selected_move == "Prompt Pulse":
                        pp_text = f"1 / {move_details['pp_max']}"
                    else:
                        pp_text = f"0 / {move_details['pp_max']}"
                    render_text_with_outline(pp_text, (0, 0, 0), top_right_cell_x, top_right_cell_center_y, align_right=True)
                    
                    # Bottom left cell: "TYPE/" (left aligned, 8px from left, center height)
                    bottom_left_cell_x = right_grid_x + 8  # 8px from left
                    bottom_left_cell_y = right_grid_y + self.combat_ui_right_cell_height
                    bottom_left_cell_center_y = bottom_left_cell_y + (self.combat_ui_right_cell_height // 2)
                    render_text_with_outline("TYPE/", (0, 0, 0), bottom_left_cell_x, bottom_left_cell_center_y)
                    
                    # Bottom right cell: "TYPENAME" (right aligned, 8px from right, center height)
                    # Bottom right cell is in column 1 (second column)
                    # Column 1 starts at: right_grid_x + self.combat_ui_right_cell_width
                    # Right edge of column 1: right_grid_x + 2 * self.combat_ui_right_cell_width
                    # 8px from right edge: right_grid_x + 2 * self.combat_ui_right_cell_width - 8
                    bottom_right_cell_x = right_grid_x + (2 * self.combat_ui_right_cell_width) - 8
                    bottom_right_cell_y = right_grid_y + self.combat_ui_right_cell_height
                    bottom_right_cell_center_y = bottom_right_cell_y + (self.combat_ui_right_cell_height // 2)
                    type_name = move_details['type']  # Remove brackets
                    render_text_with_outline(type_name, (0, 0, 0), bottom_right_cell_x, bottom_right_cell_center_y, align_right=True)
                else:
                    # No move selected, show default/empty
                    # Helper function to render text with white outline
                    def render_text_with_outline(text, color, x, y):
                        outline_color = (255, 255, 255)  # White outline
                        outline_width = 2
                        text_surface = self.combat_ui_font.render(text, True, color)
                        # Create surface with outline
                        temp_surface = pygame.Surface((text_surface.get_width() + outline_width * 2,
                                                      text_surface.get_height() + outline_width * 2), pygame.SRCALPHA)
                        # Render outline
                        for dx in range(-outline_width, outline_width + 1):
                            for dy in range(-outline_width, outline_width + 1):
                                if dx != 0 or dy != 0:
                                    outline_surface = self.combat_ui_font.render(text, True, outline_color)
                                    temp_surface.blit(outline_surface, (outline_width + dx, outline_width + dy))
                        # Render main text
                        temp_surface.blit(text_surface, (outline_width, outline_width))
                        blit_y = y - (temp_surface.get_height() // 2)
                        screen.blit(temp_surface, (x, blit_y))
                    
                    # Top left: "PP" (8px from left, center height)
                    top_left_cell_x = right_grid_x + 8  # 8px from left
                    top_left_cell_y = right_grid_y
                    top_left_cell_center_y = top_left_cell_y + (self.combat_ui_right_cell_height // 2)
                    render_text_with_outline("PP", (0, 0, 0), top_left_cell_x, top_left_cell_center_y)
                    
                    # Bottom left: "TYPE/" (8px from left, center height)
                    bottom_left_cell_x = right_grid_x + 8  # 8px from left
                    bottom_left_cell_y = right_grid_y + self.combat_ui_right_cell_height
                    bottom_left_cell_center_y = bottom_left_cell_y + (self.combat_ui_right_cell_height // 2)
                    render_text_with_outline("TYPE/", (0, 0, 0), bottom_left_cell_x, bottom_left_cell_center_y)
            
            # Draw bag screen (when BAG button is clicked)
            if self.current_screen == "bag" and self.bag_screen:
                # Scale bag screen to screen size if needed
                if self.bag_screen.get_width() != Config.SCREEN_WIDTH or self.bag_screen.get_height() != Config.SCREEN_HEIGHT:
                    scaled_bag = pygame.transform.scale(self.bag_screen, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                    screen.blit(scaled_bag, (0, 0))
                else:
                    screen.blit(self.bag_screen, (0, 0))
                
                # Draw "Use" text box (22px from bottom, 8px from right, 96x21, center aligned)
                text_box_x = Config.SCREEN_WIDTH - self.screen_text_box_right_offset - self.screen_text_box_width
                text_box_y = Config.SCREEN_HEIGHT - self.screen_text_box_bottom_offset - self.screen_text_box_height
                
                # Draw transparent black background on hover (1px taller from top and bottom)
                if self.screen_text_hovered:
                    bg_surface = pygame.Surface((self.screen_text_box_width, self.screen_text_box_height + 2), pygame.SRCALPHA)
                    bg_surface.fill((0, 0, 0, 64))  # Transparent black (lower opacity)
                    screen.blit(bg_surface, (text_box_x, text_box_y - 1))  # 1px taller from top
                
                # Draw "USE" text (center aligned, white, all caps)
                use_text = self.screen_text_font.render("USE", True, (255, 255, 255))
                text_rect = use_text.get_rect(center=(text_box_x + self.screen_text_box_width // 2, 
                                                      text_box_y + self.screen_text_box_height // 2))
                screen.blit(use_text, text_rect)
                
                return  # Skip drawing battle elements when bag screen is shown
            
            # Draw pokemon screen (when POKEMON button is clicked)
            if self.current_screen == "pokemon" and self.pokemon_screen:
                # Scale pokemon screen to screen size if needed
                if self.pokemon_screen.get_width() != Config.SCREEN_WIDTH or self.pokemon_screen.get_height() != Config.SCREEN_HEIGHT:
                    scaled_pokemon = pygame.transform.scale(self.pokemon_screen, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                    screen.blit(scaled_pokemon, (0, 0))
                else:
                    screen.blit(self.pokemon_screen, (0, 0))
                
                # Draw "Return" text box (22px from bottom, 8px from right, 96x21, center aligned)
                text_box_x = Config.SCREEN_WIDTH - self.screen_text_box_right_offset - self.screen_text_box_width
                text_box_y = Config.SCREEN_HEIGHT - self.screen_text_box_bottom_offset - self.screen_text_box_height
                
                # Draw transparent black background on hover (1px taller from top and bottom)
                if self.screen_text_hovered:
                    bg_surface = pygame.Surface((self.screen_text_box_width, self.screen_text_box_height + 2), pygame.SRCALPHA)
                    bg_surface.fill((0, 0, 0, 64))  # Transparent black (lower opacity)
                    screen.blit(bg_surface, (text_box_x, text_box_y - 1))  # 1px taller from top
                
                # Draw "RETURN" text (center aligned, white, all caps)
                return_text = self.screen_text_font.render("RETURN", True, (255, 255, 255))
                text_rect = return_text.get_rect(center=(text_box_x + self.screen_text_box_width // 2, 
                                                         text_box_y + self.screen_text_box_height // 2))
                screen.blit(return_text, text_rect)
                
                return  # Skip drawing battle elements when pokemon screen is shown
            
            # Draw black block or attack_pulse_end.png (covers whole screen, above all text and UI elements)
            # This should be above: dialog text, combat UI, fight UI, and venusaur stat PNG
            if self.move_used_state == "fading_black":
                # Draw black block first (behind attack_pulse_end.png)
                if self.fade_out_after_shake:
                    # Use fade-out alpha for black background during fade-out
                    if self.black_block_fade_out_alpha > 0:
                        black_block = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                        black_block.fill((0, 0, 0))  # Black
                        black_block.set_alpha(int(self.black_block_fade_out_alpha))
                        screen.blit(black_block, (0, 0))
                elif self.black_block_alpha > 0:
                    # Use original black block alpha before fade-out starts
                    black_block = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                    black_block.fill((0, 0, 0))  # Black
                    black_block.set_alpha(int(self.black_block_alpha))
                    screen.blit(black_block, (0, 0))
                
                # After move-back is complete, show attack_pulse_end.png on top of black block
                if self.move_back_complete and self.attack_pulse_end_image:
                    # Scale attack_pulse_end.png to screen size
                    scaled_end = pygame.transform.scale(self.attack_pulse_end_image, 
                        (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                    # Apply fade-out alpha if fade-out has started
                    if self.fade_out_after_shake:
                        scaled_end.set_alpha(self.attack_pulse_end_alpha)
                    screen.blit(scaled_end, apply_shake_offset(0, 0))
            
            # Draw battle Lugia (above black box during fading_black, higher z-index)
            # Scale by 1.5x, centered left/right on water
            # Render above black box only when Y coordinate has been updated (lugia_moved_above_screen is True)
            # No animations except GIF during fading_black
            if self.move_used_state == "fading_black" and self.battle_lugia_visible and self.battle_lugia and self.battle_water:
                # Only draw above black box when Y coordinate has been updated
                if hasattr(self, 'lugia_moved_above_screen') and self.lugia_moved_above_screen:
                    scaled_lugia = pygame.transform.scale(self.battle_lugia, 
                        (int(self.battle_lugia.get_width() * 1.5), int(self.battle_lugia.get_height() * 1.5)))
                    # Use battle_lugia_x and battle_lugia_y directly
                    lugia_x = self.battle_lugia_x
                    scaled_lugia_y = self.battle_lugia_y
                    # Store center point for rotation
                    lugia_center_x = lugia_x + scaled_lugia.get_width() // 2
                    lugia_center_y = scaled_lugia_y + scaled_lugia.get_height() // 2
                    # Rotate lugia during shake (side to side) - after Lugia finishes sliding down
                    if self.screen_shake_active and abs(self.lugia_rotation_angle) > 0.1:
                        scaled_lugia = pygame.transform.rotate(scaled_lugia, self.lugia_rotation_angle)
                        # Adjust position to keep center point after rotation
                        rotated_rect = scaled_lugia.get_rect(center=(lugia_center_x, lugia_center_y))
                        lugia_x = rotated_rect.x
                        scaled_lugia_y = rotated_rect.y
                    # Apply alpha for fade-in during move-back
                    if self.battle_lugia_alpha < 255:
                        scaled_lugia.set_alpha(self.battle_lugia_alpha)
                    else:
                        scaled_lugia.set_alpha(255)
                    # Apply shake offset after Lugia finishes sliding down
                    if self.screen_shake_active:
                        screen.blit(scaled_lugia, apply_shake_offset(lugia_x, scaled_lugia_y))
                    else:
                        screen.blit(scaled_lugia, (lugia_x, scaled_lugia_y))
            
            # Draw battle venusaur GIF (above black box during fade-in, sliding to center)
            # Scale by 2x, positioned 30px lower so bottom is partially cut off by dialog
            # Only draw here during fading_black (normally drawn before dialog)
            if self.move_used_state == "fading_black" and self.battle_venu_visible and self.battle_venu and self.battle_grass:
                scaled_venu = pygame.transform.scale(self.battle_venu, 
                    (int(self.battle_venu.get_width() * 2.0), int(self.battle_venu.get_height() * 2.0)))
                # During fading_black, use battle_venu_x/y for sliding animation
                if hasattr(self, 'battle_venu_x') and hasattr(self, 'battle_venu_y'):
                    # Use the position set during venusaur slide (straight line to center)
                    venu_x = self.battle_venu_x
                    venu_y = self.battle_venu_y
                else:
                    # Fallback: center on current grass position
                    grass_center_x = self.battle_grass_left_x + (self.battle_grass.get_width() // 2)
                    venu_x = grass_center_x - (scaled_venu.get_width() // 2)
                    venu_y = self.battle_venu_y
                # Apply shake offset after Lugia finishes sliding down
                if self.screen_shake_active:
                    screen.blit(scaled_venu, apply_shake_offset(venu_x, venu_y))
                else:
                    screen.blit(scaled_venu, (venu_x, venu_y))
                
                # Draw prompt pulse charge sprite above venusaur (when attack sequence begins, higher z-index)
                # Draw AFTER venusaur so it appears on top (higher z-index)
                if self.venusaur_centered and not self.prompt_pulse_charge_complete and len(self.prompt_pulse_charge_frames) > 0:
                    charge_frame = self.prompt_pulse_charge_frames[self.prompt_pulse_charge_current_frame]
                    # Position above venusaur (centered horizontally, 40px down from top of venusaur)
                    charge_x = venu_x + (scaled_venu.get_width() // 2) - (charge_frame.get_width() // 2)
                    charge_y = venu_y - charge_frame.get_height() + 40  # 40px down from above venusaur
                    # Apply shake offset after Lugia finishes sliding down
                    if self.screen_shake_active:
                        screen.blit(charge_frame, apply_shake_offset(charge_x, charge_y))
                    else:
                        screen.blit(charge_frame, (charge_x, charge_y))
            
            # Draw black background fade-in after Lugia faints (highest z-index, covers everything)
            if self.end_scene_black_bg_active and self.end_scene_black_bg_alpha > 0:
                black_bg = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                black_bg.fill((0, 0, 0))  # Black
                black_bg.set_alpha(int(self.end_scene_black_bg_alpha))
                screen.blit(black_bg, (0, 0))
            
            # Draw end background image (slides in after pokemon shine fades in) - lowest z-index (drawn first)
            if self.end_scene_bg_active and self.end_scene_bg_image:
                screen.blit(self.end_scene_bg_image, (self.end_scene_bg_x, self.end_scene_bg_y))
            
            # Draw press-r SVG (fades in after end_bg, centered x-wise, 10px under end_bg, blinks) - above end_bg
            if self.end_scene_press_r_active and self.end_scene_press_r_image:
                # Use fade-in alpha if still fading, otherwise use blink alpha
                # Always use blink alpha (skip fade-in phase)
                current_alpha = self.end_scene_press_r_blink_alpha
                if current_alpha > 0:
                    temp_press_r = self.end_scene_press_r_image.copy()
                    temp_press_r.set_alpha(int(current_alpha))
                    screen.blit(temp_press_r, (self.end_scene_press_r_x, self.end_scene_press_r_y))
            
            # Draw end Venusaur image (after black background appears) - above end_bg and press-r
            if self.end_scene_venusaur_active and self.end_scene_venusaur_image and self.end_scene_venusaur_fade_alpha > 0:
                # Apply fade-in alpha
                temp_venusaur = self.end_scene_venusaur_image.copy()
                temp_venusaur.set_alpha(int(self.end_scene_venusaur_fade_alpha))
                screen.blit(temp_venusaur, (self.end_scene_venusaur_x, self.end_scene_venusaur_y))
            
            # Draw pokemon shine sprite (fades in when end_venusaur moves right) - above end_venusaur
            if self.end_scene_pokemon_shine_active and self.end_scene_pokemon_shine_frames and self.end_scene_pokemon_shine_fade_alpha > 0:
                # Get current frame
                if len(self.end_scene_pokemon_shine_frames) > 0:
                    current_frame = self.end_scene_pokemon_shine_frames[self.end_scene_pokemon_shine_current_frame]
                    # Apply fade-in alpha
                    temp_shine = current_frame.copy()
                    temp_shine.set_alpha(int(self.end_scene_pokemon_shine_fade_alpha))
                    screen.blit(temp_shine, (self.end_scene_pokemon_shine_x, self.end_scene_pokemon_shine_y))
            
            # Draw cursor-version SVG (fades in after end_bg, centered under pokemon shine) - highest z-index (drawn last)
            if self.end_scene_cursor_active and self.end_scene_cursor_image and self.end_scene_cursor_fade_alpha > 0:
                temp_cursor = self.end_scene_cursor_image.copy()
                temp_cursor.set_alpha(int(self.end_scene_cursor_fade_alpha))
                screen.blit(temp_cursor, (self.end_scene_cursor_x, self.end_scene_cursor_y))
            
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
        
        # DEBUG: Draw walkable areas and edges (for debugging)
        # Hidden by default - set enable_debugging_features = True to show
        if self.enable_debugging_features:
            grid_size = 32
            
            # Helper function to check if a cell is walkable
            def is_cell_walkable(cell_x, cell_y):
                # Check rectangles
                for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                    if min_x <= cell_x <= max_x and min_y <= cell_y <= max_y:
                        return True
                # Check individual cells
                for cell_x_check, cell_y_check in self.walkable_cells:
                    if cell_x == cell_x_check and cell_y == cell_y_check:
                        return True
                return False
            
            # Draw all walkable areas with transparent pink highlight
            pink_surface = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
            pink_surface.fill((255, 192, 203, 128))  # Transparent pink with 50% opacity
            
            # Draw rectangles
            for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                for cell_x in range(min_x, max_x + 1):
                    for cell_y in range(min_y, max_y + 1):
                        # Calculate cell position in world coordinates
                        cell_world_x = cell_x * grid_size
                        cell_world_y = cell_y * grid_size
                        # Calculate screen coordinates
                        cell_screen_x = cell_world_x - self.camera_x
                        cell_screen_y = cell_world_y - self.camera_y
                        # Only draw if on screen
                        if (cell_screen_x + grid_size > 0 and cell_screen_x < Config.SCREEN_WIDTH and
                            cell_screen_y + grid_size > 0 and cell_screen_y < Config.SCREEN_HEIGHT):
                            screen.blit(pink_surface, (cell_screen_x, cell_screen_y))
            
            # Draw individual cells
            for cell_x, cell_y in self.walkable_cells:
                # Calculate cell position in world coordinates
                cell_world_x = cell_x * grid_size
                cell_world_y = cell_y * grid_size
                # Calculate screen coordinates
                cell_screen_x = cell_world_x - self.camera_x
                cell_screen_y = cell_world_y - self.camera_y
                # Only draw if on screen
                if (cell_screen_x + grid_size > 0 and cell_screen_x < Config.SCREEN_WIDTH and
                    cell_screen_y + grid_size > 0 and cell_screen_y < Config.SCREEN_HEIGHT):
                    screen.blit(pink_surface, (cell_screen_x, cell_screen_y))
            
            # Find all edge cells (walkable cells with at least one non-walkable neighbor)
            edge_cells = set()
            
            # Check all cells in rectangles
            for min_x, min_y, max_x, max_y in self.walkable_rectangles:
                for cell_x in range(min_x, max_x + 1):
                    for cell_y in range(min_y, max_y + 1):
                        if is_cell_walkable(cell_x, cell_y):
                            # Check if this cell is on the edge (has at least one non-walkable neighbor)
                            is_edge = False
                            # Check 4 neighbors: up, down, left, right
                            neighbors = [
                                (cell_x, cell_y - 1),  # Up
                                (cell_x, cell_y + 1),  # Down
                                (cell_x - 1, cell_y),  # Left
                                (cell_x + 1, cell_y),  # Right
                            ]
                            for nx, ny in neighbors:
                                if not is_cell_walkable(nx, ny):
                                    is_edge = True
                                    break
                            if is_edge:
                                edge_cells.add((cell_x, cell_y))
            
            # Individual cells are always edges
            for cell_x, cell_y in self.walkable_cells:
                edge_cells.add((cell_x, cell_y))
            
            # Draw only edge cells with yellow highlight (on top of pink)
            yellow_surface = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
            yellow_surface.fill((255, 255, 0, 128))  # Yellow with 50% opacity
            
            for cell_x, cell_y in edge_cells:
                # Calculate cell position in world coordinates
                cell_world_x = cell_x * grid_size
                cell_world_y = cell_y * grid_size
                # Calculate screen coordinates
                cell_screen_x = cell_world_x - self.camera_x
                cell_screen_y = cell_world_y - self.camera_y
                # Only draw if on screen
                if (cell_screen_x + grid_size > 0 and cell_screen_x < Config.SCREEN_WIDTH and
                    cell_screen_y + grid_size > 0 and cell_screen_y < Config.SCREEN_HEIGHT):
                    screen.blit(yellow_surface, (cell_screen_x, cell_screen_y))
        
        # Draw exclamation (when character touches Lugia hitbox) - clipped to character's cell and cell above, but not by cells to left/right
        if self.exclamation_visible and self.exclamation_image:
            grid_size = 32
            # Calculate character's cell bounds
            player_cell_x = (self.player_world_x + self.player_width // 2) // grid_size
            player_cell_y = (self.player_world_y + self.player_height // 2) // grid_size
            # Calculate cell bounds in world coordinates
            char_cell_world_x = player_cell_x * grid_size
            char_cell_world_y = player_cell_y * grid_size
            cell_above_world_y = (player_cell_y - 1) * grid_size
            # Calculate screen coordinates
            char_cell_screen_x = char_cell_world_x - self.camera_x
            char_cell_screen_y = char_cell_world_y - self.camera_y
            cell_above_screen_y = cell_above_world_y - self.camera_y
            # Clipping rectangle: character's cell and cell above (2 cells tall), but full width to avoid cutting off sides
            # Use a wide enough area to include the exclamation image without horizontal clipping
            clip_rect = pygame.Rect(char_cell_screen_x - grid_size, cell_above_screen_y, grid_size * 3, grid_size * 2)
            
            # Calculate exclamation screen position
            exclamation_screen_x = self.exclamation_x - self.camera_x
            exclamation_screen_y = self.exclamation_y - self.camera_y
            
            # Only draw if exclamation overlaps with clip area
            exclamation_rect = pygame.Rect(exclamation_screen_x, exclamation_screen_y, 
                                         self.exclamation_image.get_width(), self.exclamation_image.get_height())
            if exclamation_rect.colliderect(clip_rect):
                # Save current clip state
                old_clip = screen.get_clip()
                # Set clipping rectangle (only vertically, horizontally allows full width)
                screen.set_clip(clip_rect)
                # Draw with alpha if needed
                if self.exclamation_alpha < 255:
                    temp_exclamation = self.exclamation_image.copy()
                    temp_exclamation.set_alpha(int(self.exclamation_alpha))
                    screen.blit(temp_exclamation, (exclamation_screen_x, exclamation_screen_y))
                else:
                    screen.blit(self.exclamation_image, (exclamation_screen_x, exclamation_screen_y))
                # Restore clip state
                screen.set_clip(old_clip)
        
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
        # Hidden by default - set enable_debugging_features = True to show
        if self.enable_debugging_features:
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
        # Always show WASD instruction
        if not self.dialog_visible:
            font = pygame.font.Font(None, self.debug_font_size)
            wasd_text = font.render("Use WASD or Arrow Keys to move", True, (255, 255, 255))
            wasd_text_rect = wasd_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 20))
            # Draw semi-transparent background for text
            bg_surface = pygame.Surface((wasd_text_rect.width + 10, wasd_text_rect.height + 4))
            bg_surface.set_alpha(128)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, (wasd_text_rect.x - 5, wasd_text_rect.y - 2))
            screen.blit(wasd_text, wasd_text_rect)
        
        # Hidden by default - set enable_debugging_features = True to show cell location
        if not self.dialog_visible and self.enable_debugging_features:
            player_cell_x = (self.player_world_x + self.player_width // 2) // 32
            player_cell_y = (self.player_world_y + self.player_height // 2) // 32
            font = pygame.font.Font(None, self.debug_font_size)
            cell_text = font.render(f"Cell: ({player_cell_x}, {player_cell_y})", True, (255, 255, 255))
            cell_text_rect = cell_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 50))
            # Draw semi-transparent background for text
            bg_surface = pygame.Surface((cell_text_rect.width + 10, cell_text_rect.height + 4))
            bg_surface.set_alpha(128)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, (cell_text_rect.x - 5, cell_text_rect.y - 2))
            screen.blit(cell_text, cell_text_rect)
        
        # Draw dialog box with text (fades out with rest of map, no sliding)
        if self.dialog_visible and self.fade_state != "faded":
            # Only draw if dialog is on screen
            if 0 <= self.dialog_slide_y < Config.SCREEN_HEIGHT:
                # Calculate fade opacity for dialog (same as scene)
                dialog_opacity = scene_opacity
                
                # Draw dialog image if available
                if self.dialog_image:
                    dialog_x = (Config.SCREEN_WIDTH - self.dialog_image.get_width()) // 2  # Center horizontally
                    dialog_y = self.dialog_slide_y  # Stay in same position, no sliding out
                    # Apply fade opacity
                    if dialog_opacity < 255:
                        temp_dialog_img = self.dialog_image.copy()
                        temp_dialog_img.set_alpha(dialog_opacity)
                        screen.blit(temp_dialog_img, (dialog_x, dialog_y))
                    else:
                        screen.blit(self.dialog_image, (dialog_x, dialog_y))
                    
                    # Draw text on top of dialog box (middle left aligned)
                    if self.dialog_text:
                        text_surface = self.dialog_font.render(self.dialog_text, True, (0, 0, 0))
                        # Text position: 48px from left, vertically centered in dialog box
                        text_x = 48  # 48px from left
                        dialog_height = self.dialog_image.get_height()
                        text_y = dialog_y + (dialog_height - text_surface.get_height()) // 2
                        # Apply fade opacity to text
                        if dialog_opacity < 255:
                            temp_text = text_surface.copy()
                            temp_text.set_alpha(dialog_opacity)
                            screen.blit(temp_text, (text_x, text_y))
                        else:
                            screen.blit(text_surface, (text_x, text_y))
                else:
                    # Fallback: just draw text if no dialog image
                    if self.dialog_text:
                        text_surface = self.dialog_font.render(self.dialog_text, True, (0, 0, 0))
                        text_x = 48  # 48px from left
                        text_y = self.dialog_slide_y
                        # Apply fade opacity to text
                        if dialog_opacity < 255:
                            temp_text = text_surface.copy()
                            temp_text.set_alpha(dialog_opacity)
                            screen.blit(temp_text, (text_x, text_y))
                        else:
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
        

