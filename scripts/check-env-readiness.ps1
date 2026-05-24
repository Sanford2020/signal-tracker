param(
    [Parameter(Mandatory = $false)]
    [string] $EnvFile = ".env",

    [Parameter(Mandatory = $false)]
    [ValidateSet("development", "production")]
    [string] $Mode = "production"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot
$EnvPath = Join-Path $RepoRoot $EnvFile

if (-not (Test-Path $EnvPath)) {
    throw "Env file not found: $EnvPath"
}

$values = @{}
Get-Content $EnvPath | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        return
    }
    $parts = $line.Split("=", 2)
    if ($parts.Count -eq 2) {
        $values[$parts[0].Trim()] = $parts[1].Trim()
    }
}

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Require-Key {
    param([string] $Key)
    if (-not $values.ContainsKey($Key) -or [string]::IsNullOrWhiteSpace($values[$Key])) {
        $errors.Add("$Key is required.")
        return
    }
    if ($values[$Key] -match "<[^>]+>" -or $values[$Key] -match "CHANGE_ME") {
        $errors.Add("$Key still contains a placeholder value.")
    }
}

@(
    "APP_ENV",
    "APP_NAME",
    "APP_VERSION",
    "DATABASE_URL",
    "REDIS_URL",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "ALLOWED_ORIGINS",
    "NEXT_PUBLIC_API_BASE_URL"
) | ForEach-Object { Require-Key $_ }

if ($Mode -eq "production") {
    Require-Key "ADMIN_API_KEY"

    if ($values.ContainsKey("APP_ENV") -and $values["APP_ENV"] -ne "production") {
        $errors.Add("APP_ENV must be production for production readiness checks.")
    }

    if ($values.ContainsKey("DATABASE_URL") -and $values["DATABASE_URL"] -match "signal_tracker:signal_tracker") {
        $errors.Add("DATABASE_URL uses default local credentials.")
    }

    if ($values.ContainsKey("ALLOWED_ORIGINS")) {
        if ($values["ALLOWED_ORIGINS"] -eq "*") {
            $errors.Add("ALLOWED_ORIGINS must not be '*'.")
        }
        if ($values["ALLOWED_ORIGINS"] -match "localhost|127\.0\.0\.1") {
            $warnings.Add("ALLOWED_ORIGINS contains local origins.")
        }
    }

    if ($values.ContainsKey("NEXT_PUBLIC_API_BASE_URL") -and $values["NEXT_PUBLIC_API_BASE_URL"] -match "localhost|127\.0\.0\.1") {
        $errors.Add("NEXT_PUBLIC_API_BASE_URL points to a local URL.")
    }

    if ($values.ContainsKey("AI_EXTRACTION_MODE") -and $values["AI_EXTRACTION_MODE"] -ne "mock" -and -not $values["AI_API_KEY"]) {
        $errors.Add("AI_API_KEY is required when AI_EXTRACTION_MODE is not mock.")
    }
}

if ($warnings.Count -gt 0) {
    Write-Host "Warnings:"
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ""
}

if ($errors.Count -gt 0) {
    Write-Host "Errors:"
    $errors | ForEach-Object { Write-Host "- $_" }
    throw "Environment readiness check failed with $($errors.Count) error(s)."
}

Write-Host "Environment readiness check passed for $Mode using $EnvFile."
