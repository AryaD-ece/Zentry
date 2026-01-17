# Zentry — Secure Two-Layer File Vault with Decoy Access (Python)

Zentry is a lightweight **encrypted file vault** implemented in Python, designed to securely store sensitive files using a **two-layer authentication model (L1 + optional L2)** and an independent **Decoy Vault** for coercion-resistant scenarios.

The system maintains strict separation between the **Real Vault** (protected) and the **Decoy Vault** (controlled disclosure). Under coercion, the decoy vault can be revealed without exposing real vault content.

---

## Contents

- [Overview](#overview)
- [Key Capabilities](#key-capabilities)
- [System Model](#system-model)
  - [Vault Separation](#vault-separation)
  - [Authentication Model](#authentication-model)
  - [Decoy Access Model](#decoy-access-model)
- [Cryptography and Security Design](#cryptography-and-security-design)
  - [Encryption](#encryption)
  - [Key Derivation](#key-derivation)
  - [Randomness](#randomness)
- [Command Line Interface](#command-line-interface)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Operational Workflow](#operational-workflow)
- [Example Usage](#example-usage)
- [Operational Notes](#operational-notes)
  - [Repository Hygiene / Git Safety](#repository-hygiene--git-safety)
  - [Security Scope Disclaimer](#security-scope-disclaimer)
- [Author](#author)

---

## Overview

Zentry provides encrypted storage for files in two separate compartments:

- **Real Vault**: intended for sensitive assets requiring strong access control  
- **Decoy Vault**: intended for safe disclosure under coercion (contains non-sensitive content only)

This model allows controlled access without compromising the confidentiality of real assets.

---

## Key Capabilities

- **Dual-vault architecture**: independent encrypted stores for Real and Decoy vaults
- **Two-layer authentication**:
  - **L1 password** (mandatory)
  - **L2 factor** (configurable: password / recovery key / disabled)
- **Cryptographic confidentiality and integrity** using **AES-GCM**
- **Password-based key derivation** using **PBKDF2** with per-vault random salt
- **Coercion-aware access model**:
  - Decoy password unlocks the decoy vault only
  - Real vault remains inaccessible without real credentials
- **CLI-driven operation** for deterministic and reproducible workflows

---

## System Model

### Vault Separation

Zentry maintains two vaults with strict separation:

- **Real Vault** (`real.zvlt`)
- **Decoy Vault** (`decoy.zvlt`)

Both vaults are encrypted independently with different derived keys and metadata.

---

### Authentication Model

#### Layer 1 (L1) — Primary Password *(mandatory)*

Used as the primary authentication factor and as input to key derivation.

#### Layer 2 (L2) — Optional Secondary Factor *(configurable during initialization)*

Supported L2 modes:

1. **L2 Password**
2. **Recovery Key (offline secret)** *(recommended for stronger security posture)*
3. **No L2**

If recovery key mode is selected:

> Real Vault unlock requires **L1 password + recovery key**

---

### Decoy Access Model

The Decoy Vault is unlocked using the **Decoy Password**. This provides controlled disclosure without revealing real vault contents.

Operational intent:

- If coerced, provide the **decoy password**
- Attacker gains access only to **decoy content**
- Real vault remains **encrypted and protected**

---

## Cryptography and Security Design

Zentry follows a pragmatic security baseline using widely adopted cryptographic primitives.

### Encryption

- **AES-GCM** (Authenticated Encryption)  
  - Confidentiality: prevents disclosure without correct keys  
  - Integrity/authentication: detects modifications (tampering)

### Key Derivation

- **PBKDF2**  
  - Derives cryptographic keys from passwords  
  - Uses **per-vault random salt**  
  - Mitigates brute-force effectiveness compared to raw password usage

### Randomness

- Random **salt** and **nonce** are generated for cryptographic operations.

✅ Files are never stored in plaintext inside vault containers.

---

## Command Line Interface

| Command | Function |
|--------|----------|
| `init` | Initialize Real and Decoy vaults |
| `add <file>` | Encrypt and add a file to the Real Vault |
| `add <file> --decoy` | Encrypt and add a file to the Decoy Vault |
| `list` | List Real Vault contents |
| `list --decoy` | List Decoy Vault contents |
| `export <file>` | Decrypt and export a file |
| `decoy-init` | Generate and insert synthetic decoy data |
| `lock` | Clear in-memory keys *(utility / demo)* |

---

## Repository Structure

```txt
Zentry/
├── cli.py                 # CLI entry point
├── crypto.py              # Cryptographic utilities (AES-GCM, PBKDF2)
├── vault.py               # Vault management logic (Real + Decoy)
├── decoy_gen.py           # Decoy content generator
├── hello.txt              # Sample file
├── exports/               # Decrypted exports (output)
├── storage/               # Internal support modules
├── zentry_store/          # Vault artifacts (encrypted)
│   ├── real.zvlt
│   ├── decoy.zvlt
│   └── meta.json
└── .venv/                 # Virtual environment (excluded from Git)
```

---

## Installation

### Requirements

- Python **3.12+**
- Dependency: `cryptography`

### Setup (Windows / Git Bash)

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependency:

```bash
pip install cryptography
```

---

## Operational Workflow

### 1) Initialize vaults

```bash
python cli.py init
```

You will be prompted for:

- **L1 password**
- **L2 mode**: password / recovery key / none
- **L2 credential** (if applicable)
- **Decoy password**

Generated vault artifacts:

```txt
zentry_store/real.zvlt
zentry_store/decoy.zvlt
zentry_store/meta.json
```

---

### 2) Add a file

Add to **Real Vault**:

```bash
python cli.py add hello.txt
```

Add to **Decoy Vault**:

```bash
python cli.py add hello.txt --decoy
```

---

### 3) List vault contents

List **Real Vault** contents:

```bash
python cli.py list
```

List **Decoy Vault** contents:

```bash
python cli.py list --decoy
```

---

### 4) Export (decrypt) a file

```bash
python cli.py export hello.txt
```

Decrypted exports are written to:

```txt
exports/hello.txt
```

---

### 5) Generate decoy vault content

```bash
python cli.py decoy-init
```

---

### 6) Lock vault (utility / demo)

```bash
python cli.py lock
```

---

## Example Usage

```bash
python cli.py init
python cli.py add hello.txt
python cli.py list
python cli.py export hello.txt
```

---

## Operational Notes

### Repository Hygiene / Git Safety

Recommended `.gitignore` exclusions:

```gitignore
.venv/
__pycache__/
*.pyc
exports/
zentry_store/
```

> **Important:** Do not commit encrypted vault artifacts (`*.zvlt`) or vault metadata (`meta.json`) to source control.

---

### Security Scope Disclaimer

Zentry is intended for educational and demonstration use in secure storage workflows. It has not been formally security-audited and is not positioned as a certified security product.

---

## Author

**Arya Dinesh**  
B.Tech — Electronics and Communication Engineering (ECE)  
Project: Secure File Storage System (Zentry)
