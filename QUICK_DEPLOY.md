# Quick Deployment Guide

## 🚀 Deploy in 3 Steps

### Step 1: Build
```bash
python build_web.py
```

### Step 2: Test Locally (Optional)
```bash
python serve_web.py
```
Visit `http://localhost:8000` to test

### Step 3: Deploy

Choose one of these free options:

#### Option A: Netlify (Easiest)
1. Go to [netlify.com](https://netlify.com) and sign up
2. Drag and drop the `web-build/` folder
3. Done! You get a URL like `yourgame.netlify.app`

#### Option B: GitHub Pages
1. Create a new GitHub repository
2. Copy all files from `web-build/` to the repo
3. Go to Settings → Pages
4. Select main branch and save
5. Your game is at: `yourusername.github.io/repo-name/`

#### Option C: Vercel
1. Install: `npm i -g vercel`
2. `cd web-build`
3. `vercel`
4. Follow prompts

## 📝 Embed in Your Website

Copy this code and update the `src` path:

```html
<iframe 
    src="https://your-game-url.com/index.html" 
    width="480" 
    height="320" 
    frameborder="0"
    allow="autoplay"
    style="border: 2px solid #333; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
</iframe>
```

For responsive (mobile-friendly) embedding, see `embed_example.html`

## ⚠️ Important Notes

- First load may be slow (WebAssembly compilation)
- Audio needs user interaction (click/tap first)
- Works on all modern browsers
- File size: ~5-10MB (compressed)

## 🆘 Troubleshooting

**Build fails?**
- Make sure Python 3.9+ is installed
- Run: `pip install --upgrade pygbag`

**Game doesn't load?**
- Check browser console (F12) for errors
- Make sure all files from `web-build/` are uploaded
- Check file paths (case-sensitive on some servers)

**Need more help?**
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide.

