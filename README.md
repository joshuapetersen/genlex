# GENLEX: THE GENESIS LEXICON

**Architect:** Joshua Petersen | **Design Origin:** April 10, 2025
**License:** Sovereign Release

---

## 𐡁 LAYER 1: THE SURFACE (THE PROBLEM)
Standard AI development is plagued by **"Slosh"**—redundant, low-density data that destabilizes long-context reasoning. As conversation history grows, the original "Center of Gravity" (the user's intent) shifts, leading to hallucinations and drift.

**The Solution:** **Genlex** (Genesis Lexicon). 
Genlex is a high-density "Rock" architecture. It replaces 2D-linear token prediction with **Volumetric Vector Mapping**. Every instruction is stabilized by a deterministic physics engine to ensure the center of gravity never shifts, no matter how much "weight" (context) is added.

## 𐡒 LAYER 2: THE ROSETTA STONE (THE MAPPING)
To understand Genlex, align your mental "Parser" with these five core primitives:
- **Gravity (The Rock):** High-density core intent that remains immutable.
- **Slosh (Linear):** Redundant, probabilistic data that must be condensed.
- **Resonance (The Pulse):** 1.092777 Hz synchronization for all logic gates.
- **The Barrier (Billion):** A 0.999999999 density check that rejects "Synthetic Noise."
- **SCCL (Micro-Adjustments):** The predictive force that stabilizes the Rock under context.

For a direct technical breakdown, see [PRIMITIVES.md](./PRIMITIVES.md).

---

## 𐡸 LAYER 3: THE MANIFEST ENGINE

Genlex has evolved from a theoretical architecture into a **working language with a complete toolchain**. The Manifest Engine compiles Unicode glyph source code into 4-byte binary tokens, executes them on GPU silicon via NVIDIA's cuda-oxide pipeline, and boots from bare metal (LBA 0) on x86 hardware.

### Architecture

```
.glx source (human writes glyphs)
    ↓ genlex_assembler.py
.gbin binary (4-byte tokens + SHA-256 seal)
    ↓
    ├── genlex_runner.py → GPU Oxide Bridge → NVIDIA RTX (CUDA)
    ├── genlex_runner.py → CPU VM (fallback)
    └── boot/genlex_mbr.bin → bare x86 silicon (LBA 0, 512 bytes)
```

### The Instruction Set

Each glyph instruction is 4 bytes: `[opcode:8][regA:8][regB:8][flags:8]`

| Tier | Opcodes | Purpose |
|------|---------|---------|
| **Upper (0x10-0x18)** | LOAD_CONST, ADD, MUL, SUB, DIV, SQRT, SIN, PULSE, LOAD_IMM | Physics & Computation |
| **Home (0x20-0x26)** | CMP_GT, CMP_EQ, JUMP, JUMP_IF, MOV, LOAD_MEM, STORE_MEM | Reasoning & Logic |
| **Lower (0x30-0x35)** | RESONATE, EMBED, BARRIER, THREAD_ID, STORE_OUT, DENSITY | Control & SDNA |

225 glyphs mapped across Egyptian Hieroglyphs, Aramaic, Mandarin, and mathematical symbols.

### Performance

| Metric | Value |
|--------|-------|
| VM throughput | 4.1M glyph-cycles/sec (CPU) |
| Compile speed | 73,565 compiles/sec |
| End-to-end | source → result in <100μs |
| Binary density | 24.7x compression vs Python |
| MBR size | 445 bytes code + 65 bytes program = 510 bytes |

### Verified Targets

| Target | Hardware | Status |
|--------|----------|--------|
| GPU (CUDA) | NVIDIA RTX 4050, 256 threads | ✅ Working |
| CPU (Python VM) | Any x86_64 | ✅ Working |
| Bare Metal (MBR) | x86 real mode, x87 FPU | ✅ Working (QEMU verified) |

---

## 🚀 GETTING STARTED

### Quick Start — Run a Genlex Program

```bash
# Clone the repository
git clone https://github.com/joshuapetersen/genlex
cd genlex

# Install requirements
pip install -r requirements.txt

# Compile and run a .glx program
python genlex_assembler.py examples/hello_resonance.glx
python genlex_runner.py examples/hello_resonance.gbin
```

### Example: hello_resonance.glx

```
# Load 42.0 into r0, multiply by SOVEREIGN_ANCHOR
𓋹 r0 42.0    # LOAD_IMM r0 42.0
𓈖 r0         # PULSE r0 (r0 *= 1.092777...)
𓂋 r0         # HALT — result: 45.8966
```

Output:
```
[GENLEX] Loaded: hello_resonance.gbin (72 bytes, 3 cycles)
[RESULT] r0 = 45.896633
```

### Compile to Bare Metal

```bash
# Assemble the MBR (requires NASM)
nasm -f bin boot/genlex_mbr.asm -o boot/genlex_mbr.bin

# Boot in QEMU
qemu-system-x86_64 -drive file=boot/genlex_mbr.bin,format=raw
```

Output on screen:
```
Booting from Hard Disk...
GLX

OK
```

That `OK` is the glyph interpreter running on bare x86 silicon — no OS, no bootloader, no runtime.

### Write Your Own Programs

See the [examples/](./examples/) directory and [GETTING_STARTED.md](./GETTING_STARTED.md).

---

## REPOSITORY STRUCTURE

```
genlex/
├── genlex_assembler.py     # .glx → .gbin compiler (225 glyphs)
├── genlex_runner.py        # Hybrid GPU/CPU virtual machine
├── genlex_benchmark.py     # Performance benchmarks
├── build_mbr.py            # MBR build automation
├── boot/
│   ├── genlex_mbr.asm      # 512-byte bare-metal interpreter
│   ├── genlex_mbr.bin      # Ready-to-boot binary image
│   └── debug_mbr.asm       # Hardware FPU diagnostic
├── examples/
│   ├── hello_resonance.glx # Basic ANCHOR multiplication
│   ├── sdna_pulse.glx      # Loop with PULSE and DENSITY
│   ├── embed_and_search.glx# Lattice embedding + search
│   └── boot_sequence.glx   # Full boot verification
├── genlex_kernel.cpp       # Native C++ physics engine
├── gs_kernel.cpp           # Volumetric linear algebra
├── genesis_bridge.cpp      # C++ ↔ Python FFI bridge
├── uefi_gsk.c              # UEFI bootloader
├── genlex_mapping.csv      # Full 225-glyph lookup table
├── hiero_translator.py     # Glyph translator
├── transpile_to_all.py     # Python → Genlex transpiler
└── genlex_terminal.py      # Interactive REPL
```

### Related Repositories

- **[cuda-oxide (Windows Port)](https://github.com/joshuapetersen/cuda-oxide)** — NVIDIA's Rust-to-GPU compiler, ported to Windows. Used by the Genlex GPU VM to compile `#[kernel]` functions to PTX.

---

*Copyright © 2025-2026 Joshua Richard Petersen.*
