# Web Display Fix

If the game loads but doesn't show the screen in the browser, try these solutions:

## Solution 1: Check Browser Console

Open browser developer tools (F12) and check the Console tab for any errors. Common issues:
- JavaScript errors
- Asset loading failures
- WebAssembly compilation errors

## Solution 2: Wait for Full Load

The game needs to:
1. Download the APK file (may take time)
2. Mount the file system
3. Compile WebAssembly
4. Load all assets

Wait for the progress bar to complete and look for "Ready to start!" message. **You may need to click/tap the page** to enable audio and start the game.

## Solution 3: Check Canvas Visibility

The canvas might be hidden. In browser console, try:
```javascript
document.getElementById('canvas').style.visibility = 'visible'
document.getElementById('canvas').style.display = 'block'
```

## Solution 4: Rebuild with Correct Screen Size

The issue might be that pygbag is using a responsive template. Try rebuilding:

```bash
.venv/bin/python build_web.py
```

Then test again.

## Solution 5: Use fix_display.html

I've created a wrapper HTML file at `build/web/fix_display.html` that properly sizes the game. Try opening that instead of `index.html`.

## Solution 6: Check Screen Size Configuration

Make sure your game screen size (480x320) matches what's expected. The HTML template might need adjustment.

## Debugging Steps

1. **Check if game is running**: Look for console output in browser dev tools
2. **Check canvas element**: Inspect the canvas element - is it visible? What are its dimensions?
3. **Check for errors**: Any red errors in console?
4. **Try different browser**: Chrome, Firefox, Safari
5. **Clear browser cache**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

## Common Issues

- **Black screen**: Game is loading, wait longer
- **White screen**: Check console for errors
- **Tiny screen**: Canvas sizing issue - see Solution 3
- **No response**: Click/tap the page to enable user interaction

