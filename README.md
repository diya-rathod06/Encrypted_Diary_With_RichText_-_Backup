# Encrypted Dairy with Rich Text & Backup

A secure personal dairy application built with Python,SQLite,and TKinter,designed for privacy-conscious users like journalists,
legal professionals,or anyone who wants to keep thier  notes safe. All dairy entries are encrypted with a password(PBKDF2+salt+Fernet AES),
so even if someone copies the database,they cannot read your notes without the correct password.

# Features
- Password-protected login(PBKDF2 key derivation + salt)
- Rich text editor(supports basic formatting,bold,italic,underline,markdown-like input)
- full-text search
- Encryption with Fernet-entries are unreadable without your password
- Automatic backup of encrypted database file
- Timestamps saved with each entry
- Simple Tkinter GUI
  
# Installation

Clone the repository:

git clone https://github.com/diya-rathod06/Encrypted_Diary_With_RichText_-_Backup.git
cd "C:\Encrypted_Diary_With_RichText_-_Backup"

Install dependencies:

pip install cryptography markdown2 tkinterweb
(tkinter, sqlite3, time, os, shutil are built into Python)

# Usage

1. Run the app:
    python -m diary_app.main
   
2. On first run:
   - Enter a password(this will be a diary password).
   - The app creates the database and salt file.

3. On later runs:
   - Enter the same password to unlock.
   - Wrong password -> access denied.

 # Security  Notes

 - Passwords are never stored.
 - A random salt ensures the same password creates different keys across systems.
 - Without the correct password,diary entries cannot be decrypted.
 - keep your password safe-lossing it means permanent data loss.

 
 

  
