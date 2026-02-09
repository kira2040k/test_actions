# vulnerable_app.py
from flask import Flask, request, render_template_string, session
import sqlite3
import os

app = Flask(__name__)

# =========================
# 🔥 Hardcoded secrets sadsd
# =========================
app.secret_key = "super-secret-dev-key-12345"
DB_PASSWORD = "rootpassword"
API_KEY = "sk_live_ABC123SUPERSECRET"
ADMIN_PASSWORD = "admin123"

DATABASE = "users.db"


# =========================
# Setup database
# =========================
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()


init_db()


# =========================
# Home
# =========================
@app.route("/")
def home():
    return """
    <h2>Vulnerable Flask App</h2>
    <ul>
        <li>/login?username=&password= (SQLi)</li>
        <li>/search?q= (SSTI)</li>
        <li>/file?name= (LFI)</li>
        <li>/debug (shows secrets)</li>
    </ul>
    """


# =========================
# ❌ SQL Injection vulnerable
# =========================
@app.route("/login")
def login():
    username = request.args.get("username", "")
    password = request.args.get("password", "")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # 🔥 VULNERABLE QUERY
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = c.execute(query).fetchone()

    if result:
        session["user"] = username
        return "Logged in!"
    else:
        return "Invalid credentials"


# =========================
# ❌ SSTI vulnerabled
# =========================
@app.route("/search")
def search():
    q = request.args.get("q", "")

    # 🔥 Directly rendering user input
    template = f"""
    <h3>Search Results</h3>
    You searched for: {q}
    """

    return render_template_string(template)


# =========================
# ❌ Local File Inclusion (LFI)
# =========================
@app.route("/file")
def read_file():
    name = request.args.get("name", "")

    try:
        with open(name, "r") as f:
            return f.read()
    except:
        return "File not foun2d"


# =========================
# ❌ Leaks secrets
# =========================
@app.route("/debug")
def debug():
    return {
        "secret_key": app.secret_key,
        "db_password": DB_PASSWORD,
        "api_key": API_KEY,
        "admin_password": ADMIN_PASSWORD,
        "cwd_files": os.listdir(".")
    }


# =========================
# Run (debug enabled intentionally)
# =========================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
