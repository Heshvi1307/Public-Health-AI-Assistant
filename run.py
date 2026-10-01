"""
run.py - Main entry point to launch the Public Health Information Assistant.
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    print("\n" + "=" * 70)
    print("PUBLIC HEALTH INFORMATION ASSISTANT")
    print("AI-assisted health information with deterministic safety controls")
    print(f"Serving live at: http://{host}:{port}")
    print(f"Safety Test Suite: http://{host}:{port}/#tests")
    print("=" * 70 + "\n", flush=True)
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
