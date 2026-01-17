# File: vault.py
"""
vault.py
Vault management for Zentry:
- Creates/reads/writes real.zvlt and decoy.zvlt
- Uses crypto.py for encryption primitives
- Vault body format: JSON list of items (each item is {"name":..., "type":"file"|"note", "data": base64(...)})
- Real vault: CEK encrypts body; CEK is wrapped with L1 (password) and optionally L2 (recovery password)
- Decoy vault: simple password-protected (single-layer) for ease-of-use

This file provides a Vault class with simple methods used by cli.py
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from base64 import urlsafe_b64encode, urlsafe_b64decode

from crypto import (
    create_cek, wrap_cek_with_password, unwrap_cek_with_password,
    create_vault_blob, decrypt_vault_blob, _b64encode, _b64decode
)

# === On-disk filenames ===
META_FILENAME = "meta.json"
REAL_FILENAME = "real.zvlt"
DECOY_FILENAME = "decoy.zvlt"

# === Vault body helpers ===
def _encode_bytes(b: bytes) -> str:
    return urlsafe_b64encode(b).decode('ascii')

def _decode_str(s: str) -> bytes:
    return urlsafe_b64decode(s.encode('ascii'))

# === Vault class ===
class Vault:
    """
    Manage a vault directory containing meta.json, real.zvlt and decoy.zvlt.
    """
    def __init__(self, root: Path):
        self.root = root
        self.meta_path = root / META_FILENAME
        self.real_path = root / REAL_FILENAME
        self.decoy_path = root / DECOY_FILENAME
        # Ensure folder exists
        root.mkdir(parents=True, exist_ok=True)

    # --------------------
    # Initialization flows
    # --------------------
    def init_new(self, l1_password: str, l2_password: Optional[str], decoy_password: str):
        """
        Initialize meta.json and create empty real & decoy vaults.
        real: empty list encrypted with CEK; CEK wrapped with L1 and (if provided) L2
        decoy: small harmless items encrypted with decoy password (single-wrap)
        """
        # Build meta
        meta = {"version":1, "real": {"file": REAL_FILENAME, "two_level": bool(l2_password)}, "decoy": {"file": DECOY_FILENAME}}
        self.meta_path.write_text(json.dumps(meta, indent=2))

        # Real vault: create CEK -> empty list body -> encrypt -> wrap CEK with L1 and L2
        cek = create_cek()
        body = json.dumps([]).encode('utf-8')  # empty list of items
        blob = create_vault_blob(cek, body)  # contains file_ct & file_nonce
        # wrap CEK with L1
        wrapped_l1 = wrap_cek_with_password(cek, l1_password)
        # optionally wrap CEK with L2
        wrapped_l2 = wrap_cek_with_password(cek, l2_password) if l2_password else None

        real_store = {"version":1, "policy": {"requires_l2": bool(l2_password)}, "wrapped_l1": wrapped_l1, "wrapped_l2": wrapped_l2, "blob": blob}
        self.real_path.write_text(json.dumps(real_store, indent=2))

        # Decoy vault: use decoy password to wrap CEK and put a few harmless items
        decoy_cek = create_cek()
        decoy_items = [
            {"name":"decoy_welcome.txt", "type":"file", "data": _encode_bytes(b"Welcome to the decoy vault. Nothing secret here.\n")}
        ]
        decoy_body = json.dumps(decoy_items).encode('utf-8')
        decoy_blob = create_vault_blob(decoy_cek, decoy_body)
        wrapped_decoy = wrap_cek_with_password(decoy_cek, decoy_password)
        decoy_store = {"version":1, "wrapped": wrapped_decoy, "blob": decoy_blob}
        self.decoy_path.write_text(json.dumps(decoy_store, indent=2))

    # --------------------
    # Helpers to read vaults
    # --------------------
    def _read_json(self, path: Path) -> Dict[str, Any]:
        txt = path.read_text()
        return json.loads(txt)

    def unlock_real(self, l1_password: str, l2_password: Optional[str]) -> List[Dict[str,Any]]:
        """
        Attempt to unwrap CEK using l1 (and l2 if required), then decrypt the vault body and return items list.
        Raises ValueError on failure.
        """
        store = self._read_json(self.real_path)
        policy = store.get("policy", {})
        requires_l2 = policy.get("requires_l2", False)

        # Unwrap with L1 first (we expect wrapped_l1 present)
        try:
            cek = unwrap_cek_with_password(store["wrapped_l1"], l1_password)
        except Exception as e:
            # Fail quietly with a generic error
            raise ValueError("unable to unlock vault") from e

        # If L2 required, attempt unwrap with L2 (must match)
        if requires_l2:
            if not l2_password:
                raise ValueError("two-level authentication required")
            try:
                cek2 = unwrap_cek_with_password(store["wrapped_l2"], l2_password)
            except Exception as e:
                raise ValueError("unable to unlock vault") from e
            # Extra check: ensure cek == cek2 (wrapped CEK was same originally)
            if cek != cek2:
                raise ValueError("unable to unlock vault")

        # Decrypt vault blob
        body_bytes = decrypt_vault_blob(cek, store["blob"])
        items = json.loads(body_bytes.decode('utf-8'))
        return items

    def save_real_items(self, l1_password: str, l2_password: Optional[str], items: List[Dict[str,Any]]):
        """
        Persist the items list back to real.zvlt using the wrapped CEK info already stored.
        Steps:
          - read store -> unwrap CEK with L1 (and L2 if required) -> encrypt items -> replace blob -> save
        """
        store = self._read_json(self.real_path)
        policy = store.get("policy", {})
        requires_l2 = policy.get("requires_l2", False)

        # unwrap CEK
        cek = unwrap_cek_with_password(store["wrapped_l1"], l1_password)
        if requires_l2:
            if not l2_password:
                raise ValueError("two-level authentication required")
            cek2 = unwrap_cek_with_password(store["wrapped_l2"], l2_password)
            if cek != cek2:
                raise ValueError("unable to unlock vault")

        # encrypt new body
        body_bytes = json.dumps(items).encode('utf-8')
        blob = create_vault_blob(cek, body_bytes)
        store["blob"] = blob
        self.real_path.write_text(json.dumps(store, indent=2))

    # --------------------
    # Decoy unlock/save (single password)
    # --------------------
    def unlock_decoy(self, decoy_password: str) -> List[Dict[str,Any]]:
        store = self._read_json(self.decoy_path)
        try:
            decoy_cek = unwrap_cek_with_password(store["wrapped"], decoy_password)
        except Exception as e:
            raise ValueError("unable to unlock decoy") from e
        body_bytes = decrypt_vault_blob(decoy_cek, store["blob"])
        items = json.loads(body_bytes.decode('utf-8'))
        return items

    def save_decoy_items(self, decoy_password: str, items: List[Dict[str,Any]]):
        store = self._read_json(self.decoy_path)
        decoy_cek = unwrap_cek_with_password(store["wrapped"], decoy_password)
        body_bytes = json.dumps(items).encode('utf-8')
        blob = create_vault_blob(decoy_cek, body_bytes)
        store["blob"] = blob
        self.decoy_path.write_text(json.dumps(store, indent=2))
