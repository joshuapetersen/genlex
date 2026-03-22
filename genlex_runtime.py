import sys
import os
import json
import re

# ADD THE GENESIS BRIDGE TO PATH
sys.path.append(os.path.abspath("./build/Release"))

class GenlexRuntime:
    def __init__(self):
        # Use absolute paths to avoid issues when running from different directories
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.lexicon_path = os.path.join(base_path, "LEXICON.sdna")
        self.lexicon = self._load_lexicon()
        try:
            import genesis_bridge
            self.core = genesis_bridge.GenesisCore("GENLEX_ENGINE_01")
            print("[ SYSTEM ] Genesis C++ Bridge: ONLINE")
        except ImportError:
            # Check build/Release directly if standard import fails
            try:
                sys.path.append(os.path.join(base_path, "build", "Release"))
                import genesis_bridge
                self.core = genesis_bridge.GenesisCore("GENLEX_ENGINE_01")
                print("[ SYSTEM ] Genesis C++ Bridge: ONLINE (Local)")
            except ImportError:
                print("[ ERROR  ] Genesis C++ Bridge: OFFLINE (Run build first)")
                self.core = None

    def _load_lexicon(self):
        """Parses the .sdna lexicon to map QWERTY keys to SI Vectors."""
        lexicon = {}
        if not os.path.exists(self.lexicon_path):
            print(f"[ ERROR  ] Lexicon not found at {self.lexicon_path}")
            return lexicon

        with open(self.lexicon_path, 'r') as f:
            content = f.read()
            # Simple regex to extract key mappings from the custom .sdna format
            matches = re.findall(r'([A-Z]):\s*(\{.*?\})', content)
            for key, val in matches:
                lexicon[key] = json.loads(val)
        return lexicon

    def pulse(self, input_string):
        """The GENLEX Pulse: Consumes a QWERTY sequence and manifests the intent."""
        print(f"\n[ PULSE  ] Sequence: '{input_string}'")
        
        # 1. THE 9+1 INHIBITORY CHECK (SDNA VERIFICATION)
        # In Genlex, if the Billion Barrier isn't met, the manifest fails.
        if self.core:
            # Check density for the entire intent
            density = self.core.calculate_density(1.0)
            if density < 0.999999999:
                print(f"[ FAILED ] SDNA Integrity: {density} (Below Billion Barrier)")
                return
            print(f"[ OK     ] SDNA Integrity: {density} (Billion Barrier PASS)")

        # 2. THE 3+1 MANIFESTATION
        # Process the keys according to the Lexicon
        for char in input_string.upper():
            if char in self.lexicon:
                axiom = self.lexicon[char]
                if "axiom" in axiom:
                    print(f"  > [VOLUMETRIC] {char}: {axiom['axiom']} ({axiom['math']})")
                elif "intent" in axiom:
                    print(f"  > [FLOW]       {char}: {axiom['intent']} (Processor: {axiom['processor']})")
                elif "law" in axiom:
                    print(f"  > [CONTROL]    {char}: {axiom['law']} (Constraint: {axiom['density_check']})")
            elif char == " ":
                print("  > [MANIFEST]   Pulse completed.")

if __name__ == "__main__":
    runtime = GenlexRuntime()
    # Test a "Resonant Chord" (Top row, Home row, Bottom row)
    # Q = Volumetric, A = Neural, Z = Physics Law
    runtime.pulse("QAZ")
