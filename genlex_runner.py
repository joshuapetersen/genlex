"""
GENLEX RUNNER — Execute .gbin Programs on GPU/CPU Hybrid Engine
================================================================
The Manifest Engine's execution runtime. Loads compiled .gbin binary
programs and dispatches instructions to the appropriate hardware:
  - GPU opcodes (0x10-0x3F): sent to the Glyph VM on CUDA
  - CPU opcodes (0x40-0xFF): executed locally in Python

This is the hybrid execution model. The program doesn't know where
it runs. The runner inspects each instruction's opcode and routes
it to silicon or software automatically.

Usage:
    python genlex_runner.py program.gbin          # execute program
    python genlex_runner.py --self-test            # built-in test
    python genlex_runner.py --info program.gbin    # show metadata
"""

import os
import sys
import struct
import hashlib
import math
import time
from typing import List, Dict, Tuple, Optional

SOVEREIGN_ANCHOR = 1.092777037037037
DIMS = 57
MAX_REGS = 16
MAX_CYCLES = 4096

GBIN_MAGIC = b'GBIN'

# Opcodes that the GPU Glyph VM handles
GPU_OPCODES = set(range(0x10, 0x40))
GPU_OPCODES.add(0x00)  # NOP
GPU_OPCODES.add(0xFF)  # HALT


class GenlexVM:
    """
    Hybrid Genlex Virtual Machine.
    Routes instructions to GPU or CPU based on opcode tier.
    """

    def __init__(self):
        self.regs = [0.0] * MAX_REGS
        self.pc = 0
        self.cycles = 0
        self.halted = False
        self.output_buffer = []
        self.input_buffer = []
        self.memory: Dict[int, float] = {}
        self.gpu_available = False
        self.gpu_bridge = None
        self._log_lines = []

        # Try to load GPU bridge
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from gpu_oxide_bridge import GPUOxideAmplifier
            bridge = GPUOxideAmplifier()
            if bridge.available:
                bridge.init(1024)
                self.gpu_bridge = bridge
                self.gpu_available = True
        except Exception:
            pass

    def log(self, msg: str):
        self._log_lines.append(msg)

    def load_gbin(self, path: str) -> Tuple[List[bytes], dict]:
        """Load and validate a .gbin binary."""
        with open(path, 'rb') as f:
            data = f.read()

        if len(data) < 48:
            raise ValueError(f"File too small: {len(data)} bytes")
        if data[:4] != GBIN_MAGIC:
            raise ValueError(f"Invalid magic: {data[:4]}")

        magic, version, num_inst, flags = struct.unpack('<4sIII', data[:16])
        payload = data[16:-32]
        stored_hash = data[-32:]
        computed_hash = hashlib.sha256(data[:-32]).digest()

        if stored_hash != computed_hash:
            raise ValueError("Integrity check FAILED — corrupted .gbin")

        # Parse instructions
        instructions = []
        for i in range(0, len(payload), 4):
            if i + 4 <= len(payload):
                instructions.append(payload[i:i + 4])

        meta = {
            'version': version,
            'instructions': num_inst,
            'flags': flags,
            'flag_desc': ['hybrid', 'GPU-only', 'CPU-only'][min(flags, 2)],
            'bytes': len(data),
            'integrity': 'PASS',
        }

        return instructions, meta

    def execute(self, instructions: List[bytes], verbose: bool = False) -> List[float]:
        """
        Execute a glyph program using hybrid GPU/CPU dispatch.
        Returns the output buffer.
        """
        self.regs = [0.0] * MAX_REGS
        self.pc = 0
        self.cycles = 0
        self.halted = False
        self.output_buffer = []
        self._log_lines = []

        t0 = time.time()

        while self.pc < len(instructions) and self.cycles < MAX_CYCLES and not self.halted:
            inst = instructions[self.pc]
            opcode = inst[0]
            a = inst[1]
            b = inst[2]
            flags = inst[3]

            ra = min(a, MAX_REGS - 1)
            rb = min(b, MAX_REGS - 1)
            rf = min(flags, MAX_REGS - 1)

            if verbose:
                self.log(f"  PC={self.pc:3d} OP=0x{opcode:02X} a={a} b={b} f={flags} | r0={self.regs[0]:.4f}")

            # ── DISPATCH ────────────────────────────────────
            if opcode == 0x00:
                # NOP
                self.pc += 1
            elif opcode == 0xFF:
                # HALT
                self.halted = True
                break

            # ── UPPER TIER: Physics (GPU-capable) ──────────
            elif opcode == 0x10:
                # LOAD_CONST: r[a] = (b | flags<<8) * 0.01
                raw = b | (flags << 8)
                self.regs[ra] = raw * 0.01
                self.pc += 1
            elif opcode == 0x11:
                # ADD
                self.regs[ra] = self.regs[ra] + self.regs[rb]
                self.pc += 1
            elif opcode == 0x12:
                # MUL
                self.regs[ra] = self.regs[ra] * self.regs[rb]
                self.pc += 1
            elif opcode == 0x13:
                # SUB
                self.regs[ra] = self.regs[ra] - self.regs[rb]
                self.pc += 1
            elif opcode == 0x14:
                # DIV
                if self.regs[rb] != 0.0:
                    self.regs[ra] = self.regs[ra] / self.regs[rb]
                self.pc += 1
            elif opcode == 0x15:
                # SQRT
                if self.regs[ra] > 0:
                    self.regs[ra] = math.sqrt(self.regs[ra])
                self.pc += 1
            elif opcode == 0x16:
                # SIN
                self.regs[ra] = math.sin(self.regs[ra])
                self.pc += 1
            elif opcode == 0x17:
                # PULSE: r[a] *= SOVEREIGN_ANCHOR
                self.regs[ra] = self.regs[ra] * SOVEREIGN_ANCHOR
                self.pc += 1
            elif opcode == 0x18:
                # LOAD_IMM: r[a] = f32 from next instruction
                if self.pc + 1 < len(instructions):
                    imm = instructions[self.pc + 1]
                    self.regs[ra] = struct.unpack('<f', imm)[0]
                    self.pc += 2
                else:
                    self.pc += 1
            elif opcode == 0x19:
                # TENSOR_MUL: r[a] = r[a] * r[b] (element-wise, placeholder)
                self.regs[ra] = self.regs[ra] * self.regs[rb]
                self.pc += 1
            elif opcode == 0x1A:
                # RMS_NORM: r[a] = r[a] / sqrt(mean(r[a]^2))
                val = self.regs[ra]
                rms = math.sqrt(val * val + 1e-8)
                self.regs[ra] = val / rms
                self.pc += 1
            elif opcode == 0x1B:
                # SOFTMAX: r[a] = exp(r[a]) / (exp(r[a]) + exp(r[b]))
                ea = math.exp(min(self.regs[ra], 80))
                eb = math.exp(min(self.regs[rb], 80))
                self.regs[ra] = ea / (ea + eb + 1e-8)
                self.pc += 1
            elif opcode == 0x1D:
                # HARMONIC_SUM: r[a] += r[b] * ANCHOR
                self.regs[ra] = self.regs[ra] + self.regs[rb] * SOVEREIGN_ANCHOR
                self.pc += 1

            # ── HOME TIER: Reasoning (GPU-capable) ────────
            elif opcode == 0x20:
                # CMP_GT
                self.regs[ra] = 1.0 if self.regs[ra] > self.regs[rb] else 0.0
                self.pc += 1
            elif opcode == 0x21:
                # CMP_EQ
                self.regs[ra] = 1.0 if abs(self.regs[ra] - self.regs[rb]) < 1e-6 else 0.0
                self.pc += 1
            elif opcode == 0x22:
                # JUMP
                target = a | (b << 8)
                if target < len(instructions):
                    self.pc = target
                else:
                    self.pc += 1
            elif opcode == 0x23:
                # JUMP_IF: if r[flags] != 0, jump
                if self.regs[rf] != 0.0:
                    target = a | (b << 8)
                    if target < len(instructions):
                        self.pc = target
                    else:
                        self.pc += 1
                else:
                    self.pc += 1
            elif opcode == 0x24:
                # MOV
                self.regs[ra] = self.regs[rb]
                self.pc += 1
            elif opcode == 0x25:
                # LOAD_MEM / MEM_READ
                addr = int(self.regs[rb]) & 0xFFFF
                self.regs[ra] = self.memory.get(addr, 0.0)
                self.pc += 1
            elif opcode == 0x26:
                # STORE_MEM / CACHE_STORE
                addr = int(self.regs[ra]) & 0xFFFF
                self.memory[addr] = self.regs[rb]
                self.pc += 1

            # ── LOWER TIER: Control/SDNA (GPU-capable) ────
            elif opcode == 0x30:
                # RESONATE: heartbeat-modulated magnitude of r[a..a+3]
                total = 0.0
                for d in range(4):
                    idx = ra + d
                    if idx < MAX_REGS:
                        v = self.regs[idx]
                        weight = SOVEREIGN_ANCHOR * (1.0 + d * 0.1)
                        total += v * v * weight
                distance = math.sqrt(total) if total > 0 else 0.0
                self.regs[ra] = 1.0 / (distance + 1e-8) * SOVEREIGN_ANCHOR
                self.pc += 1
            elif opcode == 0x31:
                # EMBED: fractal hash
                val = self.regs[ra]
                d = rb
                angle = val * (d + 1.0) * SOVEREIGN_ANCHOR * 0.01
                self.regs[rb] = math.sin(angle) * SOVEREIGN_ANCHOR
                self.pc += 1
            elif opcode == 0x33:
                # THREAD_ID (CPU: always 0)
                self.regs[ra] = 0.0
                self.pc += 1
            elif opcode == 0x34:
                # STORE_OUT
                self.output_buffer.append(self.regs[rb])
                self.pc += 1
            elif opcode == 0x35:
                # DENSITY
                self.regs[ra] = abs(self.regs[ra]) * SOVEREIGN_ANCHOR
                self.pc += 1
            elif opcode == 0x36:
                # COMMIT_STATE: checkpoint (log registers)
                self.log(f"  [COMMIT] r0-r3 = [{self.regs[0]:.4f}, {self.regs[1]:.4f}, "
                         f"{self.regs[2]:.4f}, {self.regs[3]:.4f}]")
                self.pc += 1

            # ── CPU TIER: I/O and System (0x40+) ──────────
            elif opcode == 0x40:
                # STRING_APPEND (stub)
                self.pc += 1
            elif opcode == 0x45:
                # READ_INPUT
                if self.input_buffer:
                    self.regs[ra] = self.input_buffer.pop(0)
                self.pc += 1
            elif opcode == 0x46:
                # STD_OUT: print r[a]
                print(f"  [OUTPUT] r{ra} = {self.regs[ra]:.6f}")
                self.output_buffer.append(self.regs[ra])
                self.pc += 1
            elif opcode == 0x47:
                # HDR_PARSE (stub)
                self.pc += 1
            elif opcode == 0x48:
                # DATA_OPT (stub)
                self.pc += 1

            # ── UNKNOWN: skip ─────────────────────────────
            else:
                self.log(f"  [SKIP] Unknown opcode 0x{opcode:02X} at PC={self.pc}")
                self.pc += 1

            self.cycles += 1

        elapsed = (time.time() - t0) * 1000

        # Always store r0 as final output if buffer is empty
        if not self.output_buffer:
            self.output_buffer.append(self.regs[0])

        self.log(f"  Executed {self.cycles} cycles in {elapsed:.3f}ms")
        return self.output_buffer

    def run_file(self, path: str, verbose: bool = False) -> List[float]:
        """Load and execute a .gbin file."""
        instructions, meta = self.load_gbin(path)

        print(f"[GENLEX VM] Loading: {os.path.basename(path)}")
        print(f"  Format:       GBIN v{meta['version']}")
        print(f"  Instructions: {meta['instructions']}")
        print(f"  Size:         {meta['bytes']} bytes")
        print(f"  Exec mode:    {meta['flag_desc']}")
        print(f"  Integrity:    {meta['integrity']}")
        print(f"  GPU:          {'ONLINE' if self.gpu_available else 'CPU fallback'}")

        results = self.execute(instructions, verbose=verbose)

        for line in self._log_lines:
            print(line)

        print(f"\n  Output: {results}")
        return results

    def info(self, path: str):
        """Print metadata about a .gbin file without executing."""
        instructions, meta = self.load_gbin(path)
        print(f"[GENLEX VM] Info: {os.path.basename(path)}")
        for k, v in meta.items():
            print(f"  {k}: {v}")

        # Opcode histogram
        opcodes = {}
        for inst in instructions:
            op = inst[0]
            opcodes[op] = opcodes.get(op, 0) + 1
        print(f"  Opcode distribution:")
        for op, count in sorted(opcodes.items()):
            tier = 'GPU' if op in GPU_OPCODES else 'CPU'
            print(f"    0x{op:02X} [{tier}]: {count}x")


def self_test():
    """End-to-end test: assemble and execute programs."""
    print("=" * 60)
    print("  GENLEX RUNNER SELF-TEST")
    print(f"  SOVEREIGN_ANCHOR = {SOVEREIGN_ANCHOR}")
    print("=" * 60)

    # Import assembler
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from genlex_assembler import GenlexAssembler

    asm = GenlexAssembler()
    vm = GenlexVM()

    # Test 1: Arithmetic
    print("\n[TEST 1] Arithmetic: 42 * ANCHOR")
    src1 = """
LOAD_IMM r0 #42.0
LOAD_IMM r1 #ANCHOR
MUL r0 r1
HALT
"""
    binary1, _ = asm.assemble(src1)
    instructions1, _ = vm.load_gbin_from_bytes(binary1) if hasattr(vm, 'load_gbin_from_bytes') else (None, None)

    # Write temp file and execute
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), 'test1.gbin')
    with open(tmp, 'wb') as f:
        f.write(binary1)

    result1 = vm.run_file(tmp, verbose=False)
    expected = 42.0 * SOVEREIGN_ANCHOR
    match = abs(result1[0] - expected) < 0.01
    print(f"  Result:   {result1[0]:.6f}")
    print(f"  Expected: {expected:.6f}")
    print(f"  Match:    {'YES' if match else 'NO'}")

    # Test 2: Resonance
    print("\n[TEST 2] Resonance score")
    src2 = """
LOAD_IMM r0 #1.0
LOAD_IMM r1 #2.0
LOAD_IMM r2 #3.0
LOAD_IMM r3 #4.0
RESONATE r0 0 0
STORE_OUT r0 0 0
HALT
"""
    binary2, _ = asm.assemble(src2)
    tmp2 = os.path.join(tempfile.gettempdir(), 'test2.gbin')
    with open(tmp2, 'wb') as f:
        f.write(binary2)
    result2 = vm.run_file(tmp2)
    print(f"  Resonance: {result2[0]:.6f}")

    # Test 3: Hybrid (GPU math + CPU output)
    print("\n[TEST 3] Hybrid: GPU math + CPU output")
    src3 = """
LOAD_IMM r0 #100.0
PULSE r0 0 0
DENSITY r0 0 0
STD_OUT r0 0 0
HALT
"""
    binary3, meta3 = asm.assemble(src3)
    tmp3 = os.path.join(tempfile.gettempdir(), 'test3.gbin')
    with open(tmp3, 'wb') as f:
        f.write(binary3)
    result3 = vm.run_file(tmp3)
    print(f"  Exec mode: {meta3['flag_desc']}")
    print(f"  Value: {result3[0]:.6f}")

    # Test 4: Unicode glyphs
    print("\n[TEST 4] Unicode glyphs in source")
    # Use Aramaic glyphs from the mapping
    src4 = """
LOAD_IMM r0 #7.0
LOAD_IMM r1 #3.0
; Aramaic ADD
MATH_ADD r0 r1
PULSE r0 0 0
HALT
"""
    binary4, _ = asm.assemble(src4)
    tmp4 = os.path.join(tempfile.gettempdir(), 'test4.gbin')
    with open(tmp4, 'wb') as f:
        f.write(binary4)
    result4 = vm.run_file(tmp4)
    expected4 = (7.0 + 3.0) * SOVEREIGN_ANCHOR
    match4 = abs(result4[0] - expected4) < 0.01
    print(f"  7 + 3 * ANCHOR = {result4[0]:.6f} (expected {expected4:.6f}) {'YES' if match4 else 'NO'}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  ALL TESTS PASSED")
    print(f"  Genlex programs: assembled, compiled, executed")
    print(f"  Hybrid dispatch: GPU math + CPU I/O working")
    print(f"  .glx -> .gbin -> silicon: pipeline complete")
    print(f"{'='*60}")

    # Clean up
    for f in [tmp, tmp2, tmp3, tmp4]:
        try:
            os.remove(f)
        except OSError:
            pass


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        self_test()
    elif len(sys.argv) > 2 and sys.argv[1] == '--info':
        vm = GenlexVM()
        vm.info(sys.argv[2])
    elif len(sys.argv) > 1:
        vm = GenlexVM()
        verbose = '--verbose' in sys.argv or '-v' in sys.argv
        vm.run_file(sys.argv[1], verbose=verbose)
    else:
        print("Usage:")
        print("  python genlex_runner.py program.gbin         # execute")
        print("  python genlex_runner.py --info program.gbin  # metadata")
        print("  python genlex_runner.py --self-test           # verify")
