import sys
import os

# Add the build directory to the path so we can import the new module
sys.path.append(os.path.abspath("./build/Release"))

try:
    import genesis_bridge
    print("[SUCCESS] Genesis Bridge imported.")
    
    # Initialize the core
    core = genesis_bridge.GenesisCore("Sovereign_Node_01")
    print(f"[ Genesis ] {core.handshake()}")
    
    # Test SDNA density calculation
    input_val = 1.0
    density = core.calculate_density(input_val)
    print(f"[ SDNA    ] Input: {input_val} -> Calculated Density: {density}")
    
    if abs(density - 0.999999999) < 1e-12:
        print("[ VERIFY  ] SDNA Billion Barrier Logic: PASS")
    else:
        print("[ VERIFY  ] SDNA Billion Barrier Logic: FAIL")

except ImportError as e:
    print(f"[ ERROR   ] Could not import genesis_bridge: {e}")
except Exception as e:
    print(f"[ ERROR   ] An error occurred: {e}")
