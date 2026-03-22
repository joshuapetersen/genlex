# Genlex Sovereign Profile
# Genesis Handshake Persistence
$LinearDir = "C:\Genlex_Linear"
$GridDir = "C:\Sumerian_Grid"
$FreqDir = "C:\Genlex_Frequency"

# Command Aliases
function Invoke-GenlexLinear { python "$LinearDir\all_engine.py" @args }
function Invoke-GenlexGrid { python "$GridDir\ggl_engine.py" @args }
function Invoke-GenlexFrequency { python "$FreqDir\gfl_engine.py" @args }

Set-Alias -Name gll -Value Invoke-GenlexLinear -Force
Set-Alias -Name ggl -Value Invoke-GenlexGrid -Force
Set-Alias -Name gfl -Value Invoke-GenlexFrequency -Force

# Standard Sovereign Aliases
Set-Alias -Name gl -Value gll -Force
Set-Alias -Name gg -Value ggl -Force
Set-Alias -Name gf -Value gfl -Force

Write-Output "Genlex Sovereign Interface Seated."
