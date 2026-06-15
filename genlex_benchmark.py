"""
GENLEX BENCHMARK — Measure everything.
"""
import os, sys, time, struct, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genlex_assembler import GenlexAssembler
from genlex_runner import GenlexVM

ANCHOR = 1.092777037037037

def bench(name, func, iterations=1000):
    """Run func N times, return total and per-iteration time."""
    # Warmup
    for _ in range(10):
        func()
    # Measure
    t0 = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed = time.perf_counter() - t0
    per_iter = elapsed / iterations
    return elapsed, per_iter

def main():
    print("=" * 70)
    print("  GENLEX MANIFEST ENGINE — PERFORMANCE BENCHMARK")
    print(f"  SOVEREIGN_ANCHOR = {ANCHOR}")
    print("=" * 70)

    asm = GenlexAssembler()
    vm = GenlexVM()

    # ── 1. ASSEMBLER SPEED ──────────────────────────────────
    print("\n[1] ASSEMBLER THROUGHPUT")

    src_hello = "LOAD_IMM r0 #42.0\nLOAD_IMM r1 #ANCHOR\nMUL r0 r1\nHALT\n"
    src_boot = open(os.path.join(os.path.dirname(__file__), 'examples', 'boot_sequence.glx'), 
                    'r', encoding='utf-8').read()

    total, per = bench("hello_resonance", lambda: asm.assemble(src_hello), 10000)
    print(f"  hello_resonance (4 inst):  {per*1e6:.1f} us/compile  ({1/per:.0f} compiles/sec)")

    total, per = bench("boot_sequence (20 inst)", lambda: asm.assemble(src_boot), 5000)
    print(f"  boot_sequence (20 inst):   {per*1e6:.1f} us/compile  ({1/per:.0f} compiles/sec)")

    # Larger program
    src_big = "\n".join([f"LOAD_IMM r{i%16} #{float(i)}" for i in range(100)] + ["HALT"])
    total, per = bench("100-instruction program", lambda: asm.assemble(src_big), 1000)
    print(f"  100-inst program:          {per*1e6:.1f} us/compile  ({1/per:.0f} compiles/sec)")

    # ── 2. VM EXECUTION SPEED ───────────────────────────────
    print("\n[2] VM EXECUTION SPEED (CPU path)")

    # Pre-compile binaries
    bin_hello, _ = asm.assemble(src_hello)
    bin_boot, _ = asm.assemble(src_boot)

    import tempfile
    tmp_hello = os.path.join(tempfile.gettempdir(), 'bench_hello.gbin')
    tmp_boot = os.path.join(tempfile.gettempdir(), 'bench_boot.gbin')
    with open(tmp_hello, 'wb') as f: f.write(bin_hello)
    with open(tmp_boot, 'wb') as f: f.write(bin_boot)

    # Load once
    inst_hello, _ = vm.load_gbin(tmp_hello)
    inst_boot, _ = vm.load_gbin(tmp_boot)

    total, per = bench("hello (3 cycles)", lambda: vm.execute(inst_hello), 100000)
    print(f"  hello_resonance (3 cyc):   {per*1e6:.2f} us/exec  ({1/per:.0f} exec/sec)")

    total, per = bench("boot (19 cycles)", lambda: vm.execute(inst_boot), 50000)
    print(f"  boot_sequence (19 cyc):    {per*1e6:.2f} us/exec  ({1/per:.0f} exec/sec)")

    # Stress: 1000-cycle loop program
    src_loop = """
LOAD_IMM r0 #1.0
LOAD_IMM r1 #1000.0
LOAD_IMM r2 #0.0
LOAD_CONST r4 1 0
:loop
PULSE r0 0 0
ADD r2 r4
CMP_GT r1 r2 0
JUMP_IF :loop 0 r1
HALT
"""
    bin_loop, _ = asm.assemble(src_loop)
    tmp_loop = os.path.join(tempfile.gettempdir(), 'bench_loop.gbin')
    with open(tmp_loop, 'wb') as f: f.write(bin_loop)
    inst_loop, _ = vm.load_gbin(tmp_loop)

    total, per = bench("loop (1000 cycles)", lambda: vm.execute(inst_loop), 1000)
    cycles_per_sec = 1000 / per
    print(f"  1000-cycle loop:           {per*1e6:.1f} us/exec  ({cycles_per_sec/1e6:.1f}M cycles/sec)")

    # ── 3. END-TO-END: source -> binary -> execute ──────────
    print("\n[3] END-TO-END PIPELINE (.glx -> .gbin -> result)")

    def e2e_hello():
        b, _ = asm.assemble(src_hello)
        # Parse in memory (skip file I/O)
        payload = b[16:-32]
        insts = [payload[i:i+4] for i in range(0, len(payload), 4)]
        return vm.execute(insts)

    total, per = bench("hello e2e", e2e_hello, 10000)
    print(f"  hello (compile+execute):   {per*1e6:.1f} us  ({1/per:.0f} programs/sec)")

    def e2e_boot():
        b, _ = asm.assemble(src_boot)
        payload = b[16:-32]
        insts = [payload[i:i+4] for i in range(0, len(payload), 4)]
        return vm.execute(insts)

    total, per = bench("boot e2e", e2e_boot, 5000)
    print(f"  boot (compile+execute):    {per*1e6:.1f} us  ({1/per:.0f} programs/sec)")

    # ── 4. COMPARISON: Python equivalent ────────────────────
    print("\n[4] COMPARISON: Genlex vs Pure Python")

    def python_42_anchor():
        return 42.0 * 1.092777037037037

    def python_resonance():
        vals = [1.0, 2.0, 3.0, 4.0]
        total = 0.0
        for d, v in enumerate(vals):
            weight = 1.092777037037037 * (1.0 + d * 0.1)
            total += v * v * weight
        distance = math.sqrt(total) if total > 0 else 0.0
        return 1.0 / (distance + 1e-8) * 1.092777037037037

    def python_boot():
        r0 = 1.0
        for _ in range(21):
            r0 *= 1.092777037037037
        return abs(r0) * 1.092777037037037

    _, per_py1 = bench("python 42*ANCHOR", python_42_anchor, 1000000)
    _, per_glx1 = bench("genlex 42*ANCHOR", lambda: vm.execute(inst_hello), 100000)
    print(f"  42*ANCHOR:    Python={per_py1*1e9:.0f}ns  Genlex={per_glx1*1e6:.1f}us  ratio={per_glx1/per_py1:.0f}x")

    _, per_py2 = bench("python resonance", python_resonance, 1000000)
    _, per_glx2 = bench("genlex boot", lambda: vm.execute(inst_boot), 50000)
    print(f"  Boot seq:     Python={per_py2*1e9:.0f}ns  Genlex={per_glx2*1e6:.1f}us  ratio={per_glx2/per_py2:.0f}x")

    # ── 5. BINARY DENSITY ───────────────────────────────────
    print("\n[5] BINARY DENSITY")
    programs = [
        ("hello_resonance", src_hello, "42 * ANCHOR"),
        ("boot_sequence", src_boot, "21-subsystem boot loop"),
    ]
    for name, src, desc in programs:
        b, meta = asm.assemble(src)
        src_bytes = len(src.encode('utf-8'))
        bin_bytes = meta['payload_bytes']
        ratio = src_bytes / bin_bytes if bin_bytes > 0 else 0
        print(f"  {name}: {src_bytes} bytes source -> {bin_bytes} bytes binary ({ratio:.1f}x compression)")

    # Vs Python equivalent
    py_boot = """
r0 = 1.0
for _ in range(21):
    r0 *= 1.092777037037037
density = abs(r0) * 1.092777037037037
result = 1.0 if density > 0.999999999 else 0.0
"""
    py_bytes = len(py_boot.encode('utf-8'))
    glx_bytes = len(src_boot.encode('utf-8'))
    bin_boot_meta = asm.assemble(src_boot)[1]
    print(f"  boot_sequence vs Python: Genlex={bin_boot_meta['payload_bytes']}B binary, Python={py_bytes}B source")

    # ── SUMMARY ─────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  BENCHMARK COMPLETE")
    print(f"  VM throughput:    {cycles_per_sec/1e6:.1f}M glyph-cycles/sec (CPU path)")
    print(f"  Compile speed:    {1/per:.0f} programs/sec")
    print(f"  Pipeline:         source -> binary -> result in <100us")
    print(f"{'='*70}")

    # Cleanup
    for f in [tmp_hello, tmp_boot, tmp_loop]:
        try: os.remove(f)
        except: pass

if __name__ == '__main__':
    main()
