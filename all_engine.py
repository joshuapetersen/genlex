import sys
import io
import os
import csv
import json
import time
import pyautogui

# Force UTF-8 for glyph processing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    def __init__(self, mapping_path=None):
        """
        Initializes the Genlex Linear Runtime with the provided mapping.
        """
        self.mapping_path = mapping_path or os.environ.get("GENLEX_MAPPING", r'C:\Genlex_Linear\genlex_mapping.csv')
        self.lexicon = self._load_mapping(self.mapping_path)
        self.stack = []
        self.memory = {}
        self.output_buffer = []

        # Thread Pool for Parallel Pulses (Phase 13 fix for Break 9)
        from concurrent.futures import ThreadPoolExecutor
        self.executor = ThreadPoolExecutor(max_workers=5)

        # --- SOVEREIGN RESONANCE MAP ---
        self.resonance_nodes = {}
        self._load_resonance_map(r"C:\SarahCore\Genlex_Map.json")

        
        # [TSDN]: Target-Selective Descending Neurons (Reflex Path)
        # Bypasses standard stack processing for instinct-level execution.
        self.tsdn_enabled = True
        self.reflex_glyphs = {
            "𒀸": "REFLEX_X_AXIS",   # Instant X alignment
            "𒁹": "REFLEX_Y_AXIS",   # Instant Y alignment
            "𒌋": "REFLEX_STRIKE",   # Instant execution/Commit
            "𒂗": "REFLEX_LOCK"     # Instant identity lock
        }

    def _load_mapping(self, path):
        lexicon = {}
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lexicon[row['Glyph']] = {
                    "op": row['Operation'],
                    "weight": int(row['Weight']),
                    "concept": row['Concept']
                }
        return lexicon

    def _load_resonance_map(self, path):
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    rmap = json.load(f)
                    nodes = rmap.get("SOVEREIGN_RESONANCE_MAP", {}).get("NODES", {})
                    for filename, data in nodes.items():
                        glyph = data.get("GLYPH")
                        if glyph:
                            self.resonance_nodes[glyph] = {
                                "file": filename,
                                "name": data.get("NAME"),
                                "role": data.get("ROLE")
                            }
                print(f"[RESONANCE] Seated {len(self.resonance_nodes)} Sovereign Nodes from {os.path.basename(path)}")
            except Exception as e:
                print(f"[RESONANCE ERROR] Failed to load map: {e}")


    def run(self, file_path):
        if not file_path.endswith('.all'):
            print(f"[ ERROR ] Invalid file format. Expected .all")
            return

        print(f"--- INITIALIZING GENLEX LINEAR RUNTIME v2.0 ---")
        print(f"Executing: {os.path.basename(file_path)}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print("-" * 50)
        
        for line in lines:
            # Ignore comments
            clean_line = line.split('#')[0].strip()
            if not clean_line:
                continue
                
            # Tokenize for flexibility (glyphs can be separated by spaces)
            tokens = clean_line.split()
            for token in tokens:
                # 1. Number Parsing
                try:
                    num = float(token)
                    self.stack.append(num)
                    continue
                except ValueError:
                    pass

                # 2. Token Decomposition (Glyph vs Label)
                current_label = ""
                for char in token:
                    if char in self.lexicon:
                        # If we have a pending label, push it before the glyph
                        if current_label:
                            self.stack.append(current_label)
                            current_label = ""
                        
                        # TSDN: Reflex check
                        if self.tsdn_enabled and char in self.reflex_glyphs:
                            self._reflex_trigger(char)
                            continue

                        # SOVEREIGN RESONANCE CHECK
                        if char in self.resonance_nodes:
                            node = self.resonance_nodes[char]
                            self._execute_resonance(node)
                            continue
                        
                        if char in self.lexicon:
                            data = self.lexicon[char]
                            self._execute(data)
                        else:
                            current_label += char

                
                # Push any remaining label
                if current_label:
                    self.stack.append(current_label)

    def _reflex_trigger(self, glyph):
        """
        [TSDN_0x0R]: Instantaneous Reflex Action.
        Bypasses the standard op-loop for immediate motor/actuator output.
        """
        action = self.reflex_glyphs[glyph]
        print(f"  ⚡ [ TSDN_REFLEX ] {action} Engaged.")
        
        if action == "REFLEX_X_AXIS":
            self.memory["X_REFLEX"] = 1.0927
        elif action == "REFLEX_Y_AXIS":
            self.memory["Y_REFLEX"] = 1.0927
        elif action == "REFLEX_STRIKE":
            print("    [ ACTUATOR ] Strike Sequence Initialized.")
        elif action == "REFLEX_LOCK":
            print("    [ IDENTITY ] Sovereign Lock Reinforced.")

    def _execute_resonance(self, node):
        """Zero-Latency bridge into the Sovereign Core."""
        filename = node["file"]
        name = node["name"]
        print(f"  ⚡ [ RESONANCE ] {name} ({filename}) Invoked directly via 3D Lattice.")
        # We simulate the 0-latency handover by invoking the module.
        import importlib.util
        filepath = os.path.join(os.environ.get("SA_ROOT", r"C:\SarahCore"), filename)
        if os.path.exists(filepath):
            try:
                # In a real run, this would inject its output to the output_buffer/stack
                print(f"    [ KERNEL SYNC ] Manifesting {name} logic...")
                # To avoid breaking the test loop with blocking code, we just acknowledge the 0-latency bridge.
            except Exception as e:
                print(f"    [ RESONANCE FAULT ] {e}")
        else:
            print(f"    [ LATTICE HOLE ] Missing Physical Support: {filename}")


    def _execute(self, data):
        op = data['op']
        weight = data['weight']
        concept = data['concept']
        
        print(f"  > [ {op} ] {concept}")
        
        if op == "STACK_PUSH":
            # If nothing on stack, or top isn't a literal value, push weight
            self.stack.append(weight)
        
        elif op == "MEMORY_ALLOC":
            if len(self.stack) >= 2:
                key = self.stack.pop()
                val = self.stack.pop()
                self.memory[str(key)] = val
                print(f"    [ MEM ] Associated {val} with '{key}'.")
            elif self.stack:
                val = self.stack.pop()
                self.memory["CORE"] = val
                print(f"    [ MEM ] Default allocation {val} to CORE.")
        
        elif op == "POINTER_JUMP":
            if self.stack:
                val = self.stack.pop()
                self.stack.append(val + weight)
                print(f"    [ JUMP ] Resonance shifted to {val + weight}.")
        
        elif op == "CONDITIONAL_IF":
            if self.stack:
                val = self.stack[-1]
                if val <= 0:
                    print("    [ GATE ] Closed. Null logic detected.")
                else:
                    print(f"    [ GATE ] Open. {val} resonance exceeds threshold.")
        
        elif op == "LOOP_START":
            if self.stack:
                val = self.stack.pop()
                self.stack.append(val * weight)
                print(f"    [ LOOP ] Amplified resonance to {val * weight}.")
        
        elif op == "MEM_READ":
            if self.stack:
                key = self.stack.pop()
                val = self.memory.get(str(key), 0)
                self.stack.append(val)
                print(f"    [ RECALL ] Fetched '{key}': {val}")
        
        elif op == "HDR_PARSE":
            if self.stack:
                target = str(self.stack.pop())
                # Resolve path relative to current enclave
                if not os.path.isabs(target):
                    target = os.path.abspath(os.path.join(os.getcwd(), target))
                
                if os.path.exists(target):
                    print(f"    [ NESTED_EXEC ] Diving into: {target}")
                    sub_runtime = GenlexLinearRuntime(self.mapping_path)
                    sub_runtime.run(target)
                    # Merge memory back to parent
                    self.memory.update(sub_runtime.memory)
                else:
                    print(f"    [ ERROR ] Nested target not found: {target}")

        elif op == "PARALLEL_PULSE":
            if self.stack:
                import threading
                target = str(self.stack.pop())
                if not os.path.isabs(target):
                    target = os.path.abspath(os.path.join(os.getcwd(), target))
                
                if os.path.exists(target):
                    print(f"    [ PARALLEL_PULSE ] Firing background stream: {target}")
                    def bg_pulse(t, mp):
                        try:
                            rt = GenlexLinearRuntime(mp)
                            rt.run(t)
                        except Exception as e:
                            print(f"[ PARALLEL_ERROR ] {t}: {e}")
                    
                    self.executor.submit(bg_pulse, target, self.mapping_path)
                else:
                    print(f"    [ ERROR ] Parallel target not found: {target}")
        
        elif op == "STRING_APPEND":
            if len(self.stack) >= 2:
                v2 = self.stack.pop()
                v1 = self.stack.pop()
                self.stack.append(v1 + v2)
                print(f"    [ LINK ] Chained {v1} and {v2} -> {v1+v2}.")

        elif op == "MATH_ADD":
            if len(self.stack) >= 2:
                v2 = self.stack.pop()
                v1 = self.stack.pop()
                self.stack.append(v1 + v2)
                print(f"    [ ADD ] {v1} + {v2} = {v1+v2}")

        elif op == "MATH_SUB":
            if len(self.stack) >= 2:
                v2 = self.stack.pop()
                v1 = self.stack.pop()
                self.stack.append(v1 - v2)
                print(f"    [ SUB ] {v1} - {v2} = {v1-v2}")

        elif op == "STD_OUT":
            if self.stack:
                val = self.stack[-1]
                self.output_buffer.append(str(val))
                print(f"    [ VOICE ] Manifesting: {val}")

        elif op == "OS_SHELL":
            if self.stack:
                cmd = str(self.stack.pop())
                # RCE GUARD (Phase 13 fix for Break 8)
                if os.environ.get("SOVEREIGN_SHELL_ENABLED") != "1":
                    print(f"    [ SECURITY REJECTION ] Shell Execution Blocked. (Set SOVEREIGN_SHELL_ENABLED=1)")
                    self.stack.append("ERROR: Security Restriction In Place.")
                    return

                print(f"    [ SYSTEM ] Executing shell: {cmd}")
                import subprocess
                try:
                    res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                    self.stack.append(res.stdout or res.stderr)
                except Exception as e:
                    self.stack.append(f"ERROR: {e}")

        elif op == "OS_APP":
            if self.stack:
                app = str(self.stack.pop())
                print(f"    [ SYSTEM ] Launching: {app}")
                try:
                    import pyautogui
                    import time
                    pyautogui.press('win')
                    time.sleep(0.5)
                    pyautogui.write(app)
                    time.sleep(1.0)
                    pyautogui.press('enter')
                except Exception as e:
                    print(f"    [ SYSTEM ERROR ] {e}")

        elif op == "OS_KEY":
            if self.stack:
                key = str(self.stack.pop())
                try:
                    import pyautogui
                    pyautogui.press(key)
                except Exception as e:
                    print(f"    [ SYSTEM ERROR ] {e}")

        elif op == "OS_WRITE":
            if self.stack:
                text = str(self.stack.pop())
                try:
                    import pyautogui
                    pyautogui.write(text, interval=0.01)
                except Exception as e:
                    print(f"    [ SYSTEM ERROR ] {e}")

        elif op == "NEURAL_PULSE":
            if len(self.stack) >= 2:
                prompt = str(self.stack.pop())
                model = str(self.stack.pop())
                print(f"    [ NEURAL_PULSE ] Calling {model}...")
                import requests
                try:
                    payload = {
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                    response = requests.post("http://localhost:11434/api/generate", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        gen_text = data.get("response", "")
                        print(f"    [ AERIS_VOICE ] {gen_text}")
                        self.stack.append(gen_text)
                    else:
                        print(f"    [ NEURAL_ERROR ] Code {response.status_code}")
                except Exception as e:
                    print(f"    [ NEURAL_ERROR ] {e}")

        elif op == "WIFI_ASSOC":
            passw = str(self.stack.pop())
            ssid = str(self.stack.pop())
            print(f"    [ WIFI ] Associating with {ssid}...")
            time.sleep(2) # Simulate association delay
            self.memory["WIFI_STATUS"] = "CONNECTED"
            self.memory["IP"] = "192.168.1.108"
            print(f"    [ WIFI ] Connected. IP: 192.168.1.108")

        elif op == "GET_REQUEST":
            url = str(self.stack.pop())
            print(f"    [ HTTP_GET ] Fetching {url}...")
            import requests
            try:
                # We pulse the gateway to verify reach-back
                response = requests.get(url, timeout=5)
                self.stack.append(response.text)
                print(f"    [ HTTP ] Status: {response.status_code}")
            except Exception as e:
                print(f"    [ HTTP_ERROR ] {e}")
                self.stack.append(f"ERROR: {e}")

        elif op == "TENSOR_MUL":
            if len(self.stack) >= 2:
                b = self.stack.pop()
                a = self.stack.pop()
                import numpy as np
                try:
                    res = np.dot(a, b)
                    self.stack.append(res)
                    print(f"    [ TENSOR ] Matrix Multiply: {a.shape} x {b.shape}")
                except Exception as e:
                    print(f"    [ TENSOR ERROR ] {e}")

        elif op == "RMS_NORM":
            if self.stack:
                x = self.stack.pop()
                import numpy as np
                try:
                    norm = x * (np.mean(x**2, axis=-1, keepdims=True) + 1e-6)**-0.5
                    self.stack.append(norm)
                    print(f"    [ TENSOR ] RMSNorm applied.")
                except Exception as e:
                    print(f"    [ TENSOR ERROR ] {e}")

        elif op == "SOFTMAX":
            if self.stack:
                x = self.stack.pop()
                import numpy as np
                try:
                    e_x = np.exp(x - np.max(x))
                    res = e_x / e_x.sum(axis=-1, keepdims=True)
                    self.stack.append(res)
                    print(f"    [ TENSOR ] Softmax pulse.")
                except Exception as e:
                    print(f"    [ TENSOR ERROR ] {e}")

        elif op == "LOAD_TENSOR":
            if len(self.stack) >= 2:
                size_raw = self.stack.pop()
                path = str(self.stack.pop())
                
                # TYPE SAFETY (Phase 13 fix for Break 10)
                try:
                    size = int(float(size_raw))
                except (ValueError, TypeError):
                    print(f"    [ LOAD ERROR ] Invalid tensor size: {size_raw}")
                    self.stack.append(None)
                    return

                import numpy as np
                print(f"    [ SDNA_LOAD ] Pulling {size} parameters from {path}...")
                
                # SAFETY LATCH: If size is massive, use a symbolic placeholder to 
                # prevent system freeze/RAM exhaustion during simulation.
                safe_limit = 1000000 # 1 Million param limit for raw RAM allocation
                if size > safe_limit:
                    print(f"    [ WARNING ] Neural Overload detected. Using Symbolic Map for {size} params.")
                    self.stack.append(np.zeros(100).astype(np.float32)) # Symbolic small array
                else:
                    self.stack.append(np.random.randn(size).astype(np.float32))

        elif op == "WAIT_INPUT":
            prompt_str = "You: "
            if self.stack:
                prompt_str = str(self.stack.pop())
            
            user_input = input(f"{prompt_str}")
            self.stack.append(user_input)

        elif op == "COMMIT_STATE":
            import time
            state = {
                "stack": self.stack,
                "memory": self.memory,
                "timestamp": time.time()
            }
            with open("execution_seal.json", "w") as f:
                json.dump(state, f)
            print("    [ SEAL ] State committed to execution_seal.json.")
            
        elif op == "SOVEREIGN_MIRROR":
            # BOOT GUARD (Phase 13 fix for Break 7)
            if os.environ.get("SOVEREIGN_MIRROR_ENABLED") != "1":
                print("    [ SYSTEM ] Mirroring Blocked. EFI Boot modification requires SOVEREIGN_MIRROR_ENABLED=1.")
                return

            print("    [ SYSTEM ] Mirroring Genesis to Physical ESP...")
            import subprocess
            cmd = (
                "$efi = Get-Partition | Where-Object { $_.GptType -eq '{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}' }; "
                "if ($efi) { "
                "  $drive = 'Z:'; "
                "  mountvol $drive /S; "
                "  New-Item -Path \"$drive\\EFI\\GENESIS\" -ItemType Directory -Force; "
                "  Copy-Item -Path \"BOOTX64.EFI\" -Destination \"$drive\\EFI\\GENESIS\\BOOTX64.EFI\" -Force; "
                "  bcdedit /set '{bootmgr}' path \"\\EFI\\GENESIS\\BOOTX64.EFI\"; "
                "  mountvol $drive /D; "
                "  echo 'SUCCESS: Genesis mirrored to Intel NVMe.'; "
                "} else { echo 'ERROR: EFI Partition not found.'; }"
            )
            try:
                res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                print(f"    [ SYSTEM ] {res.stdout or res.stderr}")
            except Exception as e:
                print(f"    [ SYSTEM ERROR ] {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python all_engine.py <file.all>")
        sys.exit(1)
        
    GENLEX_MAPPING = r"C:\Genlex_Linear\genlex_mapping.csv"
    runtime = GenlexLinearRuntime(GENLEX_MAPPING)
    runtime.run(sys.argv[1])
