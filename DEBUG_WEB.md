# Debugging Web Display - "Loads but Nothing Happens"

## What to Check

### Step 1: Open Browser Console (F12)

After the game loads, check the Console tab for:

1. **Look for these messages:**
   - "Loading cursor-test from cursor-test.apk" ✓
   - "Ready to start !" ✓
   - "* Waiting for media user engagement : please click/touch page *" ✓
   - "Starting game..." (NEW - should appear after you click)
   - "Initializing pygame..." (NEW)
   - "Creating screen: 480x320" (NEW)
   - "Screen created successfully" (NEW)
   - "Game running... frame 60" (NEW - appears every second)

2. **Look for errors:**
   - Any red error messages?
   - Import errors?
   - File not found errors?

### Step 2: After Loading Completes

1. **Click/tap anywhere on the page** - This is REQUIRED!
2. Watch the console for the debug messages above
3. The game should start displaying

### Step 3: If Still Nothing Happens

Check the console for:
- Does "Starting game..." appear after clicking?
- Any error messages?
- Does the canvas element exist? (Check Elements tab)

### Step 4: Manual Canvas Check

In browser console, run:
```javascript
// Check if canvas exists
const canvas = document.getElementById('canvas');
console.log('Canvas:', canvas);
console.log('Canvas size:', canvas?.width, 'x', canvas?.height);
console.log('Canvas visible:', canvas?.style.visibility);
console.log('Canvas display:', canvas?.style.display);

// Force visibility
if (canvas) {
    canvas.style.visibility = 'visible';
    canvas.style.display = 'block';
    canvas.style.width = '480px';
    canvas.style.height = '320px';
}
```

### Step 5: Check Network Tab

1. Open DevTools → Network tab
2. Refresh the page
3. Check if `cursor-test.apk` downloaded successfully
4. Check if all assets loaded (images, sounds)

## Common Issues

**"Ready to start!" but nothing after click:**
- Check console for errors
- The game code might be failing to initialize
- Look for Python traceback errors

**No "Starting game..." message:**
- The click might not be registering
- Try clicking multiple times
- Check if UME (User Media Engagement) is being detected

**Canvas exists but is tiny/invisible:**
- Run the manual canvas check above
- The screen might be created but not visible

## Next Steps

After checking the console, share:
1. What messages you see (or don't see)
2. Any error messages
3. Whether "Starting game..." appears after clicking

This will help diagnose the exact issue!

