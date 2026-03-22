# PUSH_TO_SARAH.PS1 - Sovereign Code Push Tool
# Run this on the Windows development machine to push
# Genlex .all scripts directly to Sarah on the Dell 5490
# Connection: Ethernet (crossover or router) OR USB-C (USB Network Sharing)
#
# USAGE:
#   .\push_to_sarah.ps1                         # Push all .all files
#   .\push_to_sarah.ps1 -File sarah_os.all      # Push specific file
#   .\push_to_sarah.ps1 -Discover               # Find Sarah on network

param(
    [string]$File = "",
    [string]$SarahIP = "192.168.5.49",   # Dell 5490 static IP (set in sarah_os.all)
    [int]$Port = 5490,                    # Sovereign port (Dell model number)
    [switch]$Discover
)

$GENLEX_PATH = "C:\Genlex_Core"
$SARAH_URL   = "http://${SarahIP}:${Port}/push"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗"
Write-Host "║  SOVEREIGN CODE PUSH — WINDOWS → DELL 5490      ║"
Write-Host "║  Architect: Joshua Petersen | Genlex Push Tool  ║"
Write-Host "╚══════════════════════════════════════════════════╝"
Write-Host ""

# --- DISCOVER MODE: find Sarah on local network ---
if ($Discover) {
    Write-Host "[SCAN] Scanning for Sarah on local network..."
    $subnet = "192.168.5"
    for ($i = 1; $i -le 254; $i++) {
        $ip = "$subnet.$i"
        try {
            $r = Invoke-WebRequest -Uri "http://${ip}:5490/ping" -TimeoutSec 1 -EA Stop
            if ($r.Content -match "SARAH") {
                Write-Host "[FOUND] Sarah is at: $ip"
                $SarahIP = $ip
                break
            }
        } catch { }
    }
    exit
}

# --- TEST CONNECTION ---
Write-Host "[TEST] Connecting to Sarah at $SarahIP`:$Port ..."
try {
    $ping = Invoke-WebRequest -Uri "http://${SarahIP}:${Port}/ping" -TimeoutSec 3 -EA Stop
    Write-Host "[OK]   Sarah online: $($ping.Content)"
} catch {
    Write-Host "[WARN] Sarah not responding. Checking connection..."
    Write-Host "       1. Ensure Dell 5490 is booted into S-OS"
    Write-Host "       2. Connect via Ethernet cable or USB-C"
    Write-Host "       3. Sarah's IP: $SarahIP (check with [N] in S-OS)"
    exit 1
}

# --- PUSH SPECIFIC FILE OR ALL .all FILES ---
$files = @()
if ($File -ne "") {
    $files = @(Join-Path $GENLEX_PATH $File)
} else {
    $files = Get-ChildItem -Path $GENLEX_PATH -Filter "*.all" | Select-Object -ExpandProperty FullName
    $files += Get-ChildItem -Path $GENLEX_PATH -Filter "*.cgl" | Select-Object -ExpandProperty FullName
}

$pushed = 0
$failed = 0

foreach ($f in $files) {
    $name = Split-Path $f -Leaf
    $content = Get-Content $f -Raw -Encoding UTF8
    try {
        $body = @{
            filename = $name
            content  = $content
        } | ConvertTo-Json
        $r = Invoke-WebRequest -Uri $SARAH_URL -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5
        Write-Host "[PUSH] $name -> $SarahIP`:$Port  [OK]"
        $pushed++
    } catch {
        Write-Host "[FAIL] $name -> $($_.Exception.Message)"
        $failed++
    }
}

Write-Host ""
Write-Host "[DONE] Pushed: $pushed  Failed: $failed"
Write-Host "       Sarah will hot-reload the scripts automatically."
Write-Host ""
