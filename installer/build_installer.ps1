# PowerShell helper to compile the Inno Setup script if Inno Setup is installed.
# Usage: Run this in PowerShell (as admin if installing to Program Files):
#   cd ./installer
#   .\build_installer.ps1

$script = Join-Path $PSScriptRoot 'JournalTherapyCat.iss'
# Try to locate ISCC (Inno Setup Compiler)
$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $iscc) {
    Write-Host "Inno Setup compiler (iscc) not found on PATH."
    Write-Host "Download and install Inno Setup from https://jrsoftware.org/ then re-run this script."
    exit 1
}

Write-Host "Found iscc at: $($iscc.Path)"
& $iscc.Path $script
if ($LASTEXITCODE -eq 0) {
    Write-Host "Installer built successfully. Output is in the same folder as the script (OutputBaseFilename in .iss)."
} else {
    Write-Host "Compiler returned code $LASTEXITCODE. Check the Inno Setup output above for details."
}
