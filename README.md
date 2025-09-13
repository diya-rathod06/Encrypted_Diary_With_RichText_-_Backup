# Encrypted Dairy with Rich Text & Backup

A secure personal dairy application built with Python,SQLite,and TKinter,designed for privacy-conscious users like journalists,legal professionals,or anyone who wants to keep thier notes safe.
All dairy entries are encrypted with a password(PBKDF2+salt+Fernet AES),so even if someone copies the database,they cannot read your notes without the correct password.

# Features
- Password-protected login(PBKDF2 key derivation + salt)
  
