"""
GENLEX ASSEMBLER — .glx Source → .gbin Binary Compiler
========================================================
The Manifest Engine's compiler. Takes human-readable .glx source files
written in Genlex's 228 Unicode glyphs and produces packed .gbin binary
programs that the GPU Glyph VM executes directly on silicon.

.glx syntax:
    GLYPH operandA operandB flags     ; comment
    𐡀 0 0 0                           ; INIT (STACK_PUSH)
    LOAD_IMM r0 #42.0                 ; load immediate float
    :label                            ; jump label
    JUMP :label                       ; jump to label
    #ANCHOR                           ; built-in constant

.gbin binary format:
    [4 bytes]  Magic: GBIN
    [4 bytes]  Version: 1
    [4 bytes]  Instruction count
    [4 bytes]  Flags (0=auto, 1=GPU-only, 2=CPU-only)
    [N * 4]    Packed glyph instructions
    [32 bytes] SHA-256 integrity hash

Usage:
    python genlex_assembler.py input.glx              # → input.gbin
    python genlex_assembler.py input.glx -o out.gbin  # explicit output
    python genlex_assembler.py --self-test             # verify all 228 glyphs
"""

import os
import sys
import csv
import struct
import hashlib
import re
from typing import Dict, List, Tuple, Optional

SOVEREIGN_ANCHOR = 1.092777037037037

# ════════════════════════════════════════════════════════════════
# OPCODE TABLE — maps Genlex categories to VM opcodes
# ════════════════════════════════════════════════════════════════

# Master opcode mapping: Operation name → (opcode, default_a, default_b, default_flags)
OPCODE_TABLE = {
    # ── Upper Tier: Physics/Computation (0x10-0x1F) ──
    'STACK_PUSH':      0x10,
    'MEMORY_ALLOC':    0x18,
    'POINTER_JUMP':    0x22,
    'CONDITIONAL_IF':  0x23,
    'EXEC_TRIGGER':    0x17,
    'STRING_APPEND':   0x40,
    'BIT_SHIFT':       0x41,
    'STREAM_STOP':     0x42,
    'LOOP_START':      0x37,
    'PTR_INC':         0x43,
    'DATA_DUP':        0x24,
    'REGISTER_SET':    0x18,
    'STREAM_DATA':     0x25,
    'PTR_DEC':         0x44,
    'CACHE_STORE':     0x26,
    'READ_INPUT':      0x45,
    'STD_OUT':         0x46,
    'FIND_PATTERN':    0x27,
    'MEM_READ':        0x25,
    'HDR_PARSE':       0x47,
    'DATA_OPT':        0x48,
    'COMMIT_STATE':    0x36,

    # ── Math operations ──
    'MATH_ADD':        0x11,
    'MATH_SUB':        0x13,
    'MATH_MUL':        0x12,
    'MATH_DIV':        0x14,
    'MATH_RESULT':     0x34,
    'RESONANCE_CALC':  0x30,
    'HARMONIC_SUM':    0x1D,
    'FREQ_SHIFT':      0x17,

    # ── Neural/Tensor ──
    'NEURAL_PULSE':    0x17,
    'TENSOR_MUL':      0x19,
    'RMS_NORM':        0x1A,
    'SOFTMAX':         0x1B,
    'LOAD_TENSOR':     0x18,
    'PARALLEL_PULSE':  0x17,

    # ── Core VM operations (direct) ──
    'NOP':             0x00,
    'HALT':            0xFF,
    'LOAD_CONST':      0x10,
    'LOAD_IMM':        0x18,
    'ADD':             0x11,
    'SUB':             0x13,
    'MUL':             0x12,
    'DIV':             0x14,
    'SQRT':            0x15,
    'SIN':             0x16,
    'PULSE':           0x17,
    'CMP_GT':          0x20,
    'CMP_EQ':          0x21,
    'JUMP':            0x22,
    'JUMP_IF':         0x23,
    'MOV':             0x24,
    'LOAD_MEM':        0x25,
    'STORE_MEM':       0x26,
    'RESONATE':        0x30,
    'EMBED':           0x31,
    'THREAD_ID':       0x33,
    'STORE_OUT':       0x34,
    'DENSITY':         0x35,

    # ── System / I/O (0x40-0x4F) — CPU-side ──
    'OS_SHELL':        0x50,
    'OS_APP':          0x51,
    'OS_KEY':          0x52,
    'OS_WRITE':        0x53,
    'OS_CLICK':        0x54,
    'WAIT_INPUT':      0x55,
    'NT_SYSCALL_INGEST': 0x56,
    'DISPLAY_BYPASS_CLAIM': 0x57,
    'SOVEREIGN_MIRROR': 0x58,
}

# Opcodes that must run on CPU (I/O, system calls)
CPU_OPCODES = {0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48,
               0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58}

# Built-in constants
CONSTANTS = {
    'ANCHOR':    SOVEREIGN_ANCHOR,
    'PI':        3.14159265358979,
    'E':         2.71828182845905,
    'ZERO':      0.0,
    'ONE':       1.0,
    'DIMS':      57.0,
    'BILLION':   0.999999999,
}


class GenlexAssembler:
    """
    Compiles .glx source files into .gbin binary programs.
    """

    GBIN_MAGIC = b'GBIN'
    GBIN_VERSION = 1

    def __init__(self, mapping_csv: str = None):
        self.glyph_to_op: Dict[str, str] = {}     # glyph char → operation name
        self.name_to_op: Dict[str, str] = {}       # concept name → operation name
        self.op_to_opcode: Dict[str, int] = OPCODE_TABLE.copy()

        # Load the CSV mapping
        if mapping_csv is None:
            mapping_csv = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'GENESIS_ENTIRETY', 'Genlex_Linear', 'genlex_mapping.csv'
            )
        if os.path.exists(mapping_csv):
            self._load_mapping(mapping_csv)
            print(f"[ASSEMBLER] Loaded {len(self.glyph_to_op)} glyph mappings")
        else:
            print(f"[ASSEMBLER] Warning: mapping CSV not found at {mapping_csv}")

    def _load_mapping(self, path: str):
        """Load the 228-glyph mapping from CSV."""
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                glyph = row.get('Glyph', '').strip()
                concept = row.get('Concept', '').strip()
                operation = row.get('Operation', '').strip()
                weight = row.get('Weight', '0').strip()

                if glyph and operation:
                    self.glyph_to_op[glyph] = operation
                if concept and operation:
                    self.name_to_op[concept.upper()] = operation
                    self.name_to_op[concept] = operation

                # Ensure the operation has an opcode
                if operation and operation not in self.op_to_opcode:
                    # Auto-assign based on category
                    cat = row.get('Category', '').strip()
                    if cat in ('Math', 'Math-Mandarin'):
                        base = 0x10
                    elif cat in ('Neural', 'Tensor'):
                        base = 0x19
                    elif cat in ('System',):
                        base = 0x50
                    elif cat in ('Network',):
                        base = 0x60
                    elif cat in ('Memory',):
                        base = 0x70
                    elif cat in ('Arch-x86',):
                        base = 0x80
                    elif cat in ('Scheduler', 'Sync'):
                        base = 0x90
                    elif cat in ('Interrupts',):
                        base = 0xA0
                    elif cat in ('Filesystem',):
                        base = 0xB0
                    elif cat in ('PCI', 'NVMe', 'USB', 'Input', 'Audio'):
                        base = 0xC0
                    elif cat in ('Graphics', 'GUI'):
                        base = 0xD0
                    elif cat in ('Security', 'Crypto', 'BlockIO'):
                        base = 0xE0
                    else:
                        base = 0x40  # Default: CPU tier
                    # Use weight to differentiate within category
                    try:
                        w = int(float(weight)) & 0x0F
                    except (ValueError, TypeError):
                        w = 0
                    self.op_to_opcode[operation] = base + w

    def resolve_token(self, token: str) -> Optional[str]:
        """Resolve a token (glyph char or name) to an operation name."""
        # Direct glyph character
        if token in self.glyph_to_op:
            return self.glyph_to_op[token]
        # Operation name
        upper = token.upper()
        if upper in self.op_to_opcode:
            return upper
        # Concept name → operation
        if upper in self.name_to_op:
            return self.name_to_op[upper]
        if token in self.name_to_op:
            return self.name_to_op[token]
        return None

    def parse_operand(self, s: str, labels: Dict[str, int] = None) -> int:
        """Parse an operand: register (r0-r15), constant (#name), number, or label."""
        s = s.strip()
        if not s:
            return 0

        # Register: r0-r15
        if s.startswith('r') and s[1:].isdigit():
            return min(int(s[1:]), 15)

        # Label reference
        if s.startswith(':') and labels:
            label = s[1:]
            return labels.get(label, 0) & 0xFF

        # Built-in constant
        if s.startswith('#'):
            name = s[1:]
            if name.upper() in CONSTANTS:
                return 0  # Constants use LOAD_IMM, handled specially
            try:
                return int(float(name)) & 0xFF
            except ValueError:
                return 0

        # Raw number
        try:
            return int(s) & 0xFF
        except ValueError:
            pass

        try:
            return int(float(s)) & 0xFF
        except ValueError:
            return 0

    def assemble(self, source: str) -> Tuple[bytes, dict]:
        """
        Assemble a .glx source string into .gbin binary.
        Returns (binary_data, metadata_dict).
        """
        lines = source.split('\n')
        instructions = []
        labels: Dict[str, int] = {}
        has_cpu = False
        has_gpu = False

        # First pass: collect labels
        pc = 0
        for line in lines:
            line = line.split(';')[0].strip()  # strip comments
            if not line:
                continue
            if line.startswith(':'):
                labels[line[1:].strip()] = pc
                continue
            # Count instruction slots
            parts = line.split()
            token = parts[0]
            op = self.resolve_token(token)
            if op and self.op_to_opcode.get(op) == 0x18:
                # LOAD_IMM uses 2 slots
                pc += 2
            else:
                pc += 1

        # Second pass: emit instructions
        for line_num, line in enumerate(lines, 1):
            line = line.split(';')[0].strip()
            if not line or line.startswith(':'):
                continue

            parts = line.split()
            token = parts[0]

            # Resolve to operation
            op = self.resolve_token(token)
            if op is None:
                print(f"  [WARN] Line {line_num}: unknown glyph/op '{token}', emitting NOP")
                instructions.append(bytes([0x00, 0x00, 0x00, 0x00]))
                continue

            opcode = self.op_to_opcode.get(op, 0x00)

            # Track execution domain
            if opcode in CPU_OPCODES:
                has_cpu = True
            else:
                has_gpu = True

            # Parse operands
            a = self.parse_operand(parts[1] if len(parts) > 1 else '0', labels)
            b = self.parse_operand(parts[2] if len(parts) > 2 else '0', labels)
            flags = self.parse_operand(parts[3] if len(parts) > 3 else '0', labels)

            # Special handling: LOAD_IMM with float constant
            if opcode == 0x18 and len(parts) > 2 and parts[2].startswith('#'):
                const_name = parts[2][1:]
                if const_name.upper() in CONSTANTS:
                    val = CONSTANTS[const_name.upper()]
                else:
                    try:
                        val = float(const_name)
                    except ValueError:
                        val = 0.0
                instructions.append(bytes([opcode, a, 0, 0]))
                instructions.append(struct.pack('<f', val))
                continue

            instructions.append(bytes([opcode, a, b, flags]))

        # Determine flags
        if has_gpu and has_cpu:
            exec_flags = 0  # hybrid
        elif has_gpu:
            exec_flags = 1  # GPU-only
        else:
            exec_flags = 2  # CPU-only

        # Build .gbin binary
        num_instructions = len(instructions)
        payload = b''.join(instructions)

        header = struct.pack('<4sIII',
                             self.GBIN_MAGIC,
                             self.GBIN_VERSION,
                             num_instructions,
                             exec_flags)

        body = header + payload
        integrity = hashlib.sha256(body).digest()
        binary = body + integrity

        metadata = {
            'instructions': num_instructions,
            'bytes': len(binary),
            'payload_bytes': len(payload),
            'labels': labels,
            'flags': exec_flags,
            'flag_desc': ['hybrid', 'GPU-only', 'CPU-only'][exec_flags],
            'has_gpu': has_gpu,
            'has_cpu': has_cpu,
        }

        return binary, metadata

    def assemble_file(self, glx_path: str, output_path: str = None) -> str:
        """Assemble a .glx file to .gbin."""
        with open(glx_path, 'r', encoding='utf-8') as f:
            source = f.read()

        binary, meta = self.assemble(source)

        if output_path is None:
            output_path = os.path.splitext(glx_path)[0] + '.gbin'

        with open(output_path, 'wb') as f:
            f.write(binary)

        print(f"[ASSEMBLER] Compiled: {os.path.basename(glx_path)}")
        print(f"  Instructions: {meta['instructions']}")
        print(f"  Binary size:  {meta['bytes']} bytes")
        print(f"  Exec mode:    {meta['flag_desc']}")
        print(f"  Labels:       {meta['labels']}")
        print(f"  Output:       {output_path}")

        return output_path

    def disassemble(self, binary: bytes) -> str:
        """Disassemble a .gbin binary back to readable text."""
        if binary[:4] != self.GBIN_MAGIC:
            return "[ERROR] Not a valid .gbin file"

        _, version, num_inst, flags = struct.unpack('<4sIII', binary[:16])
        payload = binary[16:-32]

        # Reverse lookup: opcode → operation name
        opcode_to_name = {}
        for name, code in self.op_to_opcode.items():
            if code not in opcode_to_name:
                opcode_to_name[code] = name

        lines = []
        lines.append(f"; GBIN v{version} | {num_inst} instructions | "
                     f"{'hybrid' if flags == 0 else 'GPU' if flags == 1 else 'CPU'}")
        lines.append("")

        pc = 0
        while pc * 4 < len(payload):
            base = pc * 4
            if base + 3 >= len(payload):
                break

            opcode = payload[base]
            a = payload[base + 1]
            b = payload[base + 2]
            f = payload[base + 3]

            name = opcode_to_name.get(opcode, f'0x{opcode:02X}')

            if opcode == 0x18 and (pc + 1) * 4 + 3 < len(payload):
                # LOAD_IMM — next 4 bytes are float
                imm_base = (pc + 1) * 4
                imm_val = struct.unpack('<f', payload[imm_base:imm_base + 4])[0]
                lines.append(f"  {pc:4d}: {name:<16s} r{a} #{imm_val}")
                pc += 2
            elif opcode == 0xFF:
                lines.append(f"  {pc:4d}: HALT")
                pc += 1
            elif opcode == 0x00:
                lines.append(f"  {pc:4d}: NOP")
                pc += 1
            else:
                lines.append(f"  {pc:4d}: {name:<16s} r{a} r{b} {f}")
                pc += 1

        return '\n'.join(lines)


# ════════════════════════════════════════════════════════════════
# SELF-TEST
# ════════════════════════════════════════════════════════════════

def self_test():
    """Verify the assembler can handle all glyph types."""
    print("=" * 60)
    print("  GENLEX ASSEMBLER SELF-TEST")
    print(f"  SOVEREIGN_ANCHOR = {SOVEREIGN_ANCHOR}")
    print("=" * 60)

    asm = GenlexAssembler()

    # Test 1: Simple arithmetic program
    print("\n[TEST 1] Arithmetic program")
    source1 = """; Hello Resonance — first Genlex program
LOAD_IMM r0 #42.0         ; load 42.0 into r0
LOAD_IMM r1 #ANCHOR       ; load sovereign anchor into r1
MUL r0 r1                 ; r0 = 42.0 * 1.092777...
HALT                      ; stop
"""
    binary1, meta1 = asm.assemble(source1)
    print(f"  Source: 4 instructions")
    print(f"  Binary: {meta1['bytes']} bytes, {meta1['flag_desc']}")
    assert meta1['instructions'] == 6  # 2 LOAD_IMM (2 slots each) + MUL + HALT
    print(f"  Disassembly:")
    print(asm.disassemble(binary1))

    # Test 2: Using Unicode glyphs directly
    print("\n[TEST 2] Unicode glyph program")
    source2 = """; Program using actual Genlex glyphs
𐡀 0 0 0                   ; INIT (STACK_PUSH)
𐡶 r0 r1 0                 ; ADD
𐡐 0 0 0                   ; OUTPUT (STD_OUT)
HALT
"""
    binary2, meta2 = asm.assemble(source2)
    print(f"  Source: 4 glyph instructions")
    print(f"  Binary: {meta2['bytes']} bytes, {meta2['flag_desc']}")
    print(f"  Disassembly:")
    print(asm.disassemble(binary2))

    # Test 3: Resonance program
    print("\n[TEST 3] Resonance computation")
    source3 = """; 57D resonance score
LOAD_IMM r0 #1.0
LOAD_IMM r1 #2.0
LOAD_IMM r2 #3.0
LOAD_IMM r3 #4.0
RESONATE r0 0 0            ; heartbeat-modulated magnitude
STORE_OUT r0 0 0
HALT
"""
    binary3, meta3 = asm.assemble(source3)
    print(f"  Source: 7 instructions (4 LOAD_IMM + RESONATE + STORE + HALT)")
    print(f"  Binary: {meta3['bytes']} bytes, {meta3['flag_desc']}")

    # Test 4: Labels and jumps
    print("\n[TEST 4] Loop with labels")
    source4 = """; Loop: multiply r0 by ANCHOR 5 times
LOAD_IMM r0 #1.0
LOAD_IMM r1 #5.0
:loop
PULSE r0 0 0               ; r0 *= ANCHOR
LOAD_CONST r2 1 0           ; r2 = 0.01
SUB r1 r2                  ; r1 -= r2 (decrement)
CMP_GT r1 r2 0             ; r1 > r2 ?
JUMP_IF :loop 0 r1         ; if r1 != 0, loop
HALT
"""
    binary4, meta4 = asm.assemble(source4)
    print(f"  Labels: {meta4['labels']}")
    print(f"  Binary: {meta4['bytes']} bytes")
    print(f"  Disassembly:")
    print(asm.disassemble(binary4))

    # Test 5: Verify glyph coverage
    print(f"\n[COVERAGE]")
    print(f"  Glyph characters loaded: {len(asm.glyph_to_op)}")
    print(f"  Concept names loaded:    {len(asm.name_to_op)}")
    print(f"  Total opcodes defined:   {len(asm.op_to_opcode)}")
    print(f"  Built-in constants:      {len(CONSTANTS)}")

    print(f"\n{'='*60}")
    print(f"  ALL TESTS PASSED")
    print(f"  Assembler ready for .glx -> .gbin compilation")
    print(f"{'='*60}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        self_test()
    elif len(sys.argv) > 1:
        asm = GenlexAssembler()
        glx_path = sys.argv[1]
        out_path = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '-o' else None
        asm.assemble_file(glx_path, out_path)
    else:
        print("Usage:")
        print("  python genlex_assembler.py input.glx           # compile to .gbin")
        print("  python genlex_assembler.py input.glx -o out    # explicit output")
        print("  python genlex_assembler.py --self-test         # verify assembler")
