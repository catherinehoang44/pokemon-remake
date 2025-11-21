# Deployment Guide - Web Deployment

This guide will help you build and deploy your Pygame game to the web.

## Prerequisites

1. Python 3.9 or higher
2. All dependencies installed: `pip install -r requirements.txt`

## Step 1: Build for Web

Run the build script:

```bash
python build_web.py
```

This will:
- Check if `pygbag` is installed (install if needed)
- Compile your game to WebAssembly
- Create a `web-build/` directory with all necessary files

## Step 2: Test Locally

Before deploying, test the build locally:

```bash
python serve_web.py
```

This will start a local server at `http://localhost:8000` and open it in your browser.

## Step 3: Deploy to Web Hosting

### Option A: GitHub Pages (Free)

1. Create a GitHub repository
2. Copy the contents of `web-build/` to your repository
3. Enable GitHub Pages in repository settings
4. Your game will be available at: `https://yourusername.github.io/repository-name/`

### Option B: Netlify (Free)

1. Sign up at [netlify.com](https://netlify.com)
2. Drag and drop the `web-build/` folder to Netlify
3. Your game will be live immediately with a URL like: `https://random-name.netlify.app`

### Option C: Vercel (Free)

1. Sign up at [vercel.com](https://vercel.com)
2. Install Vercel CLI: `npm i -g vercel`
3. Navigate to `web-build/` directory
4. Run: `vercel`
5. Follow the prompts

### Option D: Any Web Host

Upload the contents of `web-build/` to any web hosting service:
- Upload via FTP/SFTP
- Use cPanel file manager
- Use any static site hosting service

## Step 4: Embed in Your Website

### Simple Embed (Full Page)

Create an HTML file with this content:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Pokemon Adventure Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #87CEEB;
        }
        #game-container {
            border: 2px solid #333;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div id="game-container">
        <iframe 
            src="index.html" 
            width="480" 
            height="320" 
            frameborder="0"
            allow="autoplay"
            style="display: block;">
        </iframe>
    </div>
</body>
</html>
```

### Embed in Existing Website

Add this to your HTML page:

```html
<div id="game-container" style="text-align: center; margin: 20px auto;">
    <iframe 
        src="path/to/web-build/index.html" 
        width="480" 
        height="320" 
        frameborder="0"
        allow="autoplay"
        style="border: 2px solid #333; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    </iframe>
</div>
```

### Responsive Embed (Scales with screen size)

```html
<div id="game-container" style="position: relative; width: 100%; max-width: 480px; margin: 0 auto;">
    <div style="padding-bottom: 66.67%; position: relative; height: 0;">
        <iframe 
            src="index.html" 
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 2px solid #333;"
            frameborder="0"
            allow="autoplay">
        </iframe>
    </div>
</div>
```

## Important Notes

1. **File Size**: The initial load may be large (several MB) due to WebAssembly compilation. Consider:
   - Enabling compression on your web server
   - Using a CDN for faster delivery
   - Adding a loading screen

2. **Browser Compatibility**: 
   - Modern browsers (Chrome, Firefox, Safari, Edge) are supported
   - Mobile browsers may have performance limitations

3. **Audio**: 
   - Some browsers require user interaction before playing audio
   - Make sure users click/tap before expecting sounds

4. **Performance**:
   - First load may take time to compile WebAssembly
   - Subsequent loads will be faster (browser caching)

## Troubleshooting

### Build fails
- Make sure you have Python 3.9+
- Try: `pip install --upgrade pygbag`
- Check that all assets are in the correct paths

### Game doesn't load
- Check browser console for errors
- Ensure all files from `web-build/` are uploaded
- Check that paths are correct (case-sensitive on some servers)

### Audio doesn't work
- Some browsers block autoplay
- User must interact with page first
- Check browser console for audio errors

## Advanced: Custom Domain

1. After deploying, you'll get a URL
2. In your domain's DNS settings, add a CNAME record pointing to your hosting service
3. Configure custom domain in hosting service settings

## Support

For issues with pygbag, check:
- [pygbag GitHub](https://github.com/pygame-web/pygbag)
- [Pygame Web Documentation](https://pygame-web.github.io/)

