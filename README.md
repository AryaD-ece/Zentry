# Zentry — Two-Layer Secure Vault with Decoy Mode (Python)

Zentry is a lightweight **secure file vault** built in Python. It protects sensitive files using **two-layer authentication (L1 + optional L2)** and a **decoy (fake) vault** for coercion-resistant access.

> **Goal:** If someone forces access, you can reveal the decoy vault while the real vault remains encrypted and protected.

---

## Table of Contents
- [Key Highlights](#key-highlights)
- [How It Works](#how-it-works)
- [Security Model](#security-model)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Example Session](#example-session)
- [Notes (Repo Hygiene)](#notes-repo-hygiene)
- [Author](#author)

---

## Key Highlights
- Two independent vaults: **Real Vault** + **Decoy Vault**
- **Two-layer authentication**: L1 password + optional L2
- Strong encryption: **AES-256 (AES-GCM authenticated encryption)**
- Secure key derivation: **PBKDF2 + random salt**
- Clean **CLI workflow** with file add/list/export
- Decoy mode designed for **coercion defense**

---

## How It Works

Zentry maintains **two separate encrypted vaults**:

### 1) Real Vault (Protected)
Access requires:
- **L1:** primary password
- **L2 (optional):** chosen during setup:
  1. L2 password
  2. **Recovery key (offline)** *(recommended)*
  3. No second factor

If you select Recovery Key:
> **Real vault unlock requires L1 password + recovery key**

---

### 2) Decoy Vault (Coercion Defense)
The decoy vault is protected using a **decoy password**.

If coerced:
- You enter the **decoy password**
- The attacker sees harmless decoy files
- The real vault remains hidden and encrypted

---

## Security Model
Zentry uses:
- **AES-GCM** for confidentiality + integrity (tamper detection)
- Random **salt** and **nonce**
- **PBKDF2** to derive encryption keys securely from passwords

✅ Sensitive files are never stored in plaintext.

---

## Commands

| Command | Description |
|--------|-------------|
| `init` | Initialize real + decoy vault |
| `add <file>` | Add file to real vault |
| `add <file> --decoy` | Add file to decoy vault |
| `list` | List real vault contents |
| `list --decoy` | List decoy vault contents |
| `export <file>` | Decrypt and export file |
| `decoy-init` | Generate fake files inside decoy vault |
| `lock` | Clear in-memory keys (demo utility) |

---

## Project Structure

```txt
Zentry/
├── cli.py                 # CLI entry point
├── crypto.py              # AES-GCM + PBKDF2 utilities
├── vault.py               # vault logic (real + decoy)
├── decoy_gen.py           # decoy content generator
├── hello.txt              # sample file
├── exports/               # decrypted exports (output)
├── storage/               # internal storage/modules
├── zentry_store/          # encrypted vault data
│   ├── real.zvlt
│   ├── decoy.zvlt
│   └── meta.json
└── .venv/                 # virtual environment (ignored in Git)
Installation
Requirements
Python 3.12+

Dependency: cryptography

Setup (Windows / Git Bash)
Create and activate a virtual environment:

bash
Copy code
python -m venv .venv
source .venv/Scripts/activate
Setup (Windows / PowerShell)
powershell
Copy code
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Install dependency
bash
Copy code
pip install cryptography
Quick Start
1) Initialize the vault
bash
Copy code
python cli.py init
You will be prompted for:

L1 password

L2 method (password / recovery key / none)

Recovery key or L2 password

Decoy password

Vault files created:

txt
Copy code
zentry_store/real.zvlt
zentry_store/decoy.zvlt
zentry_store/meta.json
2) Add a file
Add to real vault:

bash
Copy code
python cli.py add hello.txt
Add to decoy vault:

bash
Copy code
python cli.py add hello.txt --decoy
3) List vault contents
Real vault:

bash
Copy code
python cli.py list
Decoy vault:

bash
Copy code
python cli.py list --decoy
4) Export (decrypt) a file
bash
Copy code
python cli.py export hello.txt
Exported output:

txt
Copy code
exports/hello.txt
If authentication fails, Zentry attempts decoy mode automatically.

5) Generate decoy content
bash
Copy code
python cli.py decoy-init
6) Lock (demo utility)
bash
Copy code
python cli.py lock
Example Session
bash
Copy code
python cli.py init
python cli.py add hello.txt
python cli.py list
python cli.py export hello.txt
Notes (Repo Hygiene)
Recommended .gitignore entries:

gitignore
Copy code
# Virtual environments
.venv/

# Python cache
__pycache__/
*.pyc

# Local outputs
exports/
decoy_tmp/
Author
Arya Dinesh
B.Tech ECE — Secure File Storage System Project