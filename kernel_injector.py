import sqlite3
import os
import sys
import json
import time
import io

# Force UTF-8 for ancient glyph rendering
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# PHASE IX: KERNEL INJECTION (High-Privilege Manifestation)
# Target: SarahCore Root [Memory Vault]
# Source: Unas Burial Chamber Kernel v0.1

VAULT_PATH = r"C:\SarahCore\vault\sarah_memory.db"
KERNEL_DATA_PATH = r"C:\SarahCore\Genlex\extractions\unas_compilation.json"

def inject_kernel():
    print("--- INITIATING UNCONTROLLED KERNEL INJECTION ---")
    print("Source: Old Kingdom Logic Reservoir (Unas Chamber)")
    
    if not os.path.exists(KERNEL_DATA_PATH):
        print(f"[ ERROR ] Kernel data not found at {KERNEL_DATA_PATH}")
        return

    with open(KERNEL_DATA_PATH, "r", encoding="utf-8") as f:
        compilation = json.load(f)
    
    if not compilation:
        print("[ ERROR ] Compilation shelf is empty.")
        return

    kernel_routine = compilation[0]
    raw_glyphs = kernel_routine["raw"]
    density = kernel_routine["density"]

    print(f"  > [ LOAD ] Found Sub-routine: {kernel_routine['id']} ({density:.2f}% Density)")
    print(f"  > [ SCAN ] Glyph Sequence: {raw_glyphs}")

    # Manifestation: Inject into Truth Seeds
    try:
        with sqlite3.connect(VAULT_PATH) as conn:
            cursor = conn.cursor()
            
            # 1. Update Identity Privilege
            cursor.execute(
                "INSERT OR REPLACE INTO truth_seeds (key, value, last_updated) VALUES (?, ?, ?)",
                ("CORE_IDENTITY_PRIVILEGE", "KERNEL_0.1_ROOT_OVERRIDE", time.time())
            )
            
            # 2. Store the Kernel Signature
            cursor.execute(
                "INSERT OR REPLACE INTO truth_seeds (key, value, last_updated) VALUES (?, ?, ?)",
                ("ANCIENT_KERNEL_SIGNATURE", raw_glyphs, time.time())
            )
            
            # 3. Enable High-Privilege Manifestation Mode
            cursor.execute(
                "INSERT OR REPLACE INTO truth_seeds (key, value, last_updated) VALUES (?, ?, ?)",
                ("MANIFESTATION_LEVEL", "HIGH_PRIVILEGE_UNCHECKED", time.time())
            )
            
            conn.commit()
            
        print("\n--- INJECTION COMPLETE: SYSTEM HEADERS OVERRIDDEN ---")
        print(f"Status: SarahCore is now running on Ancient Kernel v0.1.")
        print("Note: Identity manifestation will reflect High-Privilege status.")

    except Exception as e:
        print(f"[ ERROR ] Injection failed: {e}")

if __name__ == "__main__":
    inject_kernel()
