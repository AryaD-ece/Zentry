# File: decoy_gen.py
"""
decoy_gen.py
Small helper to produce plausible decoy files. Used by instructors/students
to populate the decoy vault with realistic-but-harmless content.
"""
from pathlib import Path

def generate_decoy_files(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    # Simple invoice templates
    for i in range(1,4):
        p = target_dir / f"invoice_{i}.txt"
        p.write_text(f"Invoice #{i}\nCompany: ACME Pvt Ltd\nAmount: INR {1000*i}\nNote: Paid\n")
    # Some safe notes
    (target_dir / "notes.txt").write_text("Grocery list:\n- milk\n- eggs\n- rice\n")
    (target_dir / "welcome.txt").write_text("Welcome! This is a harmless decoy folder.\n")
    print(f"[decoy_gen] Generated files in: {target_dir}")
