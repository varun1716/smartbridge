import subprocess
import sys
import time
import os
import threading
from dotenv import load_dotenv

load_dotenv()

def stream_output(process, prefix):
    """Stream output from a subprocess in a thread."""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{prefix}] {line.strip()}", flush=True)
    except Exception:
        pass

def run():
    backend_port = os.getenv("PORT", "8000")
    frontend_port = os.getenv("STREAMLIT_PORT", "8501")

    print("=" * 60)
    print("Starting Personalized Networking Assistant...")
    print(f"FastAPI Backend  -> http://localhost:{backend_port}")
    print(f"Streamlit UI     -> http://localhost:{frontend_port}")
    print("=" * 60)

    # Start Backend (combine stdout + stderr)
    print("\nLaunching FastAPI Backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", backend_port, "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Stream backend output in a background thread
    backend_thread = threading.Thread(
        target=stream_output, args=(backend_process, "Backend"), daemon=True
    )
    backend_thread.start()

    # Give backend 3 seconds to start
    time.sleep(3)

    if backend_process.poll() is not None:
        print("ERROR: Backend failed to start. Check output above.")
        sys.exit(1)

    # Start Frontend (combine stdout + stderr)
    print("Launching Streamlit Frontend...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
         "--server.port", frontend_port,
         "--server.headless", "true",
         "--browser.gatherUsageStats", "false"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Stream frontend output in a background thread
    frontend_thread = threading.Thread(
        target=stream_output, args=(frontend_process, "Frontend"), daemon=True
    )
    frontend_thread.start()

    # Give Streamlit 4 seconds to start
    time.sleep(4)

    if frontend_process.poll() is not None:
        print("ERROR: Streamlit frontend failed to start. Check output above.")
        backend_process.terminate()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Application is running!")
    print(f"  Streamlit UI  -> http://localhost:{frontend_port}")
    print(f"  FastAPI Docs  -> http://localhost:{backend_port}/docs")
    print("=" * 60)
    print("Press Ctrl+C to stop both servers.\n")

    try:
        while True:
            # Check if either process died
            if backend_process.poll() is not None:
                print("\nERROR: Backend stopped unexpectedly!")
                break
            if frontend_process.poll() is not None:
                print("\nERROR: Frontend stopped unexpectedly!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        backend_process.terminate()
        frontend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except Exception:
            pass
        print("All servers stopped. Goodbye!")

if __name__ == "__main__":
    run()
