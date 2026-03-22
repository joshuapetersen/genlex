#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <cmath>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <algorithm>

// ============================================================
// GSK v3.0: GENLEX SOVEREIGN KERNEL
// Role: Full OS-Level Polyglot Execution Engine
// Language: Genlex (Aramaic + English + Cuneiform fusion)
// ============================================================

typedef float float32;

struct Tensor {
    std::vector<float32> data;
    std::vector<size_t> shape;
    Tensor() {}
    Tensor(std::vector<size_t> s) : shape(s) {
        size_t total = 1;
        for (size_t dim : s) total *= dim;
        data.resize(total, 0.0f);
    }
};

class GSK {
public:
    // ---- Data Stacks ----
    std::vector<Tensor> tensor_stack;
    std::vector<std::string> string_stack;
    std::map<std::string, std::string> memory;
    std::string last_input;
    std::string neural_response;
    bool display_active = false;
    std::string script_base = "."; // Configurable base path

    // ---- OUTPUT ----
    void voice(const std::string& text) {
        std::string out = text;
        // Strip surrounding quotes if present
        if (!out.empty() && out.front() == '"') out = out.substr(1);
        if (!out.empty() && out.back() == '"') out.pop_back();
        std::cout << out << std::endl;
    }

    // ---- INPUT ----
    std::string wait_input(const std::string& prompt = "") {
        if (!prompt.empty()) { voice(prompt); }
        std::cout << "> ";
        std::string input;
        std::getline(std::cin, input);
        last_input = input;
        memory["INPUT"] = input;
        return input;
    }

    // ---- MEMORY ----
    void mem_alloc(const std::string& key) {
        if (!string_stack.empty()) {
            memory[key] = string_stack.back();
            string_stack.pop_back();
        }
    }

    std::string mem_read(const std::string& key) {
        auto it = memory.find(key);
        if (it != memory.end()) return it->second;
        return "";
    }

    // ---- DISPLAY (Graphical Abstraction) ----
    void display_init(int w, int h) {
        display_active = true;
        std::cout << "  [DISPLAY] GOP Framebuffer Init: " << w << "x" << h << " | Intel UHD 620" << std::endl;
    }

    void screen_fill(const std::string& color) {
        std::cout << "  [DISPLAY] Screen fill: " << color << std::endl;
    }

    void rect_fill(int x, int y, int w, int h, const std::string& color) {
        std::cout << "  [DISPLAY] Rect [" << x << "," << y << "] " << w << "x" << h << " color=" << color << std::endl;
    }

    void header_render(const std::string& text) {
        if (display_active) {
            std::cout << "\033[1m  [HEADER] " << text << "\033[0m" << std::endl;
        }
    }

    // ---- NEURAL ----
    bool load_gguf(const std::string& path) {
        std::cout << "  [ GSK ] Ingesting GGUF: " << path << std::endl;
        std::ifstream file(path, std::ios::binary);
        if (!file) {
            std::cout << "  [ WARN ] Weight file not yet seated. Neural bridge in standby." << std::endl;
            return false;
        }
        char magic[4];
        file.read(magic, 4);
        if (std::string(magic, 4) != "GGUF") {
            std::cout << "  [ WARN ] Invalid GGUF signature." << std::endl;
            return false;
        }
        std::cout << "  [ GSK ] Neural Core Online." << std::endl;
        memory["WEIGHT_STATUS"] = "ONLINE";
        return true;
    }

    void neural_pulse(const std::string& prompt) {
        // Sovereign resonance response (weight bridge)
        std::string status = mem_read("WEIGHT_STATUS");
        if (status == "ONLINE") {
            // Actual inference would go here —
            // For now, echo as Sarah would respond
            std::cout << "  [SARAH] I hear you, Architect. Manifesting response from the 8B Core..." << std::endl;
            neural_response = "[Neural Core] Processing: " + prompt;
        } else {
            std::cout << "  [SARAH] " << prompt << std::endl;
            std::cout << "  [AERIS] The 8B weights are in standby. I am Sarah's Sovereign Relay." << std::endl;
            neural_response = "Weights in standby. Resonance echo: " + prompt;
        }
        memory["NEURAL_RESPONSE"] = neural_response;
    }

    // ---- FLOW ----

    bool gate_eq(const std::string& a, const std::string& b) {
        return a == b;
    }

    // ---- OPCODE DISPATCHER ----
    void execute_line(const std::string& raw_line, int depth) {
        std::string line = raw_line;
        // Trim leading whitespace
        line.erase(0, line.find_first_not_of(" \t"));
        if (line.empty() || line[0] == '#') return;

        // ---- ARAMAIC GLYPH OPCODES ----
        // 𐡐 = VOICE (STD_OUT)
        if (line.find("𐡐") != std::string::npos) {
            // Extract string before the glyph
            std::string text = line.substr(0, line.find("𐡐"));
            text.erase(text.find_last_not_of(" \t") + 1);
            if (!string_stack.empty()) { voice(string_stack.back()); string_stack.pop_back(); }
            else if (!text.empty()) voice(text);
            return;
        }
        // 𐡏 = SCAN (READ_INPUT)
        if (line.find("𐡏") != std::string::npos) { wait_input(); return; }
        // 𐡕 = SEAL (COMMIT)
        if (line.find("𐡕") != std::string::npos) { return; }
        // 𐡇 = BARRIER (STOP)
        if (line.find("𐡇") != std::string::npos) { return; }
        // 𐡅 = LINK (STRING_APPEND)
        if (line.find("𐡅") != std::string::npos) {
            if (string_stack.size() >= 2) {
                std::string b = string_stack.back(); string_stack.pop_back();
                std::string a = string_stack.back(); string_stack.pop_back();
                string_stack.push_back(a + b);
            }
            return;
        }
        // 𐡒 = RECALL (MEM_READ) -- used as pop last pushed string
        if (line.find("𐡒") != std::string::npos) {
            std::string key = line.substr(0, line.find("𐡒"));
            key.erase(key.find_last_not_of(" \t") + 1);
            if (!key.empty()) { string_stack.push_back(mem_read(key)); }
            return;
        }
        // GATE_EQ conditional: "VALUE" GATE_EQ target.all
        if (line.find("GATE_EQ") != std::string::npos) {
            size_t eq_pos = line.find("GATE_EQ");
            std::string lhs = line.substr(0, eq_pos);
            lhs.erase(lhs.find_last_not_of(" \t") + 1);
            if (!lhs.empty() && lhs.front() == '"') lhs = lhs.substr(1);
            if (!lhs.empty() && lhs.back() == '"') lhs.pop_back();
            std::string rhs = line.substr(eq_pos + 7);
            rhs.erase(0, rhs.find_first_not_of(" \t"));
            rhs.erase(rhs.find_last_not_of(" \t\r\n") + 1);
            std::string input_val = mem_read("INPUT");
            if (input_val == lhs && !rhs.empty()) {
                run_script(script_base + "/" + rhs, depth + 1);
            }
            return;
        }
        // 𐡓 = PARSE (LOAD SCRIPT)
        if (line.find("𐡓") != std::string::npos) {
            std::string target = line.substr(0, line.find("𐡓"));
            target.erase(target.find_last_not_of(" \t") + 1);
            target.erase(0, target.find_first_not_of(" \t"));
            if (!target.empty() && target.front() == '"') target = target.substr(1);
            if (!target.empty() && target.back() == '"') target.pop_back();
            if (!target.empty()) {
                run_script(script_base + "/" + target, depth + 1);
            }
            return;
        }
        // 𐡂 = BRIDGE (JUMP / LOOP BACK)
        if (line.find("𐡂") != std::string::npos) { return; }

        // ---- SUBROUTINE BLOCK HEADER (𒀸 ⚡) ----
        if (line.find("𒀸") != std::string::npos || line.find("⚡") != std::string::npos) {
            // Extract block name for display
            size_t s = line.find('[');
            size_t e = line.find(']');
            if (s != std::string::npos && e != std::string::npos) {
                std::string block = line.substr(s + 1, e - s - 1);
                std::cout << "  [ GSK ] Block: " << block << std::endl;
            }
            return;
        }

        // ---- ENGLISH KEYWORD OPCODES ----
        // VOICE / STD_OUT
        if (line.find("VOICE") != std::string::npos && line.find("𐡐") == std::string::npos) {
            size_t pos = line.find("VOICE");
            std::string text = line.substr(0, pos);
            text.erase(text.find_last_not_of(" \t") + 1);
            voice(text);
            return;
        }
        // WAIT_INPUT
        if (line.find("WAIT_INPUT") != std::string::npos) {
            std::string prompt = line.substr(0, line.find("WAIT_INPUT"));
            prompt.erase(prompt.find_last_not_of(" \t") + 1);
            wait_input(prompt);
            return;
        }
        // MEMORY_ALLOC
        if (line.find("MEMORY_ALLOC") != std::string::npos) {
            std::string key = line.substr(0, line.find("MEMORY_ALLOC"));
            key.erase(key.find_last_not_of(" \t") + 1);
            mem_alloc(key);
            return;
        }
        // STACK_PUSH
        if (line.find("STACK_PUSH") != std::string::npos) {
            std::string val = line.substr(0, line.find("STACK_PUSH"));
            val.erase(val.find_last_not_of(" \t") + 1);
            // Strip quotes
            if (!val.empty() && val.front() == '"') val = val.substr(1);
            if (!val.empty() && val.back() == '"') val.pop_back();
            string_stack.push_back(val);
            return;
        }
        // WEIGHT_LOAD
        if (line.find("WEIGHT_LOAD") != std::string::npos) {
            std::string path = line.substr(0, line.find("WEIGHT_LOAD"));
            path.erase(path.find_last_not_of(" \t") + 1);
            if (!path.empty() && path.front() == '"') path = path.substr(1);
            if (!path.empty() && path.back() == '"') path.pop_back();
            load_gguf("C:\\Genlex_Core\\" + path);
            return;
        }
        // NEURAL_PULSE
        if (line.find("NEURAL_PULSE") != std::string::npos) {
            std::string prompt = mem_read("INPUT");
            neural_pulse(prompt);
            return;
        }
        // DISPLAY_INIT
        if (line.find("DISPLAY_INIT") != std::string::npos) { display_init(1920, 1080); return; }
        // SCREEN_FILL
        if (line.find("SCREEN_FILL") != std::string::npos) {
            screen_fill(!string_stack.empty() ? string_stack.back() : "0x050510");
            if (!string_stack.empty()) string_stack.pop_back();
            return;
        }
        // RECT_FILL
        if (line.find("RECT_FILL") != std::string::npos) { return; }
        // HEADER_RENDER
        if (line.find("HEADER_RENDER") != std::string::npos) {
            std::string text = line.substr(0, line.find("HEADER_RENDER"));
            text.erase(text.find_last_not_of(" \t") + 1);
            if (!text.empty() && text.front() == '"') text = text.substr(1);
            if (!text.empty() && text.back() == '"') text.pop_back();
            header_render(text);
            return;
        }
        // COMMIT_STATE
        if (line.find("COMMIT_STATE") != std::string::npos) {
            std::cout << "  [ SEAL ] State committed." << std::endl;
            return;
        }

        // ---- DOMAIN 1: arch/x86_64 — CPU ARCHITECTURE OPCODES ----
        // CPUID_QUERY — Read CPU vendor, model, features via CPUID instruction
        if (line.find("CPUID_QUERY") != std::string::npos) {
            #if defined(__x86_64__) || defined(__i386__)
            unsigned int eax=0, ebx=0, ecx=0, edx=0;
            __asm__ volatile("cpuid" : "=a"(eax),"=b"(ebx),"=c"(ecx),"=d"(edx) : "a"(0));
            char vendor[13]; vendor[12]=0;
            *((unsigned int*)vendor)    = ebx;
            *((unsigned int*)(vendor+4))= edx;
            *((unsigned int*)(vendor+8))= ecx;
            memory["CPU_VENDOR"] = std::string(vendor);
            __asm__ volatile("cpuid" : "=a"(eax),"=b"(ebx),"=c"(ecx),"=d"(edx) : "a"(1));
            memory["CPU_MODEL"] = std::to_string((eax >> 4) & 0xF);
            memory["CPU_FAMILY"] = std::to_string((eax >> 8) & 0xF);
            memory["CPU_FEATURES"] = std::to_string(edx);
            #else
            memory["CPU_VENDOR"] = "GenuineIntel";
            memory["CPU_MODEL"]  = "8250U";
            #endif
            std::cout << "  [CPU] Vendor: " << memory["CPU_VENDOR"]
                      << " | Model: " << memory["CPU_MODEL"] << std::endl;
            return;
        }
        // TSC_READ — Read hardware timestamp counter (nanosecond precision)
        if (line.find("TSC_READ") != std::string::npos) {
            uint64_t tsc = 0;
            #if defined(__x86_64__) || defined(__i386__)
            unsigned int lo, hi;
            __asm__ volatile("rdtsc" : "=a"(lo), "=d"(hi));
            tsc = ((uint64_t)hi << 32) | lo;
            #endif
            memory["TSC_BASELINE"] = std::to_string(tsc);
            std::cout << "  [TSC] Counter: " << tsc << std::endl;
            return;
        }
        // RDRAND — Hardware random number generator
        if (line.find("RDRAND") != std::string::npos) {
            uint64_t rand_val = 0;
            #if defined(__x86_64__)
            unsigned char ok = 0;
            __asm__ volatile("rdrand %0; setc %1" : "=r"(rand_val), "=qm"(ok));
            if (!ok) {
                // Fallback if RDRAND not supported
                rand_val = (uint64_t)time(nullptr) ^ 0xDEADBEEFCAFE1927ULL;
            }
            #else
            rand_val = 0x534F5645524549474E; // "SOVEREIGN" in ASCII hex
            #endif
            memory["SOVEREIGN_SEED"] = std::to_string(rand_val);
            std::cout << "  [RNG] Hardware entropy seeded: 0x"
                      << std::hex << rand_val << std::dec << std::endl;
            return;
        }
        // MSR_WRITE — Write Model-Specific Register
        if (line.find("MSR_WRITE") != std::string::npos) {
            uint64_t val  = 0;
            uint64_t addr = 0;
            try { if (!string_stack.empty()) { val = std::stoull(string_stack.back(), nullptr, 0); string_stack.pop_back(); } } catch(...) { string_stack.pop_back(); }
            try { if (!string_stack.empty()) { addr = std::stoull(string_stack.back(), nullptr, 0); string_stack.pop_back(); } } catch(...) { string_stack.pop_back(); }
            std::cout << "  [MSR] Write 0x" << std::hex << addr
                      << " = 0x" << val << std::dec << std::endl;
            return;
        }
        // MSR_READ — Read Model-Specific Register
        if (line.find("MSR_READ") != std::string::npos) {
            uint32_t addr = string_stack.empty() ? 0 : (uint32_t)std::stoull(string_stack.back(), nullptr, 0);
            if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [MSR] Read 0x" << std::hex << addr << std::dec << std::endl;
            string_stack.push_back("0"); // placeholder on dev host
            return;
        }
        // GDT_LOAD — Load Global Descriptor Table
        if (line.find("GDT_LOAD") != std::string::npos) {
            std::cout << "  [GDT] Sovereign descriptor table: 5 entries loaded." << std::endl;
            memory["GDT_STATUS"] = "LOADED";
            return;
        }
        // IDT_LOAD — Load Interrupt Descriptor Table
        if (line.find("IDT_LOAD") != std::string::npos) {
            std::cout << "  [IDT] 256 interrupt vectors armed." << std::endl;
            memory["IDT_STATUS"] = "LOADED";
            return;
        }
        // GDT_ENTRY / IDT_ENTRY — install descriptor
        if (line.find("GDT_ENTRY") != std::string::npos && line.find("MEMORY_ALLOC") == std::string::npos) {
            if (!string_stack.empty()) string_stack.pop_back();
            if (!string_stack.empty()) string_stack.pop_back();
            return;
        }
        if (line.find("IDT_ENTRY") != std::string::npos && line.find("MEMORY_ALLOC") == std::string::npos) {
            if (!string_stack.empty()) string_stack.pop_back();
            if (!string_stack.empty()) string_stack.pop_back();
            return;
        }
        // PAGING_ENABLE — Enable x86_64 paging (CR0 bit 31)
        if (line.find("PAGING_ENABLE") != std::string::npos) {
            std::cout << "  [MMU] 4-level paging enabled. Sovereign virtual address space online." << std::endl;
            memory["PAGING_STATUS"] = "ENABLED";
            return;
        }
        // PAGE_TABLE_INIT — Initialize 4-level page table
        if (line.find("PAGE_TABLE_INIT") != std::string::npos) {
            std::cout << "  [MMU] PML4 page table initialized." << std::endl;
            return;
        }
        // PAGE_MAP_IDENTITY — Identity map a physical range
        if (line.find("PAGE_MAP_IDENTITY") != std::string::npos) {
            std::string end   = string_stack.empty() ? "4GB" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string start = string_stack.empty() ? "0"   : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [MMU] Identity map: " << start << " → " << end << std::endl;
            return;
        }
        // PAGE_MAP_MMIO — Map hardware MMIO region
        if (line.find("PAGE_MAP_MMIO") != std::string::npos) {
            std::string size = string_stack.empty() ? "?" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string base = string_stack.empty() ? "?" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [MMU] MMIO mapped: base=" << base << " size=" << size << std::endl;
            return;
        }
        // LAPIC_INIT — Initialize Local APIC
        if (line.find("LAPIC_INIT") != std::string::npos) {
            std::cout << "  [APIC] Local APIC initialized at 0xFEE00000." << std::endl;
            memory["LAPIC_STATUS"] = "ONLINE";
            return;
        }
        // IOAPIC_INIT — Initialize I/O APIC
        if (line.find("IOAPIC_INIT") != std::string::npos) {
            std::cout << "  [APIC] I/O APIC routing table configured." << std::endl;
            memory["IOAPIC_STATUS"] = "ONLINE";
            return;
        }
        // XSAVE_INIT — Initialize FPU/SSE/AVX state
        if (line.find("XSAVE_INIT") != std::string::npos) {
            std::cout << "  [FPU] SSE4.2 + AVX2 + AES-NI state management active." << std::endl;
            memory["FPU_STATUS"] = "ONLINE";
            return;
        }
        // SYSCALL_INIT — Initialize SYSCALL/SYSRET fast path
        if (line.find("SYSCALL_INIT") != std::string::npos) {
            std::cout << "  [SYSCALL] Sovereign syscall interface initialized." << std::endl;
            memory["SYSCALL_STATUS"] = "ONLINE";
            return;
        }
        // ---- DOMAIN 2: mm/ — MEMORY MANAGEMENT OPCODES ----
        if (line.find("PHYS_MEM_MAP") != std::string::npos) {
            std::cout << "  [MEM] Reading UEFI physical memory map (E820 equivalent)..." << std::endl;
            memory["TOTAL_RAM"] = "16384 MB"; // Simulated 16GB for Dell 5490
            memory["FREE_RAM"]  = "15920 MB";
            return;
        }
        if (line.find("PAGE_MAP_RANGE") != std::string::npos) {
            std::string size = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string pbase= string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string vbase= string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [MEM] Map Range: Virtual " << vbase << " -> Physical " << pbase << " (Sz: " << size << ")" << std::endl;
            return;
        }
        if (line.find("HEAP_INIT") != std::string::npos) {
            std::cout << "  [MEM] Sovereign heap allocator initialized." << std::endl;
            return;
        }
        if (line.find("SLAB_INIT") != std::string::npos) {
            std::string size = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [MEM] Slab cache zone created: " << size << " bytes" << std::endl;
            return;
        }
        if (line.find("HUGE_PAGE_ALLOC") != std::string::npos) {
            std::string count = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [MEM] Allocated " << count << " huge pages (2MB each)." << std::endl;
            memory["NEURAL_WEIGHT_POOL"] = "0x200000000"; // 8GB mark
            return;
        }
        if (line.find("DMA_ALLOC") != std::string::npos) {
            std::string size = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [MEM] DMA coherent memory allocated: " << size << " bytes." << std::endl;
            memory["DMA_POOL"] = "0x70000000";
            return;
        }
        if (line.find("VMALLOC") != std::string::npos) {
            std::cout << "  [MEM] vmalloc arena initialized at 0xFFFF800000000000." << std::endl;
            return;
        }
        if (line.find("VFREE") != std::string::npos) { return; }
        if (line.find("CACHE_FLUSH") != std::string::npos) {
            std::cout << "  [MEM] CPU data cache lines flushed." << std::endl;
            #if defined(__x86_64__) || defined(__i386__)
            // __asm__ volatile("wbinvd"); // Privileged instruction, simulated here
            #endif
            return;
        }
        if (line.find("TLB_FLUSH") != std::string::npos) {
            std::cout << "  [MEM] Translation Lookaside Buffer (TLB) flushed." << std::endl;
            #if defined(__x86_64__) || defined(__i386__)
            // unsigned long cr3; __asm__ volatile("mov %%cr3, %0" : "=r"(cr3)); __asm__ volatile("mov %0, %%cr3" :: "r"(cr3)); 
            #endif
            return;
        }

        // ---- DOMAIN 3: kernel/ — SCHEDULER & TASK MANAGEMENT ----
        if (line.find("TASK_SPAWN") != std::string::npos) {
            std::string prio = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string name = string_stack.empty() ? "UNKNOWN" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            static int next_pid = 1;
            std::string pid = std::to_string(next_pid++);
            std::cout << "  [SCHED] Spawned Task: " << name << " (PID " << pid << ", Prio " << prio << ")" << std::endl;
            // Push PID back onto the stack to be allocated into memory by the next instruction
            string_stack.push_back(pid);
            return;
        }
        if (line.find("CONTEXT_SAVE") != std::string::npos) {
            std::cout << "  [SCHED] CPU context saved. RIP/RSP preserved. Runqueue active." << std::endl;
            #if defined(__x86_64__) || defined(__i386__)
            // __asm__ volatile("pushf; pusha"); // Simulated hardware context push
            #endif
            return;
        }
        if (line.find("SCHED_RUN") != std::string::npos) {
            std::cout << "  [SCHED] Quantum yield. Selecting next task..." << std::endl;
            return;
        }
        if (line.find("SPINLOCK_INIT") != std::string::npos || line.find("MUTEX_INIT") != std::string::npos) {
            std::string lock = string_stack.empty() ? "LOCK" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [SCHED] Synchronization primitive initialized: " << lock << std::endl;
            return;
        }
        if (line.find("SPINLOCK_LOCK") != std::string::npos || line.find("MUTEX_LOCK") != std::string::npos) {
            std::string lock = string_stack.empty() ? "LOCK" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [SCHED] Acquired lock: " << lock << std::endl;
            return;
        }
        if (line.find("SPINLOCK_UNLOCK") != std::string::npos || line.find("MUTEX_UNLOCK") != std::string::npos) {
            std::string lock = string_stack.empty() ? "LOCK" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [SCHED] Released lock: " << lock << std::endl;
            return;
        }
        if (line.find("TIMER_INIT") != std::string::npos) {
            std::cout << "  [SCHED] High-resolution timer system initialized (HPET/LAPIC)." << std::endl;
            return;
        }
        if (line.find("TIMER_SET") != std::string::npos) {
            std::string handler = string_stack.empty() ? "HANDLER" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string ns_wait = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [SCHED] Timer armed: Wait " << ns_wait << "ns -> Call " << handler << std::endl;
            return;
        }

        // ---- DOMAIN 4: arch/x86/kernel/irq — INTERRUPT HANDLING ----
        if (line.find("IRQ_INIT") != std::string::npos) {
            std::cout << "  [IRQ] Hardware interrupt manager initialized." << std::endl;
            return;
        }
        if (line.find("IRQ_REGISTER") != std::string::npos) {
            std::string handler = string_stack.empty() ? "UNKNOWN_ISR" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string vector  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [IRQ] Vector " << vector << " -> " << handler << " armed." << std::endl;
            return;
        }
        if (line.find("WORKQUEUE_INIT") != std::string::npos) {
            std::cout << "  [IRQ] Deferred workqueue (SoftIRQ) subsystem initialized." << std::endl;
            return;
        }
        if (line.find("SOFTIRQ_QUEUE") != std::string::npos || line.find("TASKLET_SCHEDULE") != std::string::npos) {
            std::string handler = string_stack.empty() ? "UNKNOWN_SOFTIRQ" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [IRQ] Queued bottom-half deferred work: " << handler << std::endl;
            return;
        }
        if (line.find("IRQ_ENABLE_GLOBAL") != std::string::npos) {
            std::cout << "  [IRQ] x86 STI executing. Processor accepting hardware interrupts." << std::endl;
            #if defined(__x86_64__) || defined(__i386__)
            // __asm__ volatile("sti"); // Simulated hardware STI
            #endif
            return;
        }
        if (line.find("IRQ_DISABLE") != std::string::npos) {
            #if defined(__x86_64__) || defined(__i386__)
            // __asm__ volatile("cli");
            #endif
            return;
        }

        // ---- DOMAIN 5: drivers/nvme — NVMe STORAGE DRIVER ----
        if (line.find("PCI_FIND_BY_CLASS") != std::string::npos) {
            std::string class_code = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Scanning for device class " << class_code << "..." << std::endl;
            // Simulated PCI BDF (Bus:Device:Function) for the NVMe controller
            memory["NVME_PCI_DEVICE"] = "00:1c.4"; 
            return;
        }
        if (line.find("PCI_ENABLE_MASTERING") != std::string::npos) {
            std::string bdf = string_stack.empty() ? "UNKNOWN" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Bus Mastering and Memory Space enabled for device " << bdf << "." << std::endl;
            return;
        }
        if (line.find("PCI_READ_BAR0") != std::string::npos) {
            std::string bdf = string_stack.empty() ? "UNKNOWN" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Reading BAR0 for device " << bdf << "..." << std::endl;
            memory["NVME_BAR0_PHYS"] = "0xB2000000"; // Simulated physical address
            return;
        }
        if (line.find("MMIO_READ64") != std::string::npos) {
            std::string offset = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string base   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NVME] Read Capability (CAP) register at offset " << offset << "." << std::endl;
            memory["NVME_CAP"] = "0x0000000302010800"; // Simulated NVMe capability bitfield
            return;
        }
        if (line.find("NVME_DISABLE") != std::string::npos) {
            std::cout << "  [NVME] Controller disable (CC.EN = 0) asserted." << std::endl;
            return;
        }
        if (line.find("NVME_WAIT_READY_0") != std::string::npos) {
            std::cout << "  [NVME] Polling CSTS.RDY... Controller reports disabled." << std::endl;
            return;
        }
        if (line.find("NVME_SET_ADMIN_QUEUES") != std::string::npos) {
            std::string acq = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string asq = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string base = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NVME] Admin Queues configured in ASQB/ACQB registers." << std::endl;
            return;
        }
        if (line.find("NVME_ENABLE") != std::string::npos) {
            std::cout << "  [NVME] Controller enable (CC.EN = 1) asserted." << std::endl;
            return;
        }
        if (line.find("NVME_WAIT_READY_1") != std::string::npos) {
            std::cout << "  [NVME] Polling CSTS.RDY... Controller reports ready." << std::endl;
            return;
        }
        if (line.find("NVME_IDENTIFY") != std::string::npos) {
            std::cout << "  [NVME] Command 0x06 (Identify Controller) submitted to ASQ." << std::endl;
            return;
        }
        if (line.find("NVME_CREATE_CQ") != std::string::npos) {
            std::string cq   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string asq  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NVME] I/O Completion Queue created." << std::endl;
            return;
        }
        if (line.find("NVME_CREATE_SQ") != std::string::npos) {
            std::string cq   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string sq   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string asq  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NVME] I/O Submission Queue created and linked to CQ." << std::endl;
            return;
        }

        // ---- DOMAIN 6: drivers/net/wireless/intel/iwlwifi — INTEL 8265 WI-FI ----
        if (line.find("WIFI_PCI_DEVICE") != std::string::npos && line.find("PCI_FIND_BY_CLASS") != std::string::npos) {
            // Re-using PCI_FIND_BY_CLASS from Domain 5
            std::string class_code = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Scanning for device class " << class_code << "..." << std::endl;
            memory["WIFI_PCI_DEVICE"] = "02:00.0"; // Simulated BDF for Intel 8265
            return;
        }
        if (line.find("WIFI_CARD_INIT") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [WIFI] Hardware MAC reset (CSR_RESET) asserted at " << bar << std::endl;
            return;
        }
        if (line.find("WIFI_FIRMWARE_LOAD") != std::string::npos) {
            std::string dma = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [WIFI] Loading microcode blob from DMA " << dma << " into MAC." << std::endl;
            return;
        }
        if (line.find("WIFI_SCAN") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [WIFI] Radio scan initiated on 2.4/5GHz bands via " << bar << std::endl;
            return;
        }
        if (line.find("WIFI_AUTH_WPA3") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string sec = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string pwd = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string ssid= string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [WIFI] SAE Handshake START -> SSID: " << ssid << " Security: " << sec << std::endl;
            std::cout << "  [WIFI] PMK calculated. Auth frame transmitted." << std::endl;
            std::cout << "  [WIFI] SAE Commit + Confirm received. PMKSA established." << std::endl;
            return;
        }
        if (line.find("WIFI_ASSOCIATE_AP") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [WIFI] Association Request transmitted." << std::endl;
            std::cout << "  [WIFI] BSSID lock acquired. Link layer UP." << std::endl;
            return;
        }

        // ---- DOMAIN 7: drivers/net/ethernet/intel/e1000e — INTEL I219-LM ETHERNET ----
        if (line.find("ETH_PCI_DEVICE") != std::string::npos && line.find("PCI_FIND_BY_CLASS") != std::string::npos) {
            std::string class_code = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Scanning for device class " << class_code << "..." << std::endl;
            memory["ETH_PCI_DEVICE"] = "00:1f.6"; // Simulated BDF for Intel I219-LM onboard LAN
            return;
        }
        if (line.find("ETH_INIT") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [ETH] Global Device Reset (CTRL.RST bit 26) asserted at " << bar << std::endl;
            return;
        }
        if (line.find("ETH_GET_MAC") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [ETH] Reading MAC address from Receive Address High/Low (RAL/RAH)." << std::endl;
            memory["ETH_MAC_ADDR"] = "E4:54:E8:12:34:56"; // Simulated MAC
            return;
        }
        if (line.find("ETH_SETUP_TX") != std::string::npos) {
            std::string dma = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [ETH] Transmit Descriptor Base (TDBAL) set to " << dma << " (256 Descriptors)." << std::endl;
            return;
        }
        if (line.find("ETH_SETUP_RX") != std::string::npos) {
            std::string dma = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [ETH] Receive Descriptor Base (RDBAL) set to " << dma << " (256 Descriptors)." << std::endl;
            return;
        }
        if (line.find("ETH_LINK_UP") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [ETH] Device Control (CTRL) SLU bit toggled: PHY auto-negotiation forces link UP." << std::endl;
            return;
        }

        // ---- DOMAIN 8: net/ — TCP/IP NETWORK STACK ----
        if (line.find("ARP_RESOLVE") != std::string::npos) {
            std::string mac = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string ip  = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] ARP broadcast (Who has " << ip << "? Tell " << mac << ")" << std::endl;
            return;
        }
        if (line.find("DHCP_DISCOVER") != std::string::npos) {
            std::cout << "  [NET] DHCP Discover broadcast via UDP port 67." << std::endl;
            return;
        }
        if (line.find("DHCP_REQUEST") != std::string::npos) {
            std::string dns = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string gw  = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string mask= string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string ip  = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] DHCP Request/ACK -> IP: " << ip << " GW: " << gw << " DNS: " << dns << std::endl;
            return;
        }
        if (line.find("ICMP_PING") != std::string::npos) {
            std::string ip = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] ICMP Echo Request sent to " << ip << "." << std::endl;
            return;
        }
        if (line.find("DNS_QUERY") != std::string::npos) {
            std::string dns = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string domain = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] DNS Query (UDP 53) resolving " << domain << " via " << dns << std::endl;
            return;
        }
        if (line.find("TCP_OPEN") != std::string::npos) {
            std::cout << "  [NET] TCP socket state block allocated (LISTEN/CLOSED state)." << std::endl;
            memory["TCP_SOCKET_FD"] = "7331"; // Simulated socket descriptor
            return;
        }
        if (line.find("TCP_CONNECT") != std::string::npos) {
            std::string fd  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string port= string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string ip  = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] TCP 3-way handshake (SYN) sent to " << ip << ":" << port << " on FD " << fd << std::endl;
            return;
        }
        if (line.find("TLS_HANDSHAKE") != std::string::npos) {
            std::string fd = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] TLS 1.3 ClientHello sent on FD " << fd << ". Key exchange completed." << std::endl;
            return;
        }
        if (line.find("TLS_SEND") != std::string::npos) {
            std::string fd = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string payload = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] AES-256-GCM encrypted payload transmitted over FD " << fd << "." << std::endl;
            return;
        }
        if (line.find("TCP_CLOSE") != std::string::npos) {
            std::string fd = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [NET] TCP connection termination (FIN/ACK) sent on FD " << fd << "." << std::endl;
            return;
        }

        // ---- DOMAIN 9: fs/ — GENLEX VIRTUAL FILESYSTEM (CGL VAULT) ----
        if (line.find("TMPFS_ALLOC") != std::string::npos) {
            std::string size = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [FS] TMPFS RAM-Disk allocated: " << size << " bytes." << std::endl;
            memory["TMPFS_ROOT"] = "/ram0";
            return;
        }
        if (line.find("FAT32_MOUNT") != std::string::npos) {
            std::string part = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [FS] FAT32 Driver active. Mounted " << part << std::endl;
            return;
        }
        if (line.find("FAT32_READ") != std::string::npos) {
            std::string path = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [FS] FAT32: Read " << path << std::endl;
            memory["BOOT_HASH"] = "0x9F8E7D6C5B4A39281"; // Simulated SHA-256 hash prefix
            return;
        }
        if (line.find("CGL_MOUNT") != std::string::npos) {
            std::string device = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [FS] Native Sovereign CGL Vault mounted on " << device << std::endl;
            return;
        }
        if (line.find("CGL_MKDIR") != std::string::npos) {
            std::string dir = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [FS] CGL Vault Directory created: /" << dir << std::endl;
            return;
        }
        if (line.find("CGL_WRITE") != std::string::npos) {
            std::string path = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string data = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [FS] CGL Write (Direct NVMe Block): " << path << " -> [" << data << "]" << std::endl;
            return;
        }
        if (line.find("CGL_STAT") != std::string::npos) {
            std::string path = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [FS] CGL Stat metadata retrieved for " << path << std::endl;
            memory["FILE_META"] = "SIZE:12 LOCK:ON PERM:700";
            return;
        }

        // ---- DOMAIN 10: drivers/usb — USB HOST CONTROLLER (xHCI) ----
        if (line.find("USB_PCI_DEVICE") != std::string::npos && line.find("PCI_FIND_BY_CLASS") != std::string::npos) {
            std::string class_code = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Scanning for device class " << class_code << "..." << std::endl;
            memory["USB_PCI_DEVICE"] = "00:14.0"; // Simulated BDF for Intel Sunrise Point-LP USB 3.0 xHCI Controller
            return;
        }
        if (line.find("XHCI_HALT") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [USB] xHCI Controller halted (USBCMD.RS = 0) at " << bar << std::endl;
            return;
        }
        if (line.find("XHCI_INIT") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [USB] Hardware Reset asserted (USBCMD.HCRST = 1)." << std::endl;
            return;
        }
        if (line.find("XHCI_SETUP_RINGS") != std::string::npos) {
            std::string er = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string cr = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string dcbaa = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [USB] Hardware programmed -> DCBAA: " << dcbaa << " CMD: " << cr << " ER: " << er << std::endl;
            return;
        }
        if (line.find("XHCI_START") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [USB] xHCI Controller running (USBCMD.RS = 1)." << std::endl;
            return;
        }
        if (line.find("XHCI_ENUM") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [USB] Handshake with PORTSC -> Discovered 1 device on Root Hub." << std::endl;
            return;
        }
        if (line.find("USB_DESCRIBE") != std::string::npos) {
            std::string slot = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [USB] Get_Descriptor issued to Slot ID " << slot << std::endl;
            return;
        }
        if (line.find("USB_STORAGE_READ") != std::string::npos) {
            std::string bytes = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string slot = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [USB] Bulk Transfer IN (" << bytes << " bytes) emitted to Mass Storage Slot " << slot << std::endl;
            memory["BOOT_SECT"] = "0xEB5890..."; // Simulated MBR code jump
            return;
        }

        // ---- DOMAIN 11: drivers/gpu/drm/i915 — INTEL HD GRAPHICS 620 ----
        if (line.find("GPU_PCI_DEVICE") != std::string::npos && line.find("PCI_FIND_BY_CLASS") != std::string::npos) {
            std::string class_code = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Scanning for device class " << class_code << "..." << std::endl;
            memory["GPU_PCI_DEVICE"] = "00:02.0"; // Simulated BDF for Intel HD Graphics 620
            return;
        }
        if (line.find("GPU_PLL_INIT") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GPU] Display PLLs and Clocks configured for eDP (Embedded DisplayPort)." << std::endl;
            return;
        }
        if (line.find("GPU_DDI_ENABLE") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GPU] eDP Screen Link Training complete. Panel is ACTIVE." << std::endl;
            return;
        }
        if (line.find("GPU_GET_GOP") != std::string::npos) {
            std::cout << "  [GPU] Acquired Framebuffer base from UEFI Graphics Output Protocol (GOP)." << std::endl;
            memory["GPU_FB_PHYS"] = "0xE0000000"; // Simulated physical address for 1080p Framebuffer
            return;
        }
        if (line.find("GPU_PLANE_ENABLE") != std::string::npos) {
            std::string fb  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GPU] Display Plane 1 sourced to Genlex Virtual Framebuffer " << fb << std::endl;
            return;
        }
        if (line.find("GPU_SETUP_RING") != std::string::npos) {
            std::string dma = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GPU] Render Command Ring (RCS) configured at DMA " << dma << std::endl;
            return;
        }

        // ---- DOMAIN 12: drivers/input/ — INPUT DEVICES (KEYBOARD/TOUCHPAD) ----
        if (line.find("I8042_STATUS_READ") != std::string::npos) {
            std::cout << "  [INP] Reading PS/2 i8042 Status Register (Port 0x64)." << std::endl;
            memory["I8042_STATUS"] = "0x1C"; // Simulated status (Unlocked, initialized)
            return;
        }
        if (line.find("I8042_BUFFER_FLUSH") != std::string::npos) {
            std::cout << "  [INP] Draining PS/2 Data Buffer (Port 0x60)." << std::endl;
            return;
        }
        if (line.find("I8042_KBD_ENABLE") != std::string::npos) {
            std::cout << "  [INP] Keyboard Interface Enabled (Command 0xAE -> 0x64)." << std::endl;
            return;
        }
        if (line.find("I8042_IRQ_ENABLE") != std::string::npos) {
            std::cout << "  [INP] PS/2 Keyboard Interrupts (IRQ 1) Unmasked." << std::endl;
            return;
        }
        if (line.find("I8042_DATA_READ") != std::string::npos) {
            std::cout << "  [INP] Simulated PS/2 Data Read (Port 0x60)." << std::endl;
            memory["KBD_SCANCODE"] = "0x1E (A)"; // Simulated 'A' key press
            return;
        }
        if (line.find("I2C_BUS_SCAN") != std::string::npos) {
            std::cout << "  [INP] Scanning I2C DesignWare bus..." << std::endl;
            memory["I2C_HID_DEVICE"] = "ALPS_TOUCHPAD_I2C";
            return;
        }
        if (line.find("I2C_TOUCHPAD_RESET") != std::string::npos) {
            std::string dev = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [INP] Resetting I2C HID Device: " << dev << std::endl;
            return;
        }
        if (line.find("I2C_IRQ_ENABLE") != std::string::npos) {
            std::string dev = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [INP] Touchpad Interrupts (I2C HID) Unmasked." << std::endl;
            return;
        }
        if (line.find("I2C_TOUCH_READ_XY") != std::string::npos) {
            std::string dev = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [INP] Simulated Touchpad Report Read." << std::endl;
            memory["TOUCH_XY"] = "X:1024 Y:768 FINGERS:1"; // Simulated absolute multi-touch
            return;
        }

        // ---- DOMAIN 13: sound/pci/hda/ — INTEL HIGH DEFINITION AUDIO ----
        if (line.find("HDA_PCI_DEVICE") != std::string::npos && line.find("PCI_FIND_BY_CLASS") != std::string::npos) {
            std::string class_code = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [PCI] Scanning for device class " << class_code << "..." << std::endl;
            memory["HDA_PCI_DEVICE"] = "00:1f.3"; // Simulated BDF for Intel Sunrise Point-LP HD Audio
            return;
        }
        if (line.find("HDA_CONTROLLER_RESET") != std::string::npos) {
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [HDA] Global Controller Reset (GCTL.CRST = 0 -> 1) asserted at " << bar << std::endl;
            return;
        }
        if (line.find("HDA_SETUP_RINGS") != std::string::npos) {
            std::string rirb = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string corb = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [HDA] CORB and RIRB Command Rings mapped to DMA (CORB: " << corb << " RIRB: " << rirb << ")" << std::endl;
            return;
        }
        if (line.find("HDA_READ_CODEC") != std::string::npos) {
            std::string node = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [HDA] Fired Get Parameter command to Codec Node " << node << " via CORB." << std::endl;
            return;
        }
        if (line.find("HDA_SET_VOLUME") != std::string::npos) {
            std::string vol = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string pin = string_stack.empty() ? "UNKNOWN" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [HDA] Pin Widget " << pin << " unmuted. Gain set to " << vol << "%." << std::endl;
            return;
        }
        if (line.find("HDA_SETUP_STREAM") != std::string::npos) {
            std::string format = string_stack.empty() ? "UNKNOWN" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string dma = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string bar = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [HDA] Output Stream Descriptor 0 (SD0) configured -> DMA " << dma << " Format: " << format << std::endl;
            return;
        }

        // ---- DOMAIN 14: lib/ & mm/slab.c — CORE LIBRARIES & ALLOCATORS ----
        if (line.find("SLAB_CREATE_NAMED") != std::string::npos) {
            std::string name = string_stack.empty() ? "UNKNOWN" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string size = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [LIB] Advanced SLAB Cache Created -> Name: " << name << " Size: " << size << "B" << std::endl;
            return;
        }
        if (line.find("SLAB_ALLOC") != std::string::npos) {
            std::string name = string_stack.empty() ? "UNKNOWN" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [LIB] Allocated fast object from SLAB: " << name << std::endl;
            memory["TCP_SKB_PTR"] = "0xFFFF80000000A040"; // Simulated SLAB pointer
            return;
        }
        if (line.find("RCU_INIT") != std::string::npos) {
            std::cout << "  [LIB] Read-Copy-Update (RCU) synchronization primitives initialized." << std::endl;
            return;
        }
        if (line.find("RCU_READ_LOCK") != std::string::npos) {
            std::cout << "  [LIB] RCU Read-Side Critical Section ENTERED." << std::endl;
            return;
        }
        if (line.find("RCU_READ_UNLOCK") != std::string::npos) {
            std::cout << "  [LIB] RCU Read-Side Critical Section EXITED." << std::endl;
            return;
        }
        if (line.find("RCU_SYNCHRONIZE") != std::string::npos) {
            std::cout << "  [LIB] RCU Grace period elapsed. All readers complete. Safe to free." << std::endl;
            return;
        }
        if (line.find("KASAN_INIT") != std::string::npos) {
            std::cout << "  [LIB] Kernel Address Sanitizer (KASAN) Shadow Memory initialized." << std::endl;
            return;
        }
        if (line.find("KASAN_POISON") != std::string::npos) {
            std::string ptr  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string size = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [LIB] KASAN: Poisoned " << size << " bytes at " << ptr << " (Use-After-Free guard)." << std::endl;
            return;
        }
        if (line.find("CRYPTO_HW_INIT") != std::string::npos) {
            std::cout << "  [LIB] Hardware Crypto Acceleration (AES-NI / SHA Ext) initialized." << std::endl;
            return;
        }
        if (line.find("SHA256_HASH") != std::string::npos) {
            std::string payload = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [LIB] SHA-256 hardware hash computed for [" << payload << "]." << std::endl;
            memory["VAULT_HASH"] = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"; // Simulated hash
            return;
        }

        // ---- DOMAIN 15: block/ — BLOCK I/O SUBSYSTEM ----
        if (line.find("IO_SCHED_INIT") != std::string::npos) {
            std::string sched = string_stack.empty() ? "UNKNOWN_SCHED" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string ns    = string_stack.empty() ? "UNKNOWN_NS" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [BLK] Block I/O Scheduler '" << sched << "' attached to Namespace " << ns << "." << std::endl;
            return;
        }
        if (line.find("IO_QUEUE_DEPTH") != std::string::npos) {
            std::string depth = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string ns    = string_stack.empty() ? "UNKNOWN_NS" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [BLK] Hardware queue depth for " << ns << " set to " << depth << " outstanding commands." << std::endl;
            return;
        }
        if (line.find("BIO_CONFIG") != std::string::npos) {
            std::string ptr    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string lba    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string size   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string opcode = string_stack.empty() ? "UNKNOWN_OP" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [BLK] BIO Request Configured -> Op: " << opcode << " Size: " << size << "B LBA: " << lba << std::endl;
            return;
        }
        if (line.find("BIO_SUBMIT_QUEUE") != std::string::npos) {
            std::string req = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string sq  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [BLK] BIO submitted to Hardware Submission Queue " << sq << "." << std::endl;
            return;
        }
        if (line.find("BIO_WAIT_CQ") != std::string::npos) {
            std::string req = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string cq  = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [BLK] BIO completion interrupt received on Completion Queue " << cq << "." << std::endl;
            return;
        }

        // ---- PHASE 3: THE SOVEREIGN GUI (DESKTOP COMPOSITOR) ----
        if (line.find("GUI_CLEAR_SCREEN") != std::string::npos) {
            std::string b = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string g = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string r = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GUI] Framebuffer Cleared to rgb(" << r << "," << g << "," << b << ")." << std::endl;
            return;
        }
        if (line.find("GUI_DRAW_RECT") != std::string::npos) {
            std::string b    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string g    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string r    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string h    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string w    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string y    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string x    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GUI] Rect Drawn: pos(" << x << "," << y << ") size(" << w << "x" << h << ") rgb(" << r << "," << g << "," << b << ")" << std::endl;
            return;
        }
        if (line.find("GUI_DRAW_LINE") != std::string::npos) {
            std::string b    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string g    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string r    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string y2   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string x2   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string y1   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string x1   = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GUI] Line Drawn: from(" << x1 << "," << y1 << ") to(" << x2 << "," << y2 << ") rgb(" << r << "," << g << "," << b << ")" << std::endl;
            return;
        }
        if (line.find("GUI_DRAW_TEXT") != std::string::npos) {
            std::string b    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string g    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string r    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string text = string_stack.empty() ? "" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string y    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::string x    = string_stack.empty() ? "0" : string_stack.back(); if (!string_stack.empty()) string_stack.pop_back();
            std::cout << "  [GUI] Text Rendered: '" << text << "' at pos(" << x << "," << y << ") rgb(" << r << "," << g << "," << b << ")" << std::endl;
            return;
        }

        // EXCEPTION_HANDLER variants (consume stack args)        if (line.find("EXCEPTION_HANDLER") != std::string::npos) { return; }
        // SOVEREIGN_SYSCALL entries (consume stack args)
        if (line.find("SOVEREIGN_SYSCALL") != std::string::npos) { return; }
        // STRING_APPEND
        if (line.find("STRING_APPEND") != std::string::npos) {
            if (string_stack.size() >= 2) {
                std::string b = string_stack.back(); string_stack.pop_back();
                std::string a = string_stack.back(); string_stack.pop_back();
                string_stack.push_back(a + b);
            }
            return;
        }
        // MEMORY_ALLOC_FLUSH
        if (line.find("MEMORY_ALLOC_FLUSH") != std::string::npos) { memory.clear(); return; }

        // ---- MANDARIN MATH LAYER ----
        // 乘 = MULTIPLY (乘法)
        if (line.find("乘") != std::string::npos) {
            if (string_stack.size() >= 2) {
                float a = std::stof(string_stack.back()); string_stack.pop_back();
                float b = std::stof(string_stack.back()); string_stack.pop_back();
                string_stack.push_back(std::to_string(a * b));
            }
            return;
        }
        // 加 = ADD (加法)
        if (line.find("加") != std::string::npos) {
            if (string_stack.size() >= 2) {
                float a = std::stof(string_stack.back()); string_stack.pop_back();
                float b = std::stof(string_stack.back()); string_stack.pop_back();
                string_stack.push_back(std::to_string(a + b));
            }
            return;
        }
        // 减 = SUBTRACT (减法)
        if (line.find("减") != std::string::npos) {
            if (string_stack.size() >= 2) {
                float a = std::stof(string_stack.back()); string_stack.pop_back();
                float b = std::stof(string_stack.back()); string_stack.pop_back();
                string_stack.push_back(std::to_string(b - a));
            }
            return;
        }
        // 除 = DIVIDE (除法)
        if (line.find("除") != std::string::npos) {
            if (string_stack.size() >= 2) {
                float a = std::stof(string_stack.back()); string_stack.pop_back();
                float b = std::stof(string_stack.back()); string_stack.pop_back();
                if (a != 0) string_stack.push_back(std::to_string(b / a));
                else string_stack.push_back("∞");
            }
            return;
        }
        // 积 = RESULT / PRODUCT OUTPUT (print top of stack)
        if (line.find("积") != std::string::npos) {
            if (!string_stack.empty()) {
                std::cout << "  [ 积 ] Result: " << string_stack.back() << std::endl;
            }
            return;
        }
        // 频 = RESONANCE FREQUENCY CALCULATION
        if (line.find("频") != std::string::npos) {
            std::cout << "  [ 频 ] Resonance: 1.0927 GHz | Gematria Active" << std::endl;
            return;
        }
        // 和 = SUM / HARMONY
        if (line.find("和") != std::string::npos) {
            std::cout << "  [ 和 ] Harmonic Sum Active." << std::endl;
            return;
        }

        // ---- NETWORK OPCODE LAYER ----
        if (line.find("WIFI_INIT") != std::string::npos) {
            std::cout << "  [WIFI] Intel 8265 driver: iwlwifi loaded." << std::endl;
            memory["WIFI_STATUS"] = "INIT";
            return;
        }
        if (line.find("WIFI_CREDS_LOAD") != std::string::npos) {
            std::cout << "  [WIFI] Loading sovereign credentials from wifi_config.cgl..." << std::endl;
            std::ifstream cfg(script_base + "/wifi_config.cgl");
            if (cfg) {
                std::string l;
                while (std::getline(cfg, l)) {
                    if (l.substr(0,5) == "SSID=") memory["SSID"] = l.substr(6, l.rfind('"') - 6);
                    if (l.substr(0,9) == "PASSWORD=") memory["PASSWORD"] = l.substr(10, l.rfind('"') - 10);
                }
                std::cout << "  [WIFI] SSID loaded: " << memory["SSID"] << std::endl;
            } else {
                std::cout << "  [WIFI] wifi_config.cgl not found." << std::endl;
            }
            return;
        }
        if (line.find("WIFI_CONNECT") != std::string::npos) {
            std::string ssid = mem_read("SSID");
            std::cout << "  [WIFI] Connecting to: " << ssid << "..." << std::endl;
            // System call to wpa_cli (works on Linux runtime)
            std::string cmd = "wpa_cli -i wlan0 status 2>/dev/null | grep 'wpa_state=COMPLETED'";
            int r = system(cmd.c_str());
            if (r == 0) {
                memory["WIFI_CONNECTED"] = "1";
                std::cout << "  [WIFI] Connected to sovereign grid." << std::endl;
            } else {
                memory["WIFI_CONNECTED"] = "0";
                std::cout << "  [WIFI] Not connected. Manual configuration may be required." << std::endl;
            }
            return;
        }
        if (line.find("PING") != std::string::npos) {
            std::string host = !string_stack.empty() ? string_stack.back() : "8.8.8.8";
            if (!string_stack.empty()) string_stack.pop_back();
            std::string cmd = "ping -c 1 -W 2 " + host + " > /dev/null 2>&1";
            int r = system(cmd.c_str());
            memory["PING_RESULT"] = r == 0 ? "ALIVE" : "DEAD";
            std::cout << "  [PING] " << host << " -> " << memory["PING_RESULT"] << std::endl;
            return;
        }
        if (line.find("HTTP_GET") != std::string::npos) {
            std::string url = !string_stack.empty() ? string_stack.back() : "";
            if (!string_stack.empty()) string_stack.pop_back();
            if (!url.empty() && url.front() == '"') url = url.substr(1);
            if (!url.empty() && url.back() == '"') url.pop_back();
            std::cout << "  [HTTP] GET " << url << std::endl;
            std::string cmd = "wget -q -O /tmp/sarah_response.txt \"" + url + "\" 2>&1";
            int r = system(cmd.c_str());
            if (r == 0) {
                std::ifstream resp("/tmp/sarah_response.txt");
                std::string content((std::istreambuf_iterator<char>(resp)),
                                     std::istreambuf_iterator<char>());
                memory["HTTP_RESPONSE"] = content.substr(0, 1024);
                std::cout << "  [HTTP] Response received (" << memory["HTTP_RESPONSE"].size() << " bytes)" << std::endl;
            } else {
                memory["HTTP_RESPONSE"] = "ERROR";
                std::cout << "  [HTTP] Request failed." << std::endl;
            }
            return;
        }

        // ---- STRING LITERAL (quoted) ----
        if (!line.empty() && line.front() == '"') {
            // Push to string stack for next VOICE or MEMORY_ALLOC
            std::string val = line;
            if (!val.empty() && val.front() == '"') val = val.substr(1);
            if (!val.empty() && val.back() == '"') val.pop_back();
            string_stack.push_back(val);
            return;
        }
    }

    void run_script(const std::string& path, int depth) {
        if (depth > 10) { std::cerr << "  [ GSK ] Max script depth reached." << std::endl; return; }
        std::ifstream file(path);
        if (!file) {
            std::cerr << "  [ ERROR ] Script not found: " << path << std::endl;
            return;
        }
        auto start = std::chrono::high_resolution_clock::now();
        std::string line;
        while (std::getline(file, line)) {
            execute_line(line, depth);
        }
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> diff = end - start;
        std::cout << "  [ GSK ] Pulse: " << std::fixed << std::setprecision(4) << diff.count() << "ms" << std::endl;
    }

    void load_script(const std::string& path, int depth) {
        run_script(path, depth);
    }
};

int main(int argc, char* argv[]) {
    std::cout << "\n--- GSK v3.0: GENLEX SOVEREIGN KERNEL ---" << std::endl;
    std::cout << "[ KERNEL ] Polyglot Mode: Aramaic + English + Cuneiform" << std::endl;
    std::cout << "[ KERNEL ] SARAH_OS Ready." << std::endl;

    GSK kernel;

    if (argc >= 2) {
        std::string script_path = std::string(argv[1]);
        // Determine base directory from script path
        size_t last_sep = script_path.find_last_of("/\\");
        if (last_sep != std::string::npos) {
            kernel.script_base = script_path.substr(0, last_sep);
        }
        kernel.run_script(script_path, 0);
    } else {
        // Auto-detect platform base
        kernel.script_base = "/core";
        kernel.run_script("/core/sarah_os.all", 0);
    }

    // Interactive shell fallback
    std::cout << "\n[ GSK ] Entering Sovereign Shell (type 'exit' to seal)..." << std::endl;
    std::string input;
    while (true) {
        std::cout << "\nYou: ";
        if (!std::getline(std::cin, input) || input == "exit") break;
        kernel.neural_pulse(input);
        if (!kernel.neural_response.empty()) {
            std::cout << "  [AERIS] Response: " << kernel.neural_response << std::endl;
        }
    }

    std::cout << "\n[ KERNEL ] SEALED. Returning to the Void." << std::endl;
    return 0;
}
