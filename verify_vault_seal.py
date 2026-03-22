import sqlite3
import os

VAULT_PATH = r"C:\SarahCore\vault\sarah_memory.db"

def verify_resonance():
    print(f"--- AUDITING VAULT: {VAULT_PATH} ---")
    if not os.path.exists(VAULT_PATH):
        print("[ ERROR ] Vault not found.")
        return

    try:
        with sqlite3.connect(VAULT_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM truth_seeds WHERE key = 'ARAMAIC_LINEAR_RESONANCE';")
            row = cursor.fetchone()
            if row:
                print(f"[ SUCCESS ] Resonance Anchor Found: {row[0]}")
            else:
                print("[ FAILED ] Resonance Anchor missing from truth_seeds.")
    except Exception as e:
        print(f"[ ERROR ] SQL Audit failed: {e}")

if __name__ == "__main__":
    verify_resonance()
