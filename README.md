# Encrypted Dairy with Rich Text & Backup

A secure personal dairy application built with Python,SQLite,and TKinter,designed for privacy-conscious users like journalists,
legal professionals,or anyone who wants to keep thier  notes safe. All dairy entries are encrypted with a password( SHA-256+fernet),
so even if someone copies the database,they cannot read your notes without the correct password.

# Features
- Password-protected login(SHA-256)
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



Run the app:
    python -m diary_app.main

 # Security  Notes

 - Passwords are never stored.
 - It derives a Fernet key from a SHA-256 hash of password + username. That means each user has a different key even if they share the same password.
 - Without the correct password,diary entries cannot be decrypted.
 - keep your password safe-lossing it means permanent data loss.

 
 

  
