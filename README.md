# Zentry — A Simple Two–Layer Secure Vault (Python Project)

Zentry is a lightweight, Python-based secure vault system designed to store sensitive files with **two-layer protection** and a **decoy (fake) vault**.  
It is built for beginners and works entirely through simple command-line instructions.

This project does *not* use advanced Python or AI libraries — only the `cryptography` package for AES encryption.

---

## 🚀 Features

### 🔐 1. Two-Layer Security (L1 + L2)
Zentry uses two layers of authentication for the real vault:

- **L1:** Main password  
- **L2:** Secondary unlock method (choose one):
  1. Another password  
  2. **Offline recovery key** *(recommended)*  
  3. No second factor

You chose **Option 2 → Recovery Key**.  
This means L1 + recovery key are required to open the real vault.

---

### 🎭 2. Decoy / Fake Vault (Lies to attackers)
Zentry includes a fully separate encrypted **decoy vault**, protected by a **decoy password**.

If someone forces you to open the vault:
- You enter the *decoy password*  
- They see **fake harmless files**, not your real secrets

---

### 📦 3. Encrypted Vault Storage (AES-GCM)
Both real and decoy vaults are encrypted using:
- AES-256
- Random salt + nonce  
- Integrity-checked ciphertext

Files are never stored in plain text.

Your vault files live in:

zentry_store/
real.zvlt
decoy.zvlt
meta.json

yaml
Copy code

---

### 📁 4. File Operations
Zentry supports:

| Command | Description |
|--------|-------------|
| `add <filename>` | Add a file to real/decoy vault |
| `list` | List files in the real vault |
| `list --decoy` | List decoy vault files |
| `export <filename>` | Export + decrypt a file |
| `decoy-init` | Generate fake files for the decoy vault |
| `lock` | Clear in-memory keys (demo only) |

---

## 🛠️ Installation

### 1. Make sure Python is installed  
Your project uses **Python 3.12.x**.

### 2. Install the dependencies (inside venv)

pip install cryptography

yaml
Copy code

---

## 📂 Folder Structure

Zentry/
│── cli.py
│── crypto.py
│── vault.py
│── decoy_gen.py
│── cli_demo.py (demo - optional)
│── test_run.py
│── hello.txt (sample file)
│── exports/ (exported decrypted files)
│── storage/ (temporary working folders)
│── zentry_store/ (main encrypted vault files)
└── .venv/ (virtual environment)

yaml
Copy code

---

## ▶️ Usage (Commands)

### **1. Initialize the vault**
python cli.py init

diff
Copy code

You will be prompted for:
- L1 password  
- L2 method  
- L2 password OR recovery key  
- Decoy password  

This creates:

zentry_store/real.zvlt
zentry_store/decoy.zvlt
zentry_store/meta.json

yaml
Copy code

---

### **2. Add a file**
python cli.py add hello.txt

css
Copy code

Add to decoy vault:
python cli.py add hello.txt --decoy

yaml
Copy code

---

### **3. List files**
Real vault:
python cli.py list

yaml
Copy code

Decoy vault:
python cli.py list --decoy

yaml
Copy code

---

### **4. Export (decrypt) a file**
python cli.py export hello.txt

diff
Copy code

It will ask for:
- L1
- L2
If wrong → it tries decoy vault instead.

Exported file goes to:

exports/hello.txt

yaml
Copy code

---

### **5. Generate fake decoy files**
python cli.py decoy-init

yaml
Copy code

---

### **6. Lock vault (demo only)**
python cli.py lock

yaml
Copy code

---

## 🔍 Example Session

python cli.py init
python cli.py add hello.txt
python cli.py list
python cli.py export hello.txt

yaml
Copy code

Everything worked successfully in your setup.

---

## 🧪 Unit Tests
python -m unittest discover tests

yaml
Copy code

---

## 🎓 Why This Project Is Valuable
- Implements real encryption (AES-256 AES-GCM)
- Shows knowledge of:
  - Password hashing  
  - Key derivation with PBKDF2  
  - Secure file handling  
  - CLI application design  
  - Decoy security concepts  

Perfect for university grading.

---

## 👤 Author
Arya Dinesh  
B.Tech ECE — Secure File Storage System Project