🔐 Zentry — Two-Layer Secure Vault with Decoy Access (Python)

Zentry is a lightweight, security-first encrypted file vault written in Python. It provides two-layer authentication (L1 + optional L2) and a built-in decoy vault to support coercion-resistant access.

Core idea: If someone forces you to unlock the vault, you can reveal the Decoy Vault — while the Real Vault remains encrypted, hidden, and protected.

✨ Features

✅ Two vaults: Real Vault + Decoy Vault

✅ Two-layer authentication:

L1 password (mandatory)

L2 factor (optional): Password / Recovery Key / None

✅ Strong encryption: AES-256 via AES-GCM (authenticated encryption)

✅ Secure key derivation: PBKDF2 + random salt

✅ Tamper detection (via AES-GCM integrity guarantees)

✅ Simple, predictable CLI:

init, add, list, export, decoy-init

✅ Designed for coercion defense using decoy access mode

📌 Table of Contents

Overview

Vault Model

Security Architecture

CLI Commands

Project Structure

Installation

Quick Start

Example Workflow

Repo Hygiene Notes

Author

🧠 Overview

Zentry maintains two separate encrypted vaults:

Real Vault → contains sensitive/private data (high security)

Decoy Vault → contains safe, harmless files (coercion mode)

This model enables you to provide access under pressure without compromising real data.

🏦 Vault Model
1) Real Vault (Protected Vault)

Unlock requires:

L1: Primary password (mandatory)

L2 (optional; chosen during setup):

L2 password

Recovery key (offline) (recommended)

No second factor

If the recovery key method is chosen:

Real Vault unlock requires L1 password + Recovery Key

2) Decoy Vault (Coercion-Resistant Mode)

The Decoy Vault is encrypted separately and is unlocked using a Decoy Password.

If coerced:

You provide the Decoy Password

Attacker sees only decoy contents

Real Vault remains encrypted and inaccessible

🛡 Security Architecture

Zentry uses modern cryptographic primitives:

AES-GCM for encryption + integrity (tamper detection)

Random salt and nonce

PBKDF2 for password-based key derivation

✅ Sensitive content is never stored in plaintext.

🧾 CLI Commands
Command	Description
init	Initialize Real + Decoy vaults
add <file>	Encrypt + add file into Real Vault
add <file> --decoy	Encrypt + add file into Decoy Vault
list	List Real Vault contents
list --decoy	List Decoy Vault contents
export <file>	Decrypt + export a file from the vault
decoy-init	Generate fake files inside Decoy Vault
lock	Clear in-memory keys (demo utility)
🗂 Project Structure
Zentry/
├── cli.py                 # CLI entry point
├── crypto.py              # AES-GCM + PBKDF2 utilities
├── vault.py               # Vault logic (real + decoy)
├── decoy_gen.py           # Decoy content generator
├── hello.txt              # Sample file
├── exports/               # Decrypted exports (output)
├── storage/               # Internal modules/storage utilities
├── zentry_store/          # Encrypted vault data
│   ├── real.zvlt
│   ├── decoy.zvlt
│   └── meta.json
└── .venv/                 # Virtual environment (ignored by Git)

⚙ Installation
Requirements

Python 3.12+

Dependency: cryptography

Setup (Windows / Git Bash)

Create and activate a virtual environment:

python -m venv .venv
source .venv/Scripts/activate


Install dependencies:

pip install cryptography

🚀 Quick Start
1) Initialize vault
python cli.py init


You will be prompted for:

L1 password

L2 method (password / recovery key / none)

Recovery key or L2 password

Decoy password

Vault artifacts created:

zentry_store/real.zvlt
zentry_store/decoy.zvlt
zentry_store/meta.json

2) Add a file

Add to Real Vault:

python cli.py add hello.txt


Add to Decoy Vault:

python cli.py add hello.txt --decoy

3) List vault contents

Real Vault:

python cli.py list


Decoy Vault:

python cli.py list --decoy

4) Export (decrypt) a file
python cli.py export hello.txt


Decrypted exports are written to:

exports/hello.txt

5) Generate decoy vault content
python cli.py decoy-init

6) Lock vault (demo utility)
python cli.py lock

✅ Example Workflow
python cli.py init
python cli.py add hello.txt
python cli.py list
python cli.py export hello.txt

🧼 Repo Hygiene Notes

Recommended .gitignore entries:

.venv/

exports/

zentry_store/

__pycache__/

Do not commit vault files (*.zvlt, meta.json) to GitHub.

👤 Author

Arya Dinesh
B.Tech ECE — Secure File Storage System Project
