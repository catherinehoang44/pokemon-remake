# Pokemon Remake - React + TypeScript + Canvas

This is a browser-based version of the Pokemon game, converted from Python/Pygame to React + TypeScript with Canvas rendering.

## Features

- **Character Selection**: Choose your character
- **Pokemon Selection**: Choose your starting Pokemon
- **Map Exploration**: Navigate through the game world with scrolling camera
- **Lugia Battle Sequence**: Encounter and battle Lugia with animated sequences
- **Battle UI**: Full battle interface with animations

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. The assets are already copied to `public/assets/` from the original Python project.

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to the URL shown in the terminal (usually `http://localhost:5173`)

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready to be deployed to any static hosting service.

## Controls

- **Arrow Keys** or **WASD**: Move character
- **R**: Restart the current scene
- **Enter** or **Space**: Confirm selection
- **Mouse Click**: Advance dialog/battle sequence

## Project Structure

```
pokemon-remake/
├── src/
│   ├── scenes/          # Game scenes
│   │   ├── CharacterSelectionScene.tsx
│   │   ├── PokemonSelectionScene.tsx
│   │   └── HouseVillageScene.tsx
│   ├── config.ts        # Game configuration
│   ├── utils.ts         # Utility functions (SpriteSheet, AnimatedSprite)
│   ├── scene_manager.ts # Scene management
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── public/
│   └── assets/          # Game assets (images, sounds, sprites, fonts)
└── package.json
```

## Technical Details

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Rendering**: HTML5 Canvas
- **Game Loop**: requestAnimationFrame

## Notes

- The game uses Canvas for rendering, providing pixel-perfect control
- All assets are loaded asynchronously
- The game loop runs at ~60 FPS using requestAnimationFrame
- Sprite animations are handled frame-by-frame with delta time

