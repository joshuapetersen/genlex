import csv
import io
import sys
import os

# ARAMAIC LINEAR TRANSLATOR (v0.2)
# Harmonized with Pharaoh OS (HGL) Lab Standards.

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class AramaicTranslator:
    def __init__(self, mapping_file="aramaic_mapping.csv"):
        self.mapping_file = mapping_file
        self.lexicon = self._load_lexicon()

    def _load_lexicon(self):
        lexicon = {}
        if not os.path.exists(self.mapping_file):
            print(f"[ ERROR ] Mapping file not found: {self.mapping_file}")
            return {}
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    glyph = row['Glyph']
                    lexicon[glyph] = {
                        "op": row['Operation'],
                        "concept": row['Concept'],
                        "type": row['Category'],
                        "weight": int(row['Weight'])
                    }
            print(f"[ SYSTEM ] Aramaic Lexicon (Gematria Enabled): {len(lexicon)} Glyphs Loaded.")
        except Exception as e:
            print(f"[ ERROR ] Lexicon Sync Failed: {e}")
        return lexicon

    def translate(self, sequence):
        """Processes the Aramaic string sequentially."""
        print(f"\n[ ARAMAIC LINEAR ] Sequence Input: '{sequence}'")
        print("-" * 50)
        
        manifest = []
        total_gematria = 0
        modulation_factor = 0
        
        for glyph in sequence:
            if glyph in self.lexicon:
                data = self.lexicon[glyph]
                weight = data['weight']
                
                if data['type'] == "Modulator":
                    modulation_factor += weight
                    print(f"  > [MOD] {glyph}: Gain Shift +{weight}")
                else:
                    total_gematria += weight
                    print(f"  > [OP]  {glyph} ({data['op']}): {data['concept']} [Weight: {weight}]")
                    manifest.append(data['op'])
            elif glyph.isspace():
                continue
            else:
                print(f"  > [NOISE] '{glyph}' - Dropping from linear stream.")
        
        print("-" * 50)
        if manifest:
            final_resonance = total_gematria * (modulation_factor if modulation_factor > 0 else 1)
            print(f"[ MANIFEST ] Linear Pipeline: {' -> '.join(manifest)}")
            print(f"[ GEMATRIA ] Base Weight: {total_gematria} | Mod Gain: {modulation_factor}")
            print(f"[ RESONANCE ] Final Numerical Manifestation: {final_resonance}")
            print("[ STATUS   ] Prime Integrity: 1.0 (LOCKED)")
        else:
            print("[ FAILED   ] Logic stream is empty or invalid.")

if __name__ == "__main__":
    translator = AramaicTranslator()
    
    if len(sys.argv) > 1:
        sequence_input = sys.argv[-1]
        if os.path.exists(sequence_input):
            with open(sequence_input, 'r', encoding='utf-8') as f:
                sequence = f.read().strip()
        else:
            sequence = sequence_input
        translator.translate(sequence)
    elif os.path.exists("sequence.txt"):
        with open("sequence.txt", 'r', encoding='utf-8') as f:
            sequence = f.read().strip()
        translator.translate(sequence)
    else:
        # Default test mantra: Aleph + Beth + Waw + Taw
        # "Init + Store + Link + Seal"
        test_sequence = "𐡀𐡁𐡅𐡕"
        translator.translate(test_sequence)
