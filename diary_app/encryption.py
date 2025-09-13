from cryptography.fernet import Fernet
import base64
from hashlib import sha256

VERIFIERS = {}

def fernet_from_password(password, username):
    key = sha256((password + username).encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key)
    return Fernet(key_b64)

def encrypt_text(fernet, text):
    return fernet.encrypt(text.encode())

def decrypt_text(fernet, data):
    if isinstance(data, bytes):
        return fernet.decrypt(data).decode()
    return fernet.decrypt(data.encode()).decode()

def check_password_for_user(username, fernet):
    # Simple in-memory check
    if username not in VERIFIERS:
        return True
    try:
        fernet.decrypt(VERIFIERS[username])
        return True
    except:
        return False

def ensure_verifier(username, fernet):
    if username not in VERIFIERS:
        VERIFIERS[username] = fernet.encrypt(b"verifier")
