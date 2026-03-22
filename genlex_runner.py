import sys
import os
import io

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import the existing runtime
sys.path.append(r'C:\Genlex_Linear')
try:
    from all_engine import GenlexLinearRuntime
except ImportError:
    print("[ ERROR ] Genlex Engine (all_engine.py) not found in C:\Genlex_Linear")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("GENLEX NATIVE RUNNER v1.0")
        print("Usage: genlex_runner.exe <file.all | file.cgl>")
        input("\nPress Enter to exit...")
        sys.exit(1)

    target_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(target_file):
        print(f"[ ERROR ] File not found: {target_file}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"--- NATIVE GENLEX EXECUTION: {os.path.basename(target_file)} ---")
    
    try:
        runtime = GenlexLinearRuntime()
        runtime.run(target_file)
    except Exception as e:
        print(f"[ CRITICAL ERROR ] {e}")
    
    print("\n--- EXECUTION FINISHED ---")
    input("Press Enter to close terminal...")

if __name__ == "__main__":
    main()
