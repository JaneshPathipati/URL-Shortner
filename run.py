#!/usr/bin/env python3
"""
Run script for the SwiftLink URL Shortener Python application
"""

import os
import sys
from app import app, initialize_database

def main():
    """Main function to run the application"""
    print("🚀 Starting SwiftLink URL Shortener (Python Edition)")
    print("📦 Initializing database...")
    
    # Initialize database
    initialize_database()
    
    print("✅ Database initialized successfully")
    print("🌐 Starting Flask server on http://localhost:3000")
    print("📋 Available endpoints:")
    print("   - GET  /              - Frontend interface")
    print("   - POST /api/shorten   - Create short URL")
    print("   - GET  /:shortCode    - Redirect to original URL")
    print("   - GET  /api/stats     - Get statistics")
    print("   - GET  /api/recent    - Get recent URLs")
    print("   - GET  /api/health    - Health check")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=3000)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
