# Pokemon-style 2D Pixel Art Game

A 2D pixel art game recreating the first few scenes from Pokémon, including character selection, house/village exploration, and Pokémon selection.

## Features

- **Character Selection**: Choose your character
- **Map Exploration**: Explore a village with scrolling camera
- **Lugia Encounter**: Special sequence with Lugia flying in and animating
- **Dialog System**: Pokemon-style dialog box with pixel font
- **Fade Transitions**: Smooth transitions between scenes
- **Water Collision**: Lake areas are unwalkable (4 cells from left/right)
- **Web Compatible**: Can be built and played in a web browser

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

### Desktop Mode
```bash
python main.py
```

### Web/Browser Mode
1. Build for web:
```bash
python build_web.py
```

2. Serve locally:
```bash
python serve_web.py
```

3. Open your browser to `http://localhost:8000`

## Controls

- **Movement**: WASD or Arrow Keys
- **Restart**: Press R to restart the scene
- **Dialog**: Click anywhere after dialog appears to continue

## Project Structure

```
cursor-test/
├── main.py                 # Main game entry point
├── config.py              # Game configuration
├── scene_manager.py        # Scene management system
├── utils.py                # Sprite sheet and animation utilities
├── build_web.py            # Script to build game for web
├── serve_web.py            # Script to serve web build locally
├── scenes/
│   ├── __init__.py
│   ├── base_scene.py       # Base class for all scenes
│   ├── character_selection.py
│   ├── house_village.py    # Map exploration with scrolling camera
│   └── pokemon_selection.py
├── assets/                 # Asset folders
│   ├── sprites/           # Sprite images
│   │   ├── character_red.png
│   │   └── lugia.png
│   ├── images/            # Background images
│   │   ├── map_background.png
│   │   ├── dialog.png
│   │   └── fighting_background.png
│   ├── sounds/            # Sound effects and music
│   └── fonts/             # Custom fonts
│       └── pokemon_pixel_font.ttf
├── requirements.txt
└── README.md
```

## Assets Needed

### Required Files:
- `assets/sprites/character_red.png` - Character sprite sheet (4x4 grid, 32x64px per sprite)
- `assets/sprites/lugia.png` - Lugia sprite sheet (all sprites in a row, 132x132px each)
- `assets/images/map_background.png` - Map background image
- `assets/images/dialog.png` - Dialog box image
- `assets/images/fighting_background.png` - Fighting background for fade transition
- `assets/fonts/pokemon_pixel_font.ttf` - Pokemon pixel font

## Game Mechanics

### Map Exploration
- Character stays centered on screen
- Map scrolls as character moves
- Camera stops at map edges

### Water/Lake Collision
- Lake areas are 4 cells (128px) from left and right edges
- Only the middle bridge area is walkable
- Player cannot move into water areas

### Lugia Sequence
1. Player reaches bridge end (1 cell lower than before)
2. Lugia flies in from above (2x faster)
3. Lugia animates through all frames once
4. Dialog box slides up with text
5. Click to fade to fighting background

## Technical Details

- **Screen Size**: 480x320 pixels
- **Frame Rate**: 60 FPS
- **Player Speed**: 3 pixels per frame
- **Grid Size**: 32x32 pixels
- **Lugia Animation Speed**: 0.2

## Web Deployment

### Quick Start

1. **Build for web:**
   ```bash
   python build_web.py
   ```

2. **Test locally:**
   ```bash
   python serve_web.py
   ```

3. **Deploy:** Upload the `web-build/` folder to any web hosting service

### Deployment Options

- **GitHub Pages** (Free) - Upload `web-build/` to a GitHub repo and enable Pages
- **Netlify** (Free) - Drag and drop `web-build/` folder
- **Vercel** (Free) - Use Vercel CLI or web interface
- **Any Web Host** - Upload via FTP/cPanel

### Embedding in Your Website

See `embed_example.html` for a complete example, or check `DEPLOYMENT.md` for detailed instructions.

**Simple embed code:**
```html
<iframe 
    src="path/to/web-build/index.html" 
    width="480" 
    height="320" 
    frameborder="0"
    allow="autoplay">
</iframe>
```

📖 **Full deployment guide:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Notes for Web Version

- The game runs entirely in the browser (no server-side code needed)
- All assets are bundled during the build process
- First load may take a moment as WebAssembly files are downloaded
- Works on modern browsers (Chrome, Firefox, Safari, Edge)
- Audio requires user interaction in some browsers (click/tap to enable)












