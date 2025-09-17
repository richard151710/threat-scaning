import os
import subprocess
from pathlib import Path
from flask import Flask, request, abort, jsonify

app = Flask(__name__)

# Load secret from environment — never set it in code.
API_KEY = os.getenv("MY_APP_API_KEY")
if not API_KEY:
    # In production, fail fast so ops knows to set the secret properly
    raise RuntimeError("Missing required environment variable MY_APP_API_KEY")

SAFE_FILES_DIR = Path("/app/safe_files").resolve()  # directory you control
SAFE_FILES_DIR.mkdir(parents=True, exist_ok=True)

def is_safe_filename(filename: str) -> bool:
    # Basic allow-list: allow alphanumeric, hyphen, underscore, dot
    # and disallow path separators
    if "/" in filename or "\\" in filename:
        return False
    # Reject special names like ".."
    if filename in ("", ".", ".."):
        return False
    # Keep it simple; adjust pattern to your needs
    import re
    return re.match(r"^[A-Za-z0-9._-]+$", filename) is not None

@app.route("/ping")
def ping():
    # Validate IP (simple check) — prefer not to shell out for ping.
    ip = request.args.get("ip", "").strip()
    if ip == "":
        return jsonify({"error": "missing ip parameter"}), 400

    # Very simple pattern match for IPv4 / hostname. Use a robust validator in prod.
    import re
    if not re.match(r"^[A-Za-z0-9.\-]+$", ip):
        return jsonify({"error": "invalid ip/host"}), 400

    # Prefer using a library or socket to check reachability. Example: use subprocess safely.
    # Use list args to avoid shell interpolation and set a timeout
    try:
        completed = subprocess.run(["ping", "-c", "1", ip],
                                   capture_output=True,
                                   text=True,
                                   timeout=5,
                                   check=False)  # don't raise on non-zero exit; handle it
    except Exception:
        return jsonify({"error": "failed to run ping"}), 500

    return jsonify({
        "returncode": completed.returncode,
        "stdout": completed.stdout[:2000],  # limit size
        "stderr": completed.stderr[:1000],
    })

@app.route("/readfile")
def readfile():
    filename = request.args.get("file", "
