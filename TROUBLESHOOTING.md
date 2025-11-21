# Troubleshooting Web Display Issues

## Problem: Game loads but screen doesn't show

### Quick Fixes:

1. **Wait for full load** - The game needs time to:
   - Download the APK file
   - Mount the file system  
   - Compile WebAssembly
   - Load all assets
   
   Look for "Ready to start!" message and **click/tap the page** to enable audio.

2. **Check browser console** (F12):
   - Look for any red errors
   - Check if assets are loading
   - See if WebAssembly compiled successfully

3. **Try the wrapper HTML**:
   - Open `build/web/game.html` instead of `index.html`
   - This provides proper sizing and display

4. **Check canvas visibility**:
   In browser console, run:
   ```javascript
   document.getElementById('canvas').style.visibility = 'visible'
   document.getElementById('canvas').style.width = '480px'
   document.getElementById('canvas').style.height = '320px'
   ```

5. **Clear browser cache**:
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or clear cache in browser settings

### Common Issues:

**Black/blank screen:**
- Game is still loading - wait 10-30 seconds
- Check console for loading progress
- Make sure you clicked/tapped to enable interaction

**Tiny screen:**
- Canvas sizing issue
- Try the canvas visibility fix above
- Or use `game.html` wrapper

**No response:**
- Click/tap anywhere on the page first
- Some browsers require user interaction before starting

**Audio doesn't work:**
- Click/tap the page first (browser autoplay policy)
- Check browser console for audio errors

### Debug Steps:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for:
   - "Loading cursor-test from cursor-test.apk"
   - "Ready to start!"
   - Any red error messages
4. Go to Network tab:
   - Check if `cursor-test.apk` downloaded
   - Check if all assets loaded (images, sounds)
5. Go to Elements tab:
   - Find `<canvas id="canvas">`
   - Check its computed size and visibility

### Still Not Working?

1. **Rebuild the game:**
   ```bash
   .venv/bin/python build_web.py
   ```

2. **Try different browser:**
   - Chrome (recommended)
   - Firefox
   - Safari
   - Edge

3. **Check file permissions:**
   - Make sure all files in `build/web/` are readable
   - Check web server configuration

4. **Test locally first:**
   ```bash
   .venv/bin/python serve_web.py
   ```
   Then visit `http://localhost:8000`

### Technical Details:

The game uses:
- **Screen size**: 480x320 pixels
- **WebAssembly**: Compiled Python code
- **Canvas rendering**: HTML5 canvas element
- **File system**: Virtual file system mounted from APK

The canvas should be visible and sized to 480x320. If it's not showing, it's usually a sizing or visibility CSS issue.

