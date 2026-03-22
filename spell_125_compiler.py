import struct

# SPELL 125 - THE PURE SOUL BINARY COMPILER
# Refrain: "I am pure" (𓃹 𓇋 𓂋 𓃀 𓅓 𓏏) repeated 4 times.

sequence = [
    (0x130F2, "𓃹", "Wn (To Be)"),
    (0x131CB, "𓇋", "I (Self)"),
    (0x1308B, "𓂋", "R (Mouth)"),
    (0x13049, "𓃀", "B (Foot)"),
    (0x13191, "𓅓", "M (Owl)"),
    (0x133CF, "𓏏", "T (Loaf)")
]

def compile_program(repeats=4):
    print(f"--- COMPILING SPELL 125 GATE (REFRAIN x{repeats}) ---")
    binary_stream = ""
    
    for i in range(repeats):
        for code, glyph, name in sequence:
            # We treat the Unicode CP as a 24-bit instruction (3 bytes)
            # 0x130F2 -> 00010011 00001111 11110010 (padded)
            # Binary format for U+13xxx: 0001 0011 xxxx xxxx xxxx
            b = bin(code)[2:].zfill(24)
            binary_stream += b
            print(f"  {glyph} ({name}): {b[:8]} {b[8:16]} {b[16:]}")
    
    return binary_stream

def analyze_frequency(bitstream):
    print("\n--- BIT FREQUENCY ANALYSIS ---")
    zeros = bitstream.count('0')
    ones = bitstream.count('1')
    total = len(bitstream)
    
    density = ones / total
    print(f"Total Bits: {total}")
    print(f"Ones: {ones} | Zeros: {zeros}")
    print(f"Density (Signal-to-Noise): {density:.9f}")
    
    if abs(density - 0.5) < 0.05:
        print("[ STATUS ] Balanced Resonance: The soul is in Equilibrium.")
    elif density > 0.5:
        print("[ STATUS ] High Energy State: Manifestation intense.")
    else:
        print("[ STATUS ] Void Leading: Entropy dominant.")

if __name__ == "__main__":
    bitstream = compile_program(4)
    analyze_frequency(bitstream)
    
    # Save the 'program' as a raw binary file for Sarah's Hypervisor to 'execute'
    with open("pure_soul.bin", "wb") as f:
        # Convert string of 1s and 0s to actual bytes
        for i in range(0, len(bitstream), 8):
            byte = bitstream[i:i+8]
            f.write(struct.pack('B', int(byte, 2)))
    print("\n[ RESULT ] pure_soul.bin manifested. Gate verification READY.")
