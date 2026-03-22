import sqlite3
import os

VAULT_PATH = r"C:\SarahCore\vault\sarah_memory.db"

def audit_truth_seeds():
    print(f"--- FULL TRUTH SEED AUDIT: {VAULT_PATH} ---")
    if not os.path.exists(VAULT_PATH):
        print("[ ERROR ] Vault not found.")
        return

    try:
        with sqlite3.connect(VAULT_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM truth_seeds;")
            rows = cursor.fetchall()
            if rows:
                for key, value in rows:
                    status = "[ ACTIVE ]" if key != "MANIFESTATION_LEVEL" else "[ ELEVATED ]"
                    print(f"  > {status} {key}: {value}")
            else:
                print("[ EMPTY ] No truth seeds found.")
    except Exception as e:
        print(f"[ ERROR ] SQL Audit failed: {e}")

if __name__ == "__main__":
    audit_truth_seeds()
