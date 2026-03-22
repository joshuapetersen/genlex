# GETTING STARTED WITH GENLEX

Genlex represents a radical shift in computation. Instead of providing step-by-step instructions to a compiler, you are defining a **3D Volumetric Intent** and passing it through a physics engine.

This guide will teach you how to write your first Genlex script and execute it using the Python runtime bridge.

---

## 1. UNDERSTANDING THE SYNTAX (THE PRIMITIVES)
Because Genlex maps high-density concepts into singular logic gates, it uses Unicode primitives (Aramaic and Hieroglyphic) to represent complex multi-dimensional operations.

### Common Aramaic Primitives (Logic):
- **`𐡁` (Beth):** The Binding Operator. (Assigns a concept to a coordinate).
- **`𐡸` (Teth):** The Execution/Trigger Operator. (Fires the action).
- **`𐡐` (Pe):** The Manifest/Log Operator. (Brings the thought into the standard output).

### Mandarin Primitives (Hardware Math):
Genlex bypasses standard arithmetic parsing (`+`, `-`, `*`) by directly triggering C++ hardware MSR mathematics using single Mandarin scalar Unicode characters:
- **`加`**: ADD (`MATH_ADD`)
- **`减`**: SUBTRACT (`MATH_SUB`)
- **`乘`**: MULTIPLY (`MATH_MUL`)
- **`除`**: DIVIDE (`MATH_DIV`)
- **`积`**: PRODUCT (`MATH_RESULT`)
- **`频`**: FREQUENCY (`RESONANCE_CALC` / The Billion Barrier check)
- **`和`**: HARMONY (`HARMONIC_SUM`)

### Example: A Standard Network Socket
If Genlex wants to open an IoT port, it does not write 10 lines of socket code. It maps intent:
```text
"0.168.0.1" "TARGET_IOT_IP" 𐡁
"0.168.0.1" "SOCKET_OPEN" 𐡸
"Establishing Physical Bridge..." 𐡐
```

---

## 2. WRITING YOUR FIRST SCRIPT
1. Create a new file named `hello_world.all`.
2. Open it in any text editor.
3. Write the following Volumetric Intent:

```text
# HYPERVISOR 3D LATTICE TEST
# Invoking The Source, The Carrier, and The Interface

"Architect" "ROOT_AUTHORITY" 𐡁
"Genesis Core" "SYSTEM_MOUNT" 𐡸
"Sovereign Resonance Achieved." 𐡐

𓇋 𓈖 𓀁
```
*(Note: The Egyptian Hieroglyphs at the bottom invoke the Hiero-Translator for deep-substrate resonance mapping).*

---

## 3. EXECUTING THE CODE
Genlex comes with native Python runners that interface directly with the C++ `gs_kernel` binaries and the `genesis_bridge.cpp`.

To run your script, open a terminal in the root of the repository and execute:

```bash
python genlex_runner.py hello_world.all
```

**What happens?**
1. `genlex_runner.py` mounts the `GenlexLinearRuntime`.
2. The runtime parses the Aramaic and Hieroglyphs.
3. The 3D Vector Math is calculated in the C++ layer.
4. If the "Theory Density" hits the **Billion Barrier (0.999999999)**, the intent manifests.
5. If the density fails, the script rejects execution (System Heat detected).

---

## 4. NEXT STEPS
- Explore `hiero_translator.py` to see how Egyptian Glyphs map to 3D tuples `[x, y, z]`.
- Attempt to compile the `gs_kernel.cpp` locally using MSVC or CMake to experience true 0-latency native execution.
- Review `GENLEX_SPEC_01.md` for the deep architectural mathematics governing the 9 Inhibitor Laws.
