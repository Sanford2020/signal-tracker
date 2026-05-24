$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = Join-Path $RepoRoot "backups"
$BackupFile = Join-Path $BackupDir "signal-tracker-$Timestamp.dump"

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

Push-Location $RepoRoot
try {
    docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > $BackupFile
    Write-Host "Backup written to $BackupFile"
}
finally {
    Pop-Location
}
