"""
Check web build and diagnose display issues
"""

import os
from pathlib import Path

def check_build():
    """Check if web build exists and diagnose issues"""
    build_dir = Path("build/web")
    
    if not build_dir.exists():
        print("❌ Build directory not found!")
        print("Run: .venv/bin/python build_web.py")
        return False
    
    print("✓ Build directory exists")
    
    # Check for required files
    required_files = ["index.html", "cursor-test.apk"]
    missing = []
    for file in required_files:
        if not (build_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✓ All required files present")
    
    # Check index.html for screen size
    index_path = build_dir / "index.html"
    with open(index_path, 'r') as f:
        content = f.read()
        if 'ux(.100)' in content:
            print("⚠ Warning: HTML template uses 10% viewport sizing")
            print("  This might cause display issues")
            print("  Try opening game.html instead of index.html")
    
    print("\n" + "=" * 50)
    print("Build check complete!")
    print("\nTo test:")
    print("  1. .venv/bin/python serve_web.py")
    print("  2. Open http://localhost:8000/game.html")
    print("     (or http://localhost:8000/index.html)")
    print("\nIf screen doesn't show:")
    print("  - Check browser console (F12) for errors")
    print("  - Wait for 'Ready to start!' message")
    print("  - Click/tap the page to enable interaction")
    print("  - See TROUBLESHOOTING.md for more help")
    
    return True

if __name__ == "__main__":
    check_build()

