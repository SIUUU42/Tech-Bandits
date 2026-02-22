"""
Helper script to start both the Flask API server and Streamlit app.

Usage:
    python run_all.py
    
This will start:
1. Flask API server on http://127.0.0.1:5000
2. Streamlit app on http://localhost:8501
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_servers():
    """Start Flask API and Streamlit app in parallel."""
    
    print("🚀 Starting Flight Disruption Recovery Assistant...")
    print("=" * 60)
    
    # Get the current directory
    project_dir = Path(__file__).parent
    
    # Process list
    processes = []
    
    try:
        # Start Flask API server
        print("🔧 Starting Flask API server...")
        flask_process = subprocess.Popen(
            [sys.executable, str(project_dir / "api_server.py")],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(("Flask API", flask_process))
        print(f"   ✅ Flask API started (PID: {flask_process.pid})")
        
        # Give Flask time to start
        time.sleep(2)
        
        # Start Streamlit app
        print("📱 Starting Streamlit app...")
        streamlit_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(project_dir / "app.py")],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(("Streamlit", streamlit_process))
        print(f"   ✅ Streamlit app started (PID: {streamlit_process.pid})")
        
        print("=" * 60)
        print("🌐 Ready! Open your browser:")
        print("   - Main app: http://localhost:8501")
        print("   - Disruption News: http://localhost:8501/News")
        print("   - API health: http://127.0.0.1:5000/api/health")
        print("=" * 60)
        print("\nPress Ctrl+C to stop all services...")
        
        # Keep processes running
        while True:
            for name, proc in processes:
                if proc.poll() is not None:  # Process exited
                    print(f"\n❌ {name} process exited with code {proc.returncode}")
                    raise KeyboardInterrupt
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"   ✅ {name} stopped")
            except:
                proc.kill()
                print(f"   ⚠️  {name} force killed")
        print("Done!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        for _, proc in processes:
            try:
                proc.kill()
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    run_servers()
