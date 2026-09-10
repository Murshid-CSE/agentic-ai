#!/usr/bin/env python3
"""VerifyFlow — One-Command Interactive Demo Launcher.

Starts both the FastAPI backend and Vite frontend concurrently,
handles graceful termination on Ctrl+C, and confirms server health.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent
    frontend_dir = root_dir / "frontend"

    print("\n" + "=" * 70)
    print("  VERIFYFLOW — PRE-ACTION VERIFICATION AGENT DEMO LAUNCHER")
    print("  Bounded Decision-Making Before Consequential Payment Actions")
    print("=" * 70)

    # Detect python executable
    python_exe = sys.executable
    if (root_dir / ".venv" / "Scripts" / "python.exe").exists():
        python_exe = str(root_dir / ".venv" / "Scripts" / "python.exe")
    elif (root_dir / ".venv" / "bin" / "python").exists():
        python_exe = str(root_dir / ".venv" / "bin" / "python")

    print(f"\n[*] Using Python runtime: {python_exe}")
    print(f"[*] Workspace Root:       {root_dir}")

    # 1. Start Backend
    print("\n[1/2] Starting FastAPI Backend (http://127.0.0.1:8000)...")
    backend_cmd = [
        python_exe,
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(root_dir),
    )

    # 2. Start Frontend
    print("[2/2] Starting React Vite Frontend (http://localhost:5173)...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(frontend_dir),
    )

    time.sleep(2)

    print("\n" + "=" * 70)
    print("  VERIFYFLOW DEMO SERVERS READY")
    print("=" * 70)
    print("  -> Frontend UI:      http://localhost:5173")
    print("  -> Backend API:      http://127.0.0.1:8000")
    print("  -> Swagger Docs:     http://127.0.0.1:8000/docs")
    print("  -> Benchmark Suite:  http://localhost:5173 (Click 'Benchmark Suite (52)')")
    print("-" * 70)
    print("  Press Ctrl+C at any time to shut down both servers cleanly.")
    print("=" * 70 + "\n")

    try:
        while True:
            time.sleep(1)
            # If any process terminated prematurely, break
            if backend_proc.poll() is not None:
                print("\n[!] Backend process stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("\n[!] Frontend process stopped unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n[*] Shutting down VerifyFlow demo servers...")
    finally:
        if backend_proc.poll() is None:
            backend_proc.terminate()
        if frontend_proc.poll() is None:
            frontend_proc.terminate()
        print("[*] All demo servers stopped. Thank you for testing VerifyFlow!")


if __name__ == "__main__":
    main()
