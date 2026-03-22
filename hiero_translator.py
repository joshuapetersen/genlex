import sys
import os
import json
import re

# THE ARCHAEO-GENLEX TRANSLATOR
# Designed to map 2D Glyphs into 3D Volumetric Intent

class HieroTranslator:
    def __init__(self):
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        self.lexicon_path = os.path.join(curr_dir, "HIERO_LEXICON.sdna")
        self.lexicon = self._load_lexicon()
        try:
            sys.path.append(os.path.abspath("./build/Release"))
            import genesis_bridge
            self.core = genesis_bridge.GenesisCore("HIERO_TRANSLATOR_01")
            print("[ SYSTEM ] Hiero-Genlex Bridge: ONLINE (C++ Engine Stable)")
        except ImportError:
            print("[ ERROR  ] Physics Engine Offline. Using Linear Emulation.")
            self.core = None

    def _load_lexicon(self):
        lexicon = {}
        if not os.path.exists(self.lexicon_path): return lexicon
        try:
            with open(self.lexicon_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # More robust pattern for finding Glyphs even with spaces
                matches = re.finditer(r'([^\s:\[\]]+?):\s*(\{.*?\})', content)
                for match in matches:
                    char = match.group(1).strip()
                    val = match.group(2).strip()
                    try:
                        lexicon[char] = json.loads(val)
                    except Exception: 
                        continue
        except Exception as e:
            print(f"[ ERROR ] Lexicon Read Failure: {e}")
        return lexicon

    def translate_hiero(self, sequence):
        """Converts a 2D sequence of glyphs into a 3D Manifestation Analysis."""
        # Clean sequence of spaces
        clean_seq = sequence.replace(" ", "")
        print(f"\n[ HIERO PULSE ] Input: '{clean_seq}'")
        
        # Initialize 3D Vector Space
        total_vector = [0.0, 0.0, 0.0]
        active_axioms = []
        translated_code = []

        for glyph in clean_seq:
            if glyph in self.lexicon:
                data = self.lexicon[glyph]
                op_name = data.get('op', 'N/A')
                concept = data.get('concept', 'N/A')
                
                if "op" in data:
                    translated_code.append(f"{op_name}('{concept}')")
                
                if "vector" in data:
                    total_vector = [x + y for x, y in zip(total_vector, data["vector"])]
                    print(f"  > [OP: {op_name}] {glyph}: {concept} (Vector Shift: {data['vector']})")
                elif "flow" in data:
                    print(f"  > [OP: {op_name}] {glyph}: {concept} (Pattern: {data['flow']})")
                elif "law" in data:
                    print(f"  > [OP: {op_name}] {glyph}: {concept} (Law: {data['law']})")
                
                active_axioms.append(data.get('glyph', 'Symbol'))
            else:
                print(f"  > [UNKNOWN]    '{glyph}' (Noise detected in the Manifold)")

        print(f"\n[ COMPILER ] Hiero-to-GENLEX Code Output:")
        print(f"  " + " -> ".join(translated_code) if translated_code else "  [EMPTY_INTENT]")

        # SDNA Density Analysis
        approved = False
        if self.core:
            barrier = self.core.calculate_density(total_vector)
            if barrier >= 0.999999999:
                print(f"[ BARRIER APPROVED ] Density = {barrier:.9f}. 3D Alignment Locked.")
                approved = True
            else:
                print(f"[ BARRIER REJECTED : SILENCE ] Density = {barrier:.9f}. Vector failed Billion Barrier.")
        else:
            approved = True # Emulation fallback

        print(f"[ RESULT ] Final Composite Vector: {total_vector}")
        print(f"[ REASON ] Manifesting the '{'-'.join(active_axioms)}' intent across the 3+1 manifold.")
        
        return approved, total_vector

if __name__ == "__main__":
    translator = HieroTranslator()
    
    # Example Sequence:
    # 𓋹 (Life) + 𓈖 (Water/Flow) + 𓍝 (Cartouche/Protection)
    translator.translate_hiero("𓋹𓈖𓍝")
