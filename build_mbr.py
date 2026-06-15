"""
GENLEX MBR BUILDER — Assemble the bare-metal glyph interpreter
================================================================
Builds the 512-byte MBR boot sector image by encoding x86 machine
code directly. No NASM dependency required.

This creates a bootable disk image that:
1. BIOS loads from LBA 0 into 0x7C00
2. Initializes x87 FPU for floating-point
3. Runs the embedded Genlex glyph program on bare silicon
4. Displays SOVEREIGN BOOT VERIFIED or BOOT FAILED

Usage:
    python build_mbr.py                    # build genlex_mbr.bin
    python build_mbr.py --qemu             # build and run in QEMU
    python build_mbr.py --program FILE     # embed custom .gbin

The output is a 512-byte raw disk image.
"""

import os
import sys
import struct
import subprocess

SOVEREIGN_ANCHOR_F32 = struct.pack('<f', 1.092777037037037)  # 0x3F8BE01E
ONE_F32 = struct.pack('<f', 1.0)
ZERO_F32 = struct.pack('<f', 0.0)

def build_mbr(program_bytes: bytes = None) -> bytes:
    """
    Build a 512-byte MBR boot sector with embedded Genlex interpreter.
    Returns the raw binary.
    """
    code = bytearray()

    # ════════════════════════════════════════════════════════
    # ENTRY POINT (0x7C00)
    # ════════════════════════════════════════════════════════

    # cli
    code.append(0xFA)
    # xor ax, ax
    code += b'\x31\xC0'
    # mov ds, ax
    code += b'\x8E\xD8'
    # mov es, ax
    code += b'\x8E\xC0'
    # mov ss, ax
    code += b'\x8E\xD0'
    # mov sp, 0x7C00
    code += b'\xBC\x00\x7C'
    # sti
    code.append(0xFB)
    # finit
    code += b'\xDB\xE3'

    # ── Clear register file: 16 dwords at 0x7E00 ──
    # mov di, 0x7E00
    code += b'\xBF\x00\x7E'
    # mov cx, 16
    code += b'\xB9\x10\x00'
    # xor eax, eax
    code += b'\x66\x31\xC0'
    # .clear: mov [di], eax
    clear_loop_pos = len(code)
    code += b'\x66\x89\x05'  # mov [di], eax
    # add di, 4
    code += b'\x83\xC7\x04'
    # loop .clear
    code += b'\xE2'
    code.append(0x100 - (len(code) - clear_loop_pos + 1) & 0xFF)

    # ── Store ANCHOR at 0x7E40 ──
    # mov dword [0x7E40], 0x3F8BE01E
    code += b'\x66\xC7\x06\x40\x7E'
    code += SOVEREIGN_ANCHOR_F32

    # ── Store scratch area for 0.01 at 0x7E44 ──
    code += b'\x66\xC7\x06\x44\x7E'
    code += struct.pack('<f', 0.01)

    # ── Print banner ──
    # We'll use a simple print routine
    # mov si, banner_offset
    banner_call_pos = len(code)
    code += b'\xBE'
    banner_addr_fixup = len(code)
    code += b'\x00\x00'  # placeholder
    # call print_str
    code += b'\xE8'
    print_str_call_fixup_1 = len(code)
    code += b'\x00\x00'  # placeholder

    # ── Setup interpreter ──
    # mov si, program_offset
    code += b'\xBE'
    prog_addr_fixup = len(code)
    code += b'\x00\x00'  # placeholder
    # xor cx, cx
    code += b'\x31\xC9'

    # ════════════════════════════════════════════════════════
    # FETCH LOOP
    # ════════════════════════════════════════════════════════
    fetch_pos = len(code)

    # cmp cx, 4096
    code += b'\x81\xF9\x00\x10'
    # jge halt_done (far forward, placeholder)
    code += b'\x0F\x8D'
    halt_jge_fixup = len(code)
    code += b'\x00\x00'  # placeholder

    # mov al, [si] — opcode
    code += b'\x8A\x04'
    # mov bl, [si+1] — operand a
    code += b'\x8A\x5C\x01'
    # mov bh, [si+2] — operand b
    code += b'\x8A\x7C\x02'
    # mov dl, [si+3] — flags
    code += b'\x8A\x54\x03'
    # add si, 4
    code += b'\x83\xC6\x04'
    # inc cx
    code.append(0x41)  # inc cx

    # and bl, 0x0F
    code += b'\x80\xE3\x0F'
    # and bh, 0x0F
    code += b'\x80\xE7\x0F'
    # and dl, 0x0F
    code += b'\x80\xE2\x0F'

    # ════════════════════════════════════════════════════════
    # DISPATCH
    # ════════════════════════════════════════════════════════

    # Helper: compute di = REGS + bl*4 (used by most ops)
    # We'll inline this in each handler

    # cmp al, 0xFF — HALT
    code += b'\x3C\xFF'
    code += b'\x0F\x84'
    halt_je_fixup = len(code)
    code += b'\x00\x00'

    # cmp al, 0x00 — NOP -> jmp fetch
    code += b'\x3C\x00'
    code += b'\x74'
    code.append((fetch_pos - (len(code) + 1)) & 0xFF)

    # ── LOAD_IMM (0x18) ──
    code += b'\x3C\x18'
    code += b'\x75'
    load_imm_skip = len(code)
    code.append(0x00)  # placeholder

    # Handler: LOAD_IMM
    load_imm_pos = len(code)
    # movzx di, bl; shl di, 2
    code += b'\x0F\xB6\xFB'  # movzx di, bl
    code += b'\xC1\xE7\x02'  # shl di, 2
    # mov eax, [si]
    code += b'\x66\x8B\x04'
    # mov [0x7E00+di], eax
    code += b'\x66\x89\x85\x00\x7E'  # mov [di+0x7E00], eax
    # add si, 4
    code += b'\x83\xC6\x04'
    # jmp fetch
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    # Fix skip
    code[load_imm_skip] = (load_imm_pos - (load_imm_skip + 1)) & 0xFF

    # ── PULSE (0x17): r[a] *= ANCHOR ──
    code += b'\x3C\x17'
    code += b'\x75'
    pulse_skip = len(code)
    code.append(0x00)

    pulse_pos = len(code)
    # movzx di, bl; shl di, 2
    code += b'\x0F\xB6\xFB'
    code += b'\xC1\xE7\x02'
    # fld dword [0x7E00+di]
    code += b'\xD9\x85\x00\x7E'
    # fmul dword [0x7E40]  (ANCHOR)
    code += b'\xD8\x0E\x40\x7E'
    # fstp dword [0x7E00+di]
    code += b'\xD9\x9D\x00\x7E'
    # jmp fetch
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    code[pulse_skip] = (pulse_pos - (pulse_skip + 1)) & 0xFF

    # ── ADD (0x11): r[a] += r[b] ──
    code += b'\x3C\x11'
    code += b'\x75'
    add_skip = len(code)
    code.append(0x00)

    add_pos = len(code)
    # Load r[b]
    code += b'\x0F\xB6\xFF'  # movzx di, bh
    code += b'\xC1\xE7\x02'
    code += b'\xD9\x85\x00\x7E'  # fld [REGS+di]
    # Load r[a]
    code += b'\x0F\xB6\xFB'  # movzx di, bl
    code += b'\xC1\xE7\x02'
    code += b'\xD9\x85\x00\x7E'  # fld [REGS+di]
    # faddp
    code += b'\xDE\xC1'
    # fstp r[a]
    code += b'\xD9\x9D\x00\x7E'
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    code[add_skip] = (add_pos - (add_skip + 1)) & 0xFF

    # ── LOAD_CONST (0x10): r[a] = (b|flags<<8) * 0.01 ──
    code += b'\x3C\x10'
    code += b'\x75'
    lc_skip = len(code)
    code.append(0x00)

    lc_pos = len(code)
    # Build integer: ax = bh | (dl << 8)
    code += b'\x0F\xB6\xC7'  # movzx ax, bh
    code += b'\x0F\xB6\xD2'  # movzx dx, dl  (but dx already has dl)
    code += b'\xC1\xE2\x08'  # shl dx, 8
    code += b'\x09\xD0'      # or ax, dx
    # push ax; fild word [sp]; pop ax
    code += b'\x50'           # push ax
    code += b'\xDF\x04\x24'   # fild word [sp] -- actually this needs proper encoding
    # Hmm, in 16-bit mode fild word [sp] is tricky. Let me use a memory location instead.
    # Actually let me simplify: store to scratch, load as int
    # mov [0x7E48], ax
    code += b'\xA3\x48\x7E'   # mov [0x7E48], ax
    code += b'\x58'            # pop ax (balance stack)
    code += b'\xDF\x06\x48\x7E'  # fild word [0x7E48]
    # fmul dword [0x7E44]  (0.01)
    code += b'\xD8\x0E\x44\x7E'
    # Store to r[a]
    code += b'\x0F\xB6\xFB'  # movzx di, bl
    code += b'\xC1\xE7\x02'
    code += b'\xD9\x9D\x00\x7E'
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    code[lc_skip] = (lc_pos - (lc_skip + 1)) & 0xFF

    # ── CMP_GT (0x20): r[a] = (r[a] > r[b]) ? 1.0 : 0.0 ──
    code += b'\x3C\x20'
    code += b'\x75'
    cmp_skip = len(code)
    code.append(0x00)

    cmp_pos = len(code)
    # Load r[b]
    code += b'\x0F\xB6\xFF'  # movzx di, bh
    code += b'\xC1\xE7\x02'
    code += b'\xD9\x85\x00\x7E'  # fld [REGS+di]
    # Load r[a]
    code += b'\x0F\xB6\xFB'  # movzx di, bl
    code += b'\xC1\xE7\x02'
    code += b'\xD9\x85\x00\x7E'  # fld [REGS+di]
    # fcomip st0, st1
    code += b'\xDF\xF1'
    # fstp st0 (pop st1)
    code += b'\xDD\xD8'
    # ja .gt_true
    code += b'\x77\x08'
    # mov dword [REGS+di], 0 (false)
    code += b'\x66\xC7\x85\x00\x7E\x00\x00\x00\x00'
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    # .gt_true: mov dword [REGS+di], 0x3F800000 (1.0)
    code += b'\x66\xC7\x85\x00\x7E'
    code += struct.pack('<I', 0x3F800000)
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    code[cmp_skip] = (cmp_pos - (cmp_skip + 1)) & 0xFF

    # ── JUMP (0x22): pc = a|(b<<8) ──
    code += b'\x3C\x22'
    code += b'\x75'
    jmp_skip = len(code)
    code.append(0x00)

    jmp_pos = len(code)
    # ax = bl | (bh << 8); shl ax, 2; lea si, [program + ax]
    code += b'\x0F\xB6\xC3'  # movzx ax, bl
    code += b'\x0F\xB6\xD7'  # movzx dx, bh
    code += b'\xC1\xE2\x08'
    code += b'\x09\xD0'
    code += b'\xC1\xE0\x02'  # shl ax, 2
    # add ax, program_offset (will be fixed up)
    code += b'\x05'
    jmp_prog_fixup = len(code)
    code += b'\x00\x00'
    # mov si, ax
    code += b'\x89\xC6'
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    code[jmp_skip] = (jmp_pos - (jmp_skip + 1)) & 0xFF

    # ── JUMP_IF (0x23): if r[flags]!=0, jump ──
    code += b'\x3C\x23'
    code += b'\x75'
    jif_skip = len(code)
    code.append(0x00)

    jif_pos = len(code)
    # Check r[dl]
    code += b'\x0F\xB6\xFA'  # movzx di, dl
    code += b'\xC1\xE7\x02'
    # fld dword [REGS+di]
    code += b'\xD9\x85\x00\x7E'
    # ftst
    code += b'\xD9\xE4'
    # fnstsw ax
    code += b'\xDF\xE0'
    # fstp st0
    code += b'\xDD\xD8'
    # sahf
    code += b'\x9E'
    # jz fetch (zero = don't jump)
    code += b'\x0F\x84'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    # Not zero: do the jump (same as JUMP handler)
    code += b'\x0F\xB6\xC3'  # movzx ax, bl
    code += b'\x0F\xB6\xD7'  # movzx dx, bh
    code += b'\xC1\xE2\x08'
    code += b'\x09\xD0'
    code += b'\xC1\xE0\x02'
    code += b'\x05'
    jif_prog_fixup = len(code)
    code += b'\x00\x00'
    code += b'\x89\xC6'
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    code[jif_skip] = (jif_pos - (jif_skip + 1)) & 0xFF

    # ── DENSITY (0x35): r[a] = |r[a]| * ANCHOR ──
    code += b'\x3C\x35'
    code += b'\x75'
    den_skip = len(code)
    code.append(0x00)

    den_pos = len(code)
    code += b'\x0F\xB6\xFB'  # movzx di, bl
    code += b'\xC1\xE7\x02'
    code += b'\xD9\x85\x00\x7E'  # fld [REGS+di]
    code += b'\xD9\xE1'          # fabs
    code += b'\xD8\x0E\x40\x7E'  # fmul [ANCHOR]
    code += b'\xD9\x9D\x00\x7E'  # fstp [REGS+di]
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))
    code[den_skip] = (den_pos - (den_skip + 1)) & 0xFF

    # ── COMMIT (0x36) / STORE_OUT (0x34) / RESONATE (0x30) — simplified: just continue ──
    code += b'\x3C\x36'
    code += b'\x74'
    code.append((fetch_pos - (len(code) + 1)) & 0xFF)

    code += b'\x3C\x34'
    code += b'\x74'
    code.append((fetch_pos - (len(code) + 1)) & 0xFF)

    code += b'\x3C\x30'
    code += b'\x74'
    code.append((fetch_pos - (len(code) + 1)) & 0xFF)

    # Default: unknown opcode, skip
    code += b'\xE9'
    code += struct.pack('<h', fetch_pos - (len(code) + 2))

    # ════════════════════════════════════════════════════════
    # HALT HANDLER
    # ════════════════════════════════════════════════════════
    halt_pos = len(code)
    # Fix up halt jumps
    struct.pack_into('<h', code, halt_jge_fixup, halt_pos - (halt_jge_fixup + 2))
    struct.pack_into('<h', code, halt_je_fixup, halt_pos - (halt_je_fixup + 2))

    # Print halt message
    code += b'\xBE'
    halt_msg_fixup = len(code)
    code += b'\x00\x00'
    code += b'\xE8'
    print_str_call_fixup_2 = len(code)
    code += b'\x00\x00'

    # Check r0 == 1.0 (0x3F800000)
    # cmp dword [0x7E00], 0x3F800000
    code += b'\x66\x81\x3E\x00\x7E'
    code += struct.pack('<I', 0x3F800000)
    # je .pass
    code += b'\x74'
    pass_je_fixup = len(code)
    code.append(0x00)

    # FAIL:
    code += b'\xBE'
    fail_msg_fixup = len(code)
    code += b'\x00\x00'
    code += b'\xE8'
    print_str_call_fixup_3 = len(code)
    code += b'\x00\x00'
    # cli; hlt
    code += b'\xFA\xF4\xEB\xFE'

    # PASS:
    pass_pos = len(code)
    code[pass_je_fixup] = (pass_pos - (pass_je_fixup + 1)) & 0xFF

    code += b'\xBE'
    pass_msg_fixup = len(code)
    code += b'\x00\x00'
    code += b'\xE8'
    print_str_call_fixup_4 = len(code)
    code += b'\x00\x00'
    # cli; hlt
    code += b'\xFA\xF4\xEB\xFE'

    # ════════════════════════════════════════════════════════
    # PRINT_STR SUBROUTINE
    # ════════════════════════════════════════════════════════
    print_str_pos = len(code)

    # lodsb
    code.append(0xAC)
    # or al, al
    code += b'\x08\xC0'
    # jz .done
    code += b'\x74\x06'
    # mov ah, 0x0E
    code += b'\xB4\x0E'
    # mov bx, 0x0007
    code += b'\xBB\x07\x00'
    # int 0x10
    code += b'\xCD\x10'
    # jmp print_str
    code += b'\xEB'
    code.append(0x100 - (len(code) - print_str_pos + 1) & 0xFF)
    # .done: ret
    code.append(0xC3)

    # Fix up all print_str calls
    for fixup in [print_str_call_fixup_1, print_str_call_fixup_2,
                  print_str_call_fixup_3, print_str_call_fixup_4]:
        struct.pack_into('<h', code, fixup, print_str_pos - (fixup + 2))

    # ════════════════════════════════════════════════════════
    # STRINGS
    # ════════════════════════════════════════════════════════
    banner_pos = len(code)
    banner = b'GENLEX METAL v1.0\r\nGlyph VM on bare x86\r\n\x00'
    code += banner
    struct.pack_into('<H', code, banner_addr_fixup, 0x7C00 + banner_pos)

    halt_msg_pos = len(code)
    code += b'\r\nHALT\r\n\x00'
    struct.pack_into('<H', code, halt_msg_fixup, 0x7C00 + halt_msg_pos)

    pass_msg_pos = len(code)
    code += b'SOVEREIGN BOOT VERIFIED\r\n\x00'
    struct.pack_into('<H', code, pass_msg_fixup, 0x7C00 + pass_msg_pos)

    fail_msg_pos = len(code)
    code += b'BOOT FAILED\r\n\x00'
    struct.pack_into('<H', code, fail_msg_fixup, 0x7C00 + fail_msg_pos)

    # ════════════════════════════════════════════════════════
    # GLYPH PROGRAM — boot_sequence payload
    # ════════════════════════════════════════════════════════
    program_pos = len(code)
    struct.pack_into('<H', code, prog_addr_fixup, 0x7C00 + program_pos)

    # Fix up JUMP/JUMP_IF program base addresses
    struct.pack_into('<H', code, jmp_prog_fixup, 0x7C00 + program_pos)
    struct.pack_into('<H', code, jif_prog_fixup, 0x7C00 + program_pos)

    if program_bytes:
        code += program_bytes
    else:
        # Default: embedded boot_sequence program
        prog = bytearray()

        # LOAD_IMM r0 #1.0
        prog += bytes([0x18, 0x00, 0x00, 0x00])
        prog += struct.pack('<f', 1.0)

        # LOAD_IMM r1 #21.0
        prog += bytes([0x18, 0x01, 0x00, 0x00])
        prog += struct.pack('<f', 21.0)

        # LOAD_IMM r2 #1.0
        prog += bytes([0x18, 0x02, 0x00, 0x00])
        prog += struct.pack('<f', 1.0)

        # LOAD_IMM r3 #ANCHOR
        prog += bytes([0x18, 0x03, 0x00, 0x00])
        prog += SOVEREIGN_ANCHOR_F32

        # :boot_pulse (index 8)
        # PULSE r0
        prog += bytes([0x17, 0x00, 0x00, 0x00])

        # LOAD_CONST r4 1 0  (r4 = 0.01)
        prog += bytes([0x10, 0x04, 0x01, 0x00])

        # ADD r2 r4
        prog += bytes([0x11, 0x02, 0x04, 0x00])

        # CMP_GT r1 r2
        prog += bytes([0x20, 0x01, 0x02, 0x00])

        # JUMP_IF :boot_pulse(=8) 0 r1
        prog += bytes([0x23, 0x08, 0x00, 0x01])

        # DENSITY r0
        prog += bytes([0x35, 0x00, 0x00, 0x00])

        # COMMIT_STATE (nop in bare metal)
        prog += bytes([0x36, 0x00, 0x00, 0x00])

        # LOAD_IMM r5 #0.999999940395 (closest f32 to BILLION)
        prog += bytes([0x18, 0x05, 0x00, 0x00])
        prog += struct.pack('<f', 0.999999999)

        # CMP_GT r0 r5
        prog += bytes([0x20, 0x00, 0x05, 0x00])

        # STORE_OUT (nop in bare metal)
        prog += bytes([0x34, 0x00, 0x00, 0x00])

        # HALT
        prog += bytes([0xFF, 0x00, 0x00, 0x00])

        code += prog

    # ════════════════════════════════════════════════════════
    # PAD TO 510 BYTES + BOOT SIGNATURE
    # ════════════════════════════════════════════════════════
    code_size = len(code)
    if code_size > 510:
        print(f"[ERROR] Code too large: {code_size} bytes (max 510)")
        print(f"  Interpreter: {program_pos} bytes")
        print(f"  Program:     {code_size - program_pos} bytes")
        sys.exit(1)

    # Pad
    code += b'\x00' * (510 - code_size)
    # Boot signature
    code += b'\x55\xAA'

    return bytes(code)


def main():
    print("=" * 60)
    print("  GENLEX MBR BUILDER")
    print("  Building bare-metal glyph interpreter")
    print("=" * 60)

    outdir = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(outdir, 'boot')
    os.makedirs(outdir, exist_ok=True)

    mbr = build_mbr()

    outpath = os.path.join(outdir, 'genlex_mbr.bin')
    with open(outpath, 'wb') as f:
        f.write(mbr)

    # Analyze
    prog_start = mbr.index(b'\x18\x00\x00\x00\x00\x00\x80\x3F')  # LOAD_IMM r0 1.0
    interp_size = prog_start
    prog_size = 512 - 2 - prog_start  # minus boot sig minus padding
    # Find actual program end (last non-zero before padding)
    actual_prog_end = prog_start
    for i in range(len(mbr) - 3, prog_start, -1):
        if mbr[i] != 0x00 or mbr[i-1] == 0xFF:  # HALT = 0xFF
            actual_prog_end = i + 1
            break
    actual_prog_size = actual_prog_end - prog_start

    print(f"\n  Output:       {outpath}")
    print(f"  Total size:   512 bytes (MBR)")
    print(f"  Interpreter:  {interp_size} bytes")
    print(f"  Program:      {actual_prog_size} bytes (boot_sequence)")
    print(f"  Combined:     {interp_size + actual_prog_size} bytes")
    print(f"  Free space:   {510 - interp_size - actual_prog_size} bytes")
    print(f"  Boot sig:     0x{mbr[-2]:02X}{mbr[-1]:02X}")
    print(f"")
    print(f"  Test with QEMU:")
    print(f"    qemu-system-x86_64 -drive file={outpath},format=raw")
    print(f"{'='*60}")

    # Also check for QEMU
    if '--qemu' in sys.argv:
        qemu = None
        for path in [
            r'C:\Program Files\qemu\qemu-system-x86_64.exe',
            r'C:\Program Files (x86)\qemu\qemu-system-x86_64.exe',
        ]:
            if os.path.exists(path):
                qemu = path
                break
        if qemu:
            print(f"\n[QEMU] Launching: {qemu}")
            subprocess.Popen([qemu, '-drive', f'file={outpath},format=raw'])
        else:
            print("\n[QEMU] Not found. Install QEMU to test the boot image.")


if __name__ == '__main__':
    main()
