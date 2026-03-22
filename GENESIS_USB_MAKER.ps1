# GENESIS_USB_MAKER.ps1
# Creates a bootable UEFI USB drive for the Dell 5490 directly using diskpart
# Architect: Joshua Petersen
# Run as Administrator

Write-Host "[ GENESIS ] Scanning for USB drives..." -ForegroundColor Cyan

# List all removable disks
$disks = Get-Disk | Where-Object { $_.BusType -eq 'USB' }

if ($disks.Count -eq 0) {
    Write-Host "[ ERROR ] No USB drive found. Plug in the USB and run again." -ForegroundColor Red
    exit 1
}

Write-Host "[ FOUND ] The following USB drives were detected:" -ForegroundColor Green
$disks | ForEach-Object { Write-Host "  Disk $($_.Number): $($_.FriendlyName) [$([math]::Round($_.Size / 1GB, 1)) GB]" }

$diskNum = Read-Host "Enter the Disk NUMBER to use as the Genesis USB"

Write-Host "[ WARNING ] ALL DATA on Disk $diskNum WILL BE ERASED." -ForegroundColor Red
$confirm = Read-Host "Type YES to continue"

if ($confirm -ne "YES") {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host "[ ACTION ] Formatting Disk $diskNum as GPT FAT32 UEFI boot disk..." -ForegroundColor Cyan

# Use diskpart to create GPT + FAT32 ESP
$diskpartScript = @"
select disk $diskNum
clean
convert mbr
create partition primary size=512
select partition 1
format fs=fat32 quick label=GENESIS
assign letter=G
active
exit
"@

$diskpartScript | diskpart

Start-Sleep -Seconds 2

# Verify drive G: is accessible
if (-not (Test-Path "G:\")) {
    Write-Host "[ ERROR ] Drive G: not accessible after format. Try running as Administrator." -ForegroundColor Red
    exit 1
}

Write-Host "[ ACTION ] Copying BOOTX64.EFI to G:\EFI\BOOT\" -ForegroundColor Cyan

New-Item -Path "G:\EFI\BOOT" -ItemType Directory -Force | Out-Null
Copy-Item -Path "C:\Genlex_Linear\BOOTX64.EFI" -Destination "G:\EFI\BOOT\BOOTX64.EFI" -Force

# Copy support scripts
Copy-Item -Path "C:\Genlex_Linear\all_engine.py" -Destination "G:\" -Force
Copy-Item -Path "C:\Genlex_Linear\genlex_mapping.csv" -Destination "G:\" -Force

Write-Host ""
Write-Host "[ GENESIS ] USB IS READY." -ForegroundColor Green
Write-Host "  -> Plug into the Dell 5490 and boot." -ForegroundColor White
Write-Host "  -> Press W to Wipe SSD, then I to Seed Genesis." -ForegroundColor White
Write-Host "  -> Reboot, select GENESIS from F12 boot menu." -ForegroundColor White
