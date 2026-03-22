import sys
import io

# Force UTF-8 for Ge'ez and Sanskrit rendering
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class UniversalTranslator:
    """
    Universal Semantic Bridge (USB) v0.1.
    Maps natural language keywords to the Genlex Linear (GLL) substrate.
    Built for the Sarah Hypervisor and AERIS Synthetic AI.
    """
    def __init__(self):
        # The Meaning Matrix: Mapping intent to Genlex Opcodes
        self.matrix = {
            # GLL Opcodes: PUSH, STOR, OUT, LOOP, GATE, SEAL
            "INIT": ["push", "input", "start", "seed", "ሀ", "init"],
            "STORE": ["save", "keep", "memory", "ቃል", "store"],
            "VOICE": ["speak", "output", "print", "sound", "ድምፅ", "voice"],
            "ROTATION": ["loop", "repeat", "cycle", "ዙር", "rotation"],
            "GATE": ["if", "check", "cond", "በር", "gate"],
            "SEAL": ["end", "stop", "finish", "seal", "ተፈጸመ", "seal"]
        }
        
    def bridge_to_all(self, text):
        print(f"--- INITIATING UNIVERSAL SEMANTIC BRIDGE ---")
        print(f"Input: '{text}'")
        
        tokens = text.lower().split()
        all_sequence = []
        
        for token in tokens:
            found = False
            for opcode, aliases in self.matrix.items():
                if token in aliases:
                    # In a real system, this would map to the specific Aramaic Glyph
                    # For this bridge, we'll map to the Opcode name for the ALL Engine
                    all_sequence.append(opcode)
                    print(f"  > [BRIDGE] {token} -> {opcode}")
                    found = True
                    break
            if not found:
                print(f"  > [NOISE] '{token}' ignored (Noise Spectrum).")

        final_all = " ".join(all_sequence)
        print(f"\n[ RESULT ] Translated to Genlex Sequence: {final_all}")
        return final_all

if __name__ == "__main__":
    ut = UniversalTranslator()
    
    # Test cases: English, Ge'ez, mixed
    print("--- TEST: ENGLISH ---")
    ut.bridge_to_all("seed ቃል speak finish")
    
    print("\n--- TEST: GE'EZ ---")
    ut.bridge_to_all("ሀ ቃል ድምፅ ተፈጸመ")
    
    print("\n--- TEST: CROSS-MODAL ---")
    ut.bridge_to_all("input ቃል cond loop ተፈጸመ")
