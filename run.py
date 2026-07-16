import subprocess
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

def run():
    backend_port = os.getenv("PORT", "8000")
    frontend_port = os.getenv("STREAMLIT_PORT", "8501")
    
    print("=" * 60)
    print("Starting Personalized Networking Assistant...")
    print(f"FastAPI Backend Port: {backend_port}")
    print(f"Streamlit Frontend Port: {frontend_port}")
    print("=" * 60)
    
    # Start Backend
    print("Launching FastAPI Backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", backend_port],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Give backend a moment to bind
    time.sleep(2)
    
    # Start Frontend
    print("Launching Streamlit Frontend...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", frontend_port],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Make sure they are running
    if backend_process.poll() is not None:
        print("Error: Backend failed to start immediately.")
        sys.exit(1)
    if frontend_process.poll() is not None:
        print("Error: Frontend failed to start immediately.")
        backend_process.terminate()
        sys.exit(1)
        
    print("\nApplication is running! Open your browser at:")
    print(f"Streamlit UI: http://localhost:{frontend_port}")
    print(f"FastAPI Docs: http://localhost:{backend_port}/docs\n")
    print("Press Ctrl+C to terminate both servers.")
    
    try:
        # Keep main thread alive and pipe outputs if needed
        while True:
            # Check backend output
            backend_line = backend_process.stdout.readline()
            if backend_line:
                print(f"[Backend] {backend_line.strip()}")
                
            # Check frontend output
            frontend_line = frontend_process.stdout.readline()
            if frontend_line:
                print(f"[Frontend] {frontend_line.strip()}")
                
            # Exit if either process dies
            if backend_process.poll() is not None:
                print("Backend terminated unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("Frontend terminated unexpectedly.")
                break
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping processes...")
    finally:
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Processes stopped. Goodbye!")

if __name__ == "__main__":
    run()
