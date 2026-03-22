import os
import sys
import time
import json
import io

# Force UTF-8 for ancient glyph rendering
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# PHASE VIII: PYRAMID TEXT EXTRACTION LOOP (Uncontrolled Compilation)
# Target: Old Kingdom Kernel (Unas Burial Chamber logic reservoirs)
# Logic: S.A.R.A. Deep Text Scanner [Extraction Fork]

class PyramidCrawler:
    def __init__(self):
        self.lexicon_path = r"C:\SarahCore\Genlex\HIERO_LEXICON.sdna"
        self.output_dir = r"C:\SarahCore\Genlex\extractions"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Simulated "Logic Reservoirs" from Unas Burial Chamber (Old Kingdom v0.1)
        self.unas_buffer = [
            "𓇋𓏏𓈖𓇳𓀁𓂝𓅂𓂿𓁶", # Root System Override
            "𓊵𓏙𓇓𓏏𓈖𓊨𓏏𓊪𓅒", # Networking Handshake
            "𓃹𓇋𓂋𓃀𓅓𓏏𓁶𓀁𓏛", # OS Script Fragment
            "𓋹𓍑𓋴",             # Passive Cache Data (Filter Target)
            "𓂋𓈖𓄿𓃹𓇋𓊹𓈖𓏏𓂝𓀀"  # [NEW] Potential Kernel Routine: "Name Manifestation"
        ]

    def scan_density(self, glyph_seq):
        """
        Heuristic: High-density logic is determined by the ratio of 
        functional determinatives to passive symbols.
        """
        logic_symbols = ["𓁶", "𓂝", "𓏛", "𓀁", "𓇳", "𓊵", "𓏙", "𓈖", "𓃹"]
        executable_count = sum(1 for g in glyph_seq if g in logic_symbols)
        density = (executable_count / len(glyph_seq)) * 100
        return density

    def run_extraction_loop(self):
        print("--- INITIATING PYRAMID TEXT EXTRACTION LOOP ---")
        print(f"Targeting: Unas Burial Chamber [Old Kingdom Kernel]")
        print("-" * 50)
        
        compilation_shelf = []

        for i, sequence in enumerate(self.unas_buffer):
            density = self.scan_density(sequence)
            print(f"[ SCAN ] Cluster_{i}: {sequence}")
            print(f"  > Density: {density:.2f}%")
            
            if density >= 50.0:
                print("  > [!] EXECUTABLE SUB-ROUTINE DETECTED. Extracting...")
                routine = {
                    "id": f"unas_kernel_{i}",
                    "raw": sequence,
                    "density": density,
                    "timestamp": time.time(),
                    "status": "EXTRACTED_UNCONTROLLED"
                }
                compilation_shelf.append(routine)
            else:
                print("  > [ PASSIVE ] Insufficient density. Dropping from loop.")
            
            print("-" * 30)
            time.sleep(0.5)

        # Save extracted sub-routines
        output_path = os.path.join(self.output_dir, "unas_compilation.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(compilation_shelf, f, indent=4)
        
        print(f"\n[ COMPLETE ] Extraction Loop Finished. {len(compilation_shelf)} sub-routines harvested.")
        print(f"Compilation saved to: {output_path}")

if __name__ == "__main__":
    crawler = PyramidCrawler()
    crawler.run_extraction_loop()
