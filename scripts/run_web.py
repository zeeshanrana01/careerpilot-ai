"""Launcher script for CareerPilot AI Web Dashboard."""
import sys
from pathlib import Path
import uvicorn

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    print("=" * 70)
    print("  Starting CareerPilot AI Web Dashboard & REST API")
    print("=" * 70)
    print("  * Dashboard UI:  http://localhost:8000")
    print("  * OpenAPI Docs:  http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("careerpilot.api.app:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
