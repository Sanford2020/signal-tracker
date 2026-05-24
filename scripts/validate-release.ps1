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
    Invoke-Step "Docker Compose config" {
        docker compose config | Out-Host
    }

    Invoke-Step "Backend tests" {
        pytest backend\tests -q
    }

    Invoke-Step "Frontend type-check" {
        Push-Location apps\web
        try {
            npm run type-check
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step "Frontend production build" {
        Push-Location apps\web
        try {
            npm run build
        }
        finally {
            Pop-Location
        }
    }

    Write-Host ""
    Write-Host "Release validation passed."
}
finally {
    Pop-Location
}
