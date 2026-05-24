param(
    [Parameter(Mandatory = $false)]
    [string] $EnvFile = ".env.production",

    [Parameter(Mandatory = $false)]
    [ValidateSet("development", "production")]
    [string] $Mode = "production"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,
        [Parameter(Mandatory = $true)]
        [scriptblock] $Command
    )

    Write-Host ""
    Write-Host "==> $Name"
    $global:LASTEXITCODE = 0
    & $Command
    if ($global:LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $global:LASTEXITCODE"
    }
}

Push-Location $RepoRoot
try {
    Invoke-Step "PowerShell script parser check" {
        $files = @(
            "scripts\validate-release.ps1",
            "scripts\backup-postgres.ps1",
            "scripts\restore-postgres.ps1",
            "scripts\smoke-staging.ps1",
            "scripts\check-env-readiness.ps1",
            "scripts\predeploy-check.ps1"
        )
        foreach ($file in $files) {
            $errors = $null
            [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $file), [ref]$null, [ref]$errors) | Out-Null
            if ($errors.Count -gt 0) {
                $errors | ForEach-Object { Write-Error $_ }
                exit 1
            }
            Write-Host "Parsed $file"
        }
    }

    Invoke-Step "Environment readiness" {
        powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile $EnvFile -Mode $Mode
    }

    Invoke-Step "Release validation" {
        powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
    }

    Write-Host ""
    Write-Host "Predeploy check passed."
}
finally {
    Pop-Location
}
