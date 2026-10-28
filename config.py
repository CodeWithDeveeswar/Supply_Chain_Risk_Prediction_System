id="config_file"
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- BASIC CONFIG ----------------
# Read from .env locally, or from the environment on Render.
SECRET_KEY = os.getenv("SECRET_KEY")

# ---------------- DATABASE ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DB_FOLDER = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_FOLDER, "database.db")

# ---------------- FILE UPLOAD ----------------
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"csv", "xlsx"}

MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB


# ---------------- HELPER FUNCTION ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
