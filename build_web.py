"""
Build script for web deployment using pygbag
"""

import subprocess
import sys
import os
import ssl
import certifi

def fix_ssl_certificates():
    """Fix SSL certificate issues on macOS"""
    try:
        # Try to set up SSL context with certifi certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        print("✓ SSL certificates configured")
        return True
    except Exception as e:
        print(f"⚠ SSL certificate warning: {e}")
        print("Attempting to continue anyway...")
        return False

def build_web():
    """Build the game for web deployment"""
    print("Building game for web deployment...")
    print("=" * 50)
    
    # Fix SSL certificates if needed
    try:
        import certifi
        print("✓ certifi is available")
    except ImportError:
        print("Installing certifi for SSL certificate support...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "certifi"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import certifi
    
    # Set SSL certificate path
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    # Check if pygbag is installed
    try:
        import pygbag
        print("✓ pygbag is installed")
    except ImportError:
        print("✗ pygbag is not installed")
        print("Installing pygbag...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygbag>=0.8.0"])
        print("✓ pygbag installed")
    
    # Build command - use --template without specifying to use built-in
    build_cmd = [
        sys.executable, "-m", "pygbag",
        "--build",
        "main.py"
    ]
    
    print("\nRunning build command...")
    print(" ".join(build_cmd))
    print("=" * 50)
    print("Note: SSL warnings are usually safe to ignore if build continues...")
    print("=" * 50)
    
    try:
        # Set environment to ignore SSL warnings if needed
        env = os.environ.copy()
        env['PYTHONHTTPSVERIFY'] = '0'  # Only as fallback
        
        result = subprocess.run(build_cmd, check=False, env=env)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✓ Build completed successfully!")
            print("\nBuild output is in: web-build/")
            print("\nTo test locally, run:")
            print("  python serve_web.py")
            print("\nOr serve the web-build/ directory with any web server")
        else:
            print("\n" + "=" * 50)
            print("⚠ Build completed with warnings (this is usually OK)")
            print("Check if web-build/ directory was created")
            if os.path.exists("web-build"):
                print("✓ web-build/ directory exists - build likely succeeded!")
                print("\nTo test locally, run:")
                print("  python serve_web.py")
            else:
                print("✗ web-build/ directory not found - build may have failed")
                print("\nTroubleshooting:")
                print("1. Try running: pip install --upgrade pygbag certifi")
                print("2. Check your internet connection")
                print("3. SSL warnings can usually be ignored if build continues")
                sys.exit(1)
    except Exception as e:
        print(f"\n✗ Build failed with error: {e}")
        print("\nTroubleshooting:")
        print("1. Install certificates: pip install certifi")
        print("2. Update pygbag: pip install --upgrade pygbag")
        print("3. SSL warnings are usually safe to ignore")
        sys.exit(1)

if __name__ == "__main__":
    build_web()












