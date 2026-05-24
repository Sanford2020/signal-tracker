param(
    [Parameter(Mandatory = $true)]
    [string] $BackupFile
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ResolvedBackup = Resolve-Path $BackupFile

Push-Location $RepoRoot
try {
    Get-Content -Raw -Encoding Byte $ResolvedBackup | docker compose exec -T db sh -c 'pg_restore --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
    Write-Host "Restore completed from $ResolvedBackup"
}
finally {
    Pop-Location
}
