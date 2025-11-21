"""
Serve the web build locally for testing
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8000
BUILD_DIR = "build/web"  # pygbag creates build/web directory

def serve_web():
    """Serve the web build directory"""
    build_path = Path(BUILD_DIR)
    
    # Also check for web-build as fallback
    if not build_path.exists():
        fallback_path = Path("web-build")
        if fallback_path.exists():
            build_path = fallback_path
        else:
            print(f"Error: {BUILD_DIR} directory not found!")
            print("Please run build_web.py first to build the game.")
            return
    
    os.chdir(build_path)
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Server started at {url}")
        print(f"Serving from: {build_path.absolute()}")
        print("\nPress Ctrl+C to stop the server")
        
        # Try to open browser
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    serve_web()












