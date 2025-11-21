# Web Display Fix - Screen Not Showing

## The Problem

The game loads but the screen doesn't display. This is because pygbag's template creates a loading screen at 10% viewport size, and the actual game screen needs to be properly initialized.

## Solutions

### Solution 1: Wait and Click (Most Common)

1. **Wait for full load** - Look for "Ready to start!" message
2. **Click/tap anywhere on the page** - This enables user interaction
3. The game should then start displaying

### Solution 2: Check Browser Console

1. Open DevTools (F12)
2. Go to Console tab
3. Look for errors or messages
4. Try running this in console:
   ```javascript
   document.getElementById('canvas').style.visibility = 'visible';
   document.getElementById('canvas').style.width = '480px';
   document.getElementById('canvas').style.height = '320px';
   ```

### Solution 3: Use game.html Wrapper

I've created `build/web/game.html` which properly sizes the game. Try opening that instead of `index.html`.

### Solution 4: Rebuild with Debug Mode

Rebuild and check for errors:
```bash
.venv/bin/python build_web.py
```

### Solution 5: Check Canvas Element

In browser DevTools Elements tab:
1. Find `<canvas id="canvas">`
2. Check its computed styles
3. Make sure it's visible and has proper dimensions

## What's Happening

1. **Loading phase**: pygbag creates a small loading screen (10% viewport)
2. **APK download**: Game files download
3. **WebAssembly compile**: Python code compiles to WASM
4. **Asset loading**: Images, sounds load
5. **Game start**: Your game code runs and creates the 480x320 screen
6. **User interaction**: Browser requires click/tap to enable audio/game

The screen should appear after step 5, but you may need to click to enable it.

## Still Not Working?

Check `TROUBLESHOOTING.md` for more detailed debugging steps.

