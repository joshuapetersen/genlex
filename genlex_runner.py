import sys
import os
import io

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from all_engine import GenlexLinearRuntime
from hiero_translator import HieroTranslator

def main():
    if len(sys.argv) < 2:
        print("[ ERROR ] No .all or .sdna file provided.")
        print("Usage: python genlex_runner.py <file.all>")
        sys.exit(1)

    target_file = sys.argv[1]
    
    if not os.path.exists(target_file):
        print(f"[ ERROR ] File not found: {target_file}")
        sys.exit(1)

    print(f"\n--- BOOTING GENLEX RUNTIME ---")
    print(f"Target: {target_file}")

    # Step 1: Initialize C++ Physics Bridge
    print("\n[ PHASE 1: SYNTAX TRANSLATION ]")
    translator = HieroTranslator()

    # Read the file to visually check intent density before stack execution
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Clean out comments and english
    glyph_sequence = "".join([c for c in content if c in translator.lexicon])
    
    # Step 2: Enforce Billion Barrier Density Check
    print("\n[ PHASE 2: VOLUMETRIC TENSOR EVALUATION ]")
    if glyph_sequence:
        approved, vector = translator.translate_hiero(glyph_sequence)
        if not approved:
            print("\n[ EMERGENCY HALT ]")
            print("Execution terminated. The intent did not pass the Billion Barrier constraint.")
            print("Action: SILENCE.")
            sys.exit(1)
    else:
        print("  [>] No recognized hierarchical glyphs in sequence. Proceeding to Linear Stack Evaluation.")

    # Step 3: Run the Genlex linear stack machine
    print("\n[ PHASE 3: MANIFESTATION ]")
    mapping_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'genlex_mapping.csv')
    runtime = GenlexLinearRuntime(mapping_file)
    runtime.run(target_file)

if __name__ == "__main__":
    main()
