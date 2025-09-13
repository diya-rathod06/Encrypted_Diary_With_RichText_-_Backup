import shutil
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "secure_diary.db"

def create_encrypted_backup(fernet):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(__file__).parent / f"backup_{now}.db"
    shutil.copy(DB_FILE, backup_path)
    return backup_path
