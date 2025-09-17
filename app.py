import os
import subprocess
import flask
from flask import request

app = flask.Flask(__name__)


# ❌ Hardcoded secret (CodeQL should flag this)
API_KEY = "12345-SECRET-KEY"

# ❌ Exposed secret in environment variable
os.environ["SECURE_KEY"] = "super-secret-key"  # This should be flagged by CodeQL

@app.route("/ping")
def ping():
    # ❌ Command Injection vulnerability
    ip = request.args.get("ip", "127.0.0.1")
    return subprocess.getoutput(f"ping -c 1 {ip}")

@app.route("/readfile")
def readfile():
    # ❌ Path Traversal vulnerability
    filename = request.args.get("file", "test.txt")
    with open(filename, "r") as f:
        return f.read()

@app.route("/exec")
def exec_code():
    # ❌ Dangerous us
