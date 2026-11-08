import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# tests must never overwrite the live app's saved conversations
os.environ["UD_SESSION_STORE"] = os.path.join(tempfile.gettempdir(), "udyam_test_sessions.json")
os.environ["UD_NO_DOTENV"] = "1"          # never read the real .env: tests must not call the live model
os.environ.pop("OPENROUTER_API_KEY", None)
os.environ["UD_TURN_LOG"] = os.path.join(tempfile.gettempdir(), "udyam_test_turns.jsonl")
