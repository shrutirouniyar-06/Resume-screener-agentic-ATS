import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(override=True, dotenv_path=".env")

from database import init_db
from models.store_sqlite import seed_demo
from routes.roles import roles_bp
from routes.screening import screen_bp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
CORS(app, origins="*")

# Initialize database
init_db()

app.register_blueprint(roles_bp)
app.register_blueprint(screen_bp)

seed_demo()

@app.get("/api/health")
def health():
    return {"status": "ok", "model": os.getenv("HF_MODEL", "not configured")}


if __name__ == "__main__":
    app.run(debug=True, port=5000)