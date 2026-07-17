param(
    [switch]$InstallSoul
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$HermesHomeDir = if ($env:HERMES_HOME) {
    $env:HERMES_HOME
} elseif ($env:LOCALAPPDATA) {
    Join-Path $env:LOCALAPPDATA "hermes"
} else {
    Join-Path $HOME ".hermes"
}

if (-not (Get-Command hermes -ErrorAction SilentlyContinue)) {
    throw "Hermes is not installed or is not on PATH. Install/configure Hermes first."
}

$SkillsTarget = Join-Path $HermesHomeDir "skills\flyin"
$BundlesTarget = Join-Path $HermesHomeDir "skill-bundles"
$MemoriesTarget = Join-Path $HermesHomeDir "memories"
New-Item -ItemType Directory -Force -Path $SkillsTarget, $BundlesTarget, $MemoriesTarget | Out-Null

# Native Windows copies project-owned skills because symlinks may require elevated privileges.
Copy-Item -Recurse -Force (Join-Path $Root ".agents\skills\*") $SkillsTarget
Copy-Item -Force (Join-Path $Root ".agents\skill-bundles\*.yaml") $BundlesTarget

$MemoryFile = Join-Path $MemoriesTarget "MEMORY.md"
if (-not (Test-Path $MemoryFile)) {
    Copy-Item (Join-Path $Root "hermes\MEMORY.seed.md") $MemoryFile
    Write-Host "Seeded MEMORY.md"
} else {
    Write-Host "Existing MEMORY.md preserved; merge hermes/MEMORY.seed.md manually if useful."
}

$UserFile = Join-Path $MemoriesTarget "USER.md"
if (-not (Test-Path $UserFile)) {
    Copy-Item (Join-Path $Root "hermes\USER.seed.md") $UserFile
    Write-Host "Seeded USER.md"
} else {
    Write-Host "Existing USER.md preserved; merge hermes/USER.seed.md manually if useful."
}

$SoulFile = Join-Path $HermesHomeDir "SOUL.md"
if ($InstallSoul) {
    if (Test-Path $SoulFile) {
        $Timestamp = Get-Date -Format "yyyyMMddHHmmss"
        $Backup = "$SoulFile.backup.$Timestamp"
        Copy-Item $SoulFile $Backup
        Write-Host "Backed up existing SOUL.md to $Backup"
    }
    Copy-Item (Join-Path $Root "hermes\SOUL.flyin.md") $SoulFile
    Write-Host "Installed Fly-In SOUL.md globally for this Hermes home."
} elseif (Test-Path $SoulFile) {
    Write-Host "Existing SOUL.md preserved. Optional template: hermes/SOUL.flyin.md"
} else {
    Write-Host "SOUL.md not changed. Rerun with -InstallSoul after reviewing the template."
}

Write-Host "Installing/enabling official Ponytail plugin..."
& hermes plugins install DietrichGebert/ponytail --enable

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    $Python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $Python) {
    throw "Python is required to validate the context package."
}

if ($Python.Name -eq "py.exe" -or $Python.Name -eq "py") {
    & $Python.Source -3 (Join-Path $Root "scripts\validate-context.py")
} else {
    & $Python.Source (Join-Path $Root "scripts\validate-context.py")
}

Write-Host ""
Write-Host "Setup complete. Restart Hermes, open it from $Root, and use docs/prompts/FIRST_SESSION.md."
