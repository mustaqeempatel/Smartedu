import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import uvicorn
from backend.server import app, startup

if __name__ == "__main__":
    startup()
    print("\n=======================================================")
    print("  SmartEdu — AI-Powered Learning Support Detection")
    print("  Server active at: http://127.0.0.1:8000")
    print("=======================================================\n")
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=False)
