/**
 * Game configuration settings
 */

export const Config = {
  // Screen settings
  SCREEN_WIDTH: 480,
  SCREEN_HEIGHT: 320,
  FPS: 60,

  // Colors (Pokemon-style palette)
  BG_COLOR: [135, 206, 235] as [number, number, number], // Sky blue background
  WHITE: [255, 255, 255] as [number, number, number],
  BLACK: [0, 0, 0] as [number, number, number],
  GRAY: [128, 128, 128] as [number, number, number],
  DARK_GRAY: [64, 64, 64] as [number, number, number],
  RED: [255, 0, 0] as [number, number, number],
  GREEN: [0, 255, 0] as [number, number, number],
  BLUE: [0, 0, 255] as [number, number, number],

  // Game settings
  GAME_TITLE: "Pokemon: Cursor Version",

  // Tile size for pixel art (16x16 or 32x32)
  TILE_SIZE: 32,

  // Player movement speed
  PLAYER_SPEED: 3,

  // Paths
  ASSETS_PATH: "/assets",
  SPRITES_PATH: "/assets/sprites",
  IMAGES_PATH: "/assets/images",
  SOUNDS_PATH: "/assets/sounds",
  FONTS_PATH: "/assets/fonts",
};

