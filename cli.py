# File: cli.py
"""
zentry CLI - user interface for Zentry project.
Commands:
  - init          : initialize vault (real + decoy)
  - add           : add file to real or decoy vault
  - list          : list files in a chosen vault
  - export        : export file from vault to filesystem
  - lock          : lock (clears keys in-memory, demo behavior)
  - decoy-init    : regenerate decoy items using decoy_gen
Usage examples:
  python cli.py init
  python cli.py add tests/sample_secret.txt --real
  python cli.py list --real
  python cli.py export sample_secret.txt --out exported/
"""
import argparse
import getpass
import json
import shutil
from pathlib import Path

from vault import Vault
from decoy_gen import generate_decoy_files

# Project root where vault files live
ROOT = Path(__file__).resolve().parent
ZENTRY_STORE = ROOT / "zentry_store"   # folder to contain meta.json, real.zvlt, decoy.zvlt
vault = Vault(ZENTRY_STORE)

# -------------------------
# CLI command implementations
# -------------------------
def cmd_init(args):
    """
    Initialize the vault with passwords.
    Prompts for L1 (main password), optional L2 (secondary) and decoy password.
    """
    print("Zentry initialization — choose strong passwords.")
    l1 = getpass.getpass("Enter main password (L1): ")
    l1_confirm = getpass.getpass("Confirm main password: ")
    if l1 != l1_confirm:
        print("Passwords did not match. Aborting.")
        return
    # Choose L2 option
    print("Set up second factor (L2). Choose one:")
    print("  1) Use another password (typed now)")
    print("  2) Use a recovery key (string) that you will save offline")
    print("  3) No second factor (not recommended for sensitive items)")
    choice = input("Choose 1/2/3 [default 2]: ").strip() or "2"
    l2 = None
    if choice == "1":
        l2 = getpass.getpass("Enter L2 password: ")
        l2_confirm = getpass.getpass("Confirm L2 password: ")
        if l2 != l2_confirm:
            print("L2 mismatch. Aborting.")
            return
    elif choice == "2":
        # auto-generate recovery key and show it once
        import os, base64
        key = base64.urlsafe_b64encode(os.urandom(24)).decode('ascii')
        print("Recovery key (save this somewhere safe):")
        print(key)
        l2 = key
    else:
        l2 = None

    decoy = getpass.getpass("Enter decoy password (for fake vault): ")
    decoy_confirm = getpass.getpass("Confirm decoy password: ")
    if decoy != decoy_confirm:
        print("Decoy password mismatch. Aborting.")
        return

    vault.init_new(l1, l2, decoy)
    print("Zentry initialized. Vault files created in:", str(ZENTRY_STORE))

def cmd_add(args):
    """
    Add a file to real or decoy vault.
    For real vault, require unlocking with L1 and possibly L2.
    """
    src = Path(args.source)
    if not src.exists():
        print("Source file not found:", src)
        return

    if args.decoy:
        # Unlock decoy only
        decoy_pw = getpass.getpass("Enter decoy password: ")
        try:
            items = vault.unlock_decoy(decoy_pw)
        except Exception:
            print("Unable to unlock decoy. Aborting.")
            return
        # read file bytes and append
        data = src.read_bytes()
        items.append({"name": src.name, "type":"file", "data": __import__("base64").urlsafe_b64encode(data).decode('ascii')})
        vault.save_decoy_items(decoy_pw, items)
        print(f"Added '{src.name}' to decoy vault.")
        return

    # Real vault path
    l1 = getpass.getpass("Enter main password (L1): ")
    # We don't ask L2 here yet; unlock_real will fail if required
    l2 = None
    try:
        items = vault.unlock_real(l1, l2)
    except Exception:
        # If unlocking failed, maybe vault requires L2 -> ask for it and retry
        l2_try = getpass.getpass("Enter L2 (secondary) or press Enter to cancel: ")
        if not l2_try:
            print("Unable to unlock real vault.")
            return
        try:
            items = vault.unlock_real(l1, l2_try)
            l2 = l2_try
        except Exception:
            print("Unable to unlock real vault. Aborting.")
            return

    # read file and append
    data = src.read_bytes()
    items.append({"name": src.name, "type":"file", "data": __import__("base64").urlsafe_b64encode(data).decode('ascii')})
    vault.save_real_items(l1, l2, items)
    print(f"Added '{src.name}' to real vault.")

def cmd_list(args):
    """
    List files in real or decoy vault. Prompts for required passwords.
    """
    if args.decoy:
        decoy_pw = getpass.getpass("Enter decoy password: ")
        try:
            items = vault.unlock_decoy(decoy_pw)
        except Exception:
            print("Unable to unlock decoy.")
            return
        print("Files in decoy vault:")
        for it in items:
            print(" -", it.get("name"))
        return

    l1 = getpass.getpass("Enter main password (L1): ")
    l2 = None
    try:
        items = vault.unlock_real(l1, l2)
    except Exception:
        l2_try = getpass.getpass("Enter L2 (secondary) or press Enter to cancel: ")
        if not l2_try:
            print("Unable to unlock real vault.")
            return
        try:
            items = vault.unlock_real(l1, l2_try)
        except Exception:
            print("Unable to unlock real vault.")
            return
    print("Files in real vault:")
    for it in items:
        print(" -", it.get("name"))

def cmd_export(args):
    """
    Export a filename from either vault to disk (default: exported/ folder).
    """
    fname = args.filename
    outdir = Path(args.out or "exports")
    outdir.mkdir(parents=True, exist_ok=True)

    # Try real first
    l1 = getpass.getpass("Enter main password (L1) to try real (or press Enter to skip): ")
    if l1:
        l2 = None
        try:
            items = vault.unlock_real(l1, l2)
        except Exception:
            l2_try = getpass.getpass("Enter L2 (secondary) or press Enter to skip: ")
            if l2_try:
                try:
                    items = vault.unlock_real(l1, l2_try)
                except Exception:
                    items = None
            else:
                items = None
        if items is not None:
            # search
            for it in items:
                if it.get("name") == fname:
                    data = __import__("base64").urlsafe_b64decode(it["data"].encode('ascii'))
                    (outdir / fname).write_bytes(data)
                    print(f"Exported '{fname}' -> {outdir / fname}")
                    return
    # Try decoy
    decoy_pw = getpass.getpass("Enter decoy password to try decoy (or press Enter to skip): ")
    if decoy_pw:
        try:
            items = vault.unlock_decoy(decoy_pw)
            for it in items:
                if it.get("name") == fname:
                    data = __import__("base64").urlsafe_b64decode(it["data"].encode('ascii'))
                    (outdir / fname).write_bytes(data)
                    print(f"Exported '{fname}' -> {outdir / fname}")
                    return
        except Exception:
            pass

    print("File not found or unable to decrypt.")

def cmd_lock(args):
    # Real project: wipe keys from memory. Here: print only.
    print("Vault locked. (In the real implementation keys would be cleared from memory.)")

def cmd_decoy_init(args):
    """
    Generate decoy files, then insert them into decoy vault (prompt for decoy password).
    """
    tmp = Path("decoy_tmp")
    generate_decoy_files(tmp)
    decoy_pw = getpass.getpass("Enter decoy password to save decoy content: ")
    # build items
    items = []
    for p in tmp.iterdir():
        if p.is_file():
            items.append({"name": p.name, "type": "file", "data": __import__("base64").urlsafe_b64encode(p.read_bytes()).decode('ascii')})
    vault.save_decoy_items(decoy_pw, items)
    # cleanup
    for p in tmp.iterdir():
        p.unlink()
    tmp.rmdir()
    print("Decoy vault populated.")

# -------------------------
# CLI wiring
# -------------------------
def build_parser():
    p = argparse.ArgumentParser(description="Zentry CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub_init = sub.add_parser("init")
    sub_init.set_defaults(func=cmd_init)

    sub_add = sub.add_parser("add")
    sub_add.add_argument("source", help="Path to file to add")
    sub_add.add_argument("--decoy", action="store_true", help="Add to decoy vault")
    sub_add.set_defaults(func=cmd_add)

    sub_list = sub.add_parser("list")
    sub_list.add_argument("--decoy", action="store_true", help="List decoy vault")
    sub_list.set_defaults(func=cmd_list)

    sub_export = sub.add_parser("export")
    sub_export.add_argument("filename", help="Name of file in vault")
    sub_export.add_argument("--out", default="exports", help="Output folder")
    sub_export.set_defaults(func=cmd_export)

    sub_lock = sub.add_parser("lock")
    sub_lock.set_defaults(func=cmd_lock)

    sub_di = sub.add_parser("decoy-init")
    sub_di.set_defaults(func=cmd_decoy_init)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
