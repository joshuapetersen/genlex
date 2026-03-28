import os
import sys
import json
import re

class ALL_Transpiler:
    """
    Sovereign Transpiler: Maps Python logical structures to Aramaic Linear Language (ALL).
    Focuses on zero-jitter execution and direct logic-to-runtime mapping.
    
    ONTOLOGICAL GROUNDING:
    - THE ROCK: High-density core intent (ALL Opcodes).
    - THE SLOSH: Low-density Python boilerplate (Stripped during ingestion).
    - THE PULSE: 1.092777 Hz sync (Header injected).
    """
    
    OPCODES = {
        "PUSH": "𐡀",  # Aleph (STACK_PUSH)
        "STOR": "𐡁",  # Bet (MEMORY_ALLOC)
        "LOAD": "𐡒",  # Qoph (MEM_READ)
        "LOOP": "𐡈",  # Tet (LOOP_START)
        "OUT":  "𐡐",  # Pe (STD_OUT)
        "SEAL": "𐡕",  # Tav (COMMIT_STATE)
        "SYNC": "𐡓",  # Resh (HDR_PARSE / Sync)
        "GATE": "𐡃",  # Dalet (CONDITIONAL_IF)
    }

    def __init__(self):
        self.script = []

    def translate_python_op(self, py_code):
        """Pure glyph mapping for simulation logic."""
        script = []
        
        # Mapping Variables (LOAD/STOR)
        if "=" in py_code and not py_code.startswith("if"):
            script.append(self.OPCODES['PUSH'])
            script.append(self.OPCODES['STOR'])

        # Mapping Output
        if "print" in py_code:
            script.append(self.OPCODES['OUT'])

        # Mapping Loops
        if "while" in py_code or "for" in py_code:
            script.append(self.OPCODES['LOOP'])

        # Mapping Gates
        if "if" in py_code:
            script.append(self.OPCODES['GATE'])

        return "".join(script) # No spaces, pure logical stream

    def transpile_file(self, source_path, target_path):
        print(f"[TRANSPILER] Reading {source_path}...")
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Start with Sovereign Sync Glyph (Resh)
        all_script = [f"{self.OPCODES['SYNC']} 1.0927"] 
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith('"""'):
                continue
            
            translated = self.translate_python_op(line)
            if translated:
                all_script.append(translated)

        all_script.append(self.OPCODES['SEAL']) # End with Commit State (Tav)
        
        final_script = "\n".join(all_script)
        
        print(f"[TRANSPILER] Writing {target_path}...")
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(final_script)
        
        return final_script

if __name__ == "__main__":
    transpiler = ALL_Transpiler()
    # 1. Primordial Earth (Societal & World Engine)
    transpiler.transpile_file(r'C:\SarahCore\PrimordialEarth\Genesis_Societal_Ecology.py', r'C:\PrimordialEarth\primordial_ecology.all')
    transpiler.transpile_file(r'C:\SarahCore\PrimordialEarth\Genesis_World_Engine.py', r'C:\PrimordialEarth\primordial_world.all')
    
    # 2. Aethelgard Narrative logic
    transpiler.transpile_file(r'C:\SarahCore\PrimordialEarth\Genesis_Entity_Chat.py', r'C:\PrimordialEarth\aethelgard_narrative.all')
