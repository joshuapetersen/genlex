import os, sys, io, csv, json, time, subprocess, shutil, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

GENLEX_MAP   = r"C:\Genlex_Linear\genlex_mapping.csv"
HISTORY_FILE = r"C:\Genlex_Linear\terminal_history.json"

BANNER = """\033[38;2;0;255;204m
  ╔═══════════════════════════════════════════════════╗
  ║   GENESIS  //  GENLEX TERMINAL  //  v2.0          ║
  ║   Speak English. The machine speaks Genlex.       ║
  ╚═══════════════════════════════════════════════════╝\033[0m
"""

# ── Colors ────────────────────────────────────────────────────────────────────
def c(t, r, g, b): return f"\033[38;2;{r};{g};{b}m{t}\033[0m"
CYAN  = lambda t: c(t,  0, 255, 204)
DCYAN = lambda t: c(t,  0, 120, 120)
WHITE = lambda t: c(t, 220, 220, 220)
GREEN = lambda t: c(t,  0, 255, 100)
RED   = lambda t: c(t, 255,  80,  80)
AMBER = lambda t: c(t, 255, 180,   0)
GREY  = lambda t: c(t,  80,  80,  80)
PINK  = lambda t: c(t, 200,  80, 200)

# ── English → Genlex Intent Map ───────────────────────────────────────────────
# Each entry: list of trigger keywords → (genlex_op, ps_command or None)
INTENTS = [
    # Files & dirs — longer/more specific triggers FIRST
    (['list files', 'show files', 'ls', 'dir'], 'LIST_FS',
        lambda args: f"Get-ChildItem {args if args and not args.lower() in ('files','file','') else '.'} | Format-Table Name,Length,LastWriteTime -Auto"),
    (['read file', 'read', 'open file', 'cat', 'show file'], 'READ_FS',
        lambda args: f"Get-Content \"{args}\"" if args else "Write-Host 'Usage: read <filename>'"),
    (['delete file', 'remove file', 'delete', 'remove', 'rm'], 'DELETE_FS',
        lambda args: f"Remove-Item \"{args}\" -Confirm" if args else "Write-Host 'Usage: delete <filename>'"),
    (['make dir', 'new folder', 'mkdir', 'create dir'], 'MKDIR',
        lambda args: f"New-Item -ItemType Directory -Path \"{args}\"" if args else "Write-Host 'Usage: mkdir <name>'"),
    (['move file', 'move', 'mv'], 'MOVE_FS',
        lambda args: f"Move-Item {args}" if args else "Write-Host 'Usage: move <src> <dst>'"),
    (['copy file', 'copy', 'cp'], 'COPY_FS',
        lambda args: f"Copy-Item {args}" if args else "Write-Host 'Usage: copy <src> <dst>'"),

    # Processes
    (['process list', 'list processes', 'processes', 'tasks', 'running'], 'LIST_PROC',
        lambda args: "Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 | Format-Table Name,CPU,WorkingSet -Auto"),
    (['kill process', 'kill', 'stop process', 'stop', 'terminate'], 'KILL_PROC',
        lambda args: f"Stop-Process -Name {args} -Force" if args else "Write-Host 'Usage: kill <processname>'"),
    (['launch', 'start app', 'open app', 'run app'], 'LAUNCH_APP',
        lambda args: f"Start-Process {args}" if args else "Write-Host 'Usage: launch <app>'"),

    # Network
    (['ping'], 'PING',
        lambda args: f"ping {args if args else '8.8.8.8'} -n 4"),
    (['network info', 'ip address', 'network', 'interfaces', 'ipconfig'], 'NET_INFO',
        lambda args: "Get-NetIPAddress | Format-Table InterfaceAlias,IPAddress -Auto"),
    (['wifi', 'wireless'], 'WIFI_STATUS',
        lambda args: "netsh wlan show interfaces"),

    # System
    (['free memory', 'memory usage', 'memory', 'ram'], 'MEM_STATUS',
        lambda args: "(Get-WmiObject Win32_OperatingSystem | Select-Object @{n='FreeGB';e={[math]::Round($_.FreePhysicalMemory/1MB,2)}},@{n='TotalGB';e={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}} | Format-List)"),
    (['disk space', 'disk usage', 'disk', 'storage', 'drives'], 'DISK_STATUS',
        lambda args: "Get-PSDrive -PSProvider FileSystem | Format-Table Name,@{n='UsedGB';e={[math]::Round($_.Used/1GB,1)}},@{n='FreeGB';e={[math]::Round($_.Free/1GB,1)}},Root -Auto"),
    (['cpu usage', 'cpu load', 'cpu', 'processor'], 'CPU_STATUS',
        lambda args: "Get-WmiObject Win32_Processor | Select-Object Name,LoadPercentage | Format-List"),
    (['system info', 'sysinfo', 'system', 'info'], 'SYS_INFO',
        lambda args: "Get-ComputerInfo | Select-Object CsName,OsName,WindowsVersion | Format-List"),
    (['time', 'clock', 'date'], 'SYS_TIME',
        lambda args: "Get-Date"),
    (['uptime'], 'UPTIME',
        lambda args: '"Uptime: " + ((Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime).ToString()'),

    # Genlex / Genesis
    (['run genlex', 'execute genlex', 'genlex run', 'run script'], 'EXEC_GENLEX',
        lambda args: f"python C:\\Genlex_Linear\\all_engine.py {args}" if args else "Write-Host 'Usage: run genlex <file.all>'"),
    (['seal', 'save state', 'commit state'], 'COMMIT_STATE', None),
    (['vars', 'variables', 'memory vars', 'show mem'], 'SHOW_MEM', None),
    (['clear', 'cls'], 'CLEAR', None),
    (['help'], 'HELP', None),
    (['exit', 'quit'], 'EXIT', None),
]

def load_lexicon():
    lex = {}
    try:
        with open(GENLEX_MAP, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lex[row['Operation']] = {'glyph': row['Glyph'], 'concept': row['Concept'], 'cat': row['Category']}
    except FileNotFoundError:
        pass
    return lex

def run_ps(cmd, timeout=15):
    try:
        r = subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', cmd],
            capture_output=True, text=True, timeout=timeout)
        return (r.stdout or '').strip(), (r.stderr or '').strip()
    except subprocess.TimeoutExpired:
        return '', 'TIMEOUT'
    except Exception as e:
        return '', str(e)

def match_intent(line):
    lower = line.lower()
    for (triggers, op, ps_fn) in INTENTS:
        for trig in triggers:
            if trig in lower:
                # Extract argument (everything after the trigger keyword)
                idx = lower.find(trig)
                args = line[idx + len(trig):].strip()
                return op, ps_fn, args
    return None, None, None

def show_help():
    print(CYAN("\n  ┌─ WHAT YOU CAN SAY ──────────────────────────────────────────────┐"))
    examples = [
        ("list files",             "List files in current directory"),
        ("list files C:\\Users",   "List files in a specific path"),
        ("read myfile.txt",        "Show file contents"),
        ("processes",              "Show running processes"),
        ("kill notepad",           "Kill a process"),
        ("launch notepad",         "Open an application"),
        ("ping 8.8.8.8",           "Ping a host"),
        ("network",                "Show network interfaces"),
        ("memory",                 "Show RAM usage"),
        ("disk",                   "Show disk usage"),
        ("cpu",                    "Show CPU info"),
        ("sysinfo",                "Full system info"),
        ("run genlex myfile.all",  "Execute a Genlex script"),
        ("seal",                   "Save memory state"),
        ("clear",                  "Clear screen"),
        ("exit",                   "Exit terminal"),
    ]
    for cmd, desc in examples:
        print(f"  │ {AMBER(cmd.ljust(30))} {GREY(desc)}")
    print(CYAN("  └────────────────────────────────────────────────────────────────┘"))
    print(DCYAN("  Anything not matched is passed directly to PowerShell.\n"))

def save_history(hist):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(hist[-200:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def main():
    if sys.platform == 'win32':
        os.system('color')
    print(BANNER)
    lex = load_lexicon()
    print(DCYAN(f"  Lexicon: {len(lex)} Genlex operations loaded."))
    print(DCYAN(f"  PowerShell: {shutil.which('powershell') or 'NOT FOUND'}"))
    print(GREY("  Type 'help' to see what you can say.\n"))

    memory = {}
    history = load_history()
    cwd = os.getcwd()

    while True:
        try:
            prompt = (f"\033[38;2;0;80;80m╔[\033[38;2;0;200;150mGENESIS\033[38;2;0;80;80m]"
                      f"─[\033[38;2;0;120;100m{os.path.basename(cwd)}\033[38;2;0;80;80m]\033[0m\n"
                      f"\033[38;2;0;80;80m╚▶ \033[0m")
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print(CYAN("\n\n  [ GENESIS TERMINAL CLOSED ]\n"))
            break

        if not line:
            continue

        history.append({'ts': time.time(), 'cmd': line})
        save_history(history)

        op, ps_fn, args = match_intent(line)

        # Special internal ops
        if op == 'EXIT':
            print(CYAN("\n  [ GENESIS TERMINAL CLOSED ]\n"))
            break
        elif op == 'CLEAR':
            os.system('cls' if sys.platform == 'win32' else 'clear')
            print(BANNER)
            continue
        elif op == 'HELP':
            show_help()
            continue
        elif op == 'SHOW_MEM':
            if memory:
                for k, v in memory.items():
                    print(f"  {AMBER(k)} = {WHITE(str(v))}")
            else:
                print(GREY("  [MEMORY CLEAR]"))
            print()
            continue
        elif op == 'COMMIT_STATE':
            with open(r'C:\Genlex_Linear\execution_seal.json', 'w') as f:
                json.dump({'memory': memory, 'ts': time.time()}, f, indent=2)
            print(GREEN("  ✓ STATE SEALED\n"))
            continue

        # Show Genlex translation
        if op and op in lex:
            entry = lex[op]
            print(f"  {GREY('→')} {PINK(entry['glyph'])} {DCYAN(op)} {GREY(entry['concept'])}")

        # Execute via PowerShell
        if op and ps_fn:
            cmd = ps_fn(args)
            if cmd:
                print(AMBER(f"  ⚡ ") + GREY(cmd))
                t0 = time.time()
                out, err = run_ps(cmd)
                elapsed = time.time() - t0
                if out:
                    for ln in out.splitlines():
                        print(f"  {GREEN('▸')} {WHITE(ln)}")
                if err:
                    print(RED(f"  ✗ {err}"))
                print(GREY(f"  [{elapsed:.2f}s]\n"))
            else:
                print(RED("  ✗ Missing argument. Example: ") + AMBER(f"{line} <target>\n"))
        elif not op:
            # Unknown → route directly to PowerShell
            print(AMBER(f"  ⚡ PS> ") + GREY(line))
            t0 = time.time()
            out, err = run_ps(line)
            elapsed = time.time() - t0
            if out:
                for ln in out.splitlines():
                    print(f"  {GREEN('▸')} {WHITE(ln)}")
            if err:
                print(RED(f"  ✗ {err}"))
            if not out and not err:
                print(GREY("  (no output)"))
            print(GREY(f"  [{elapsed:.2f}s]\n"))

if __name__ == '__main__':
    main()
