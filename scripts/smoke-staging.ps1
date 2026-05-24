param(
    [Parameter(Mandatory = $true)]
    [string] $ApiBaseUrl,

    [Parameter(Mandatory = $false)]
    [string] $WebBaseUrl,

    [Parameter(Mandatory = $false)]
    [string] $AdminApiKey
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Join-Url {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Base,
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    return $Base.TrimEnd("/") + "/" + $Path.TrimStart("/")
}

Write-Host "==> Backend health"
$healthUrl = Join-Url -Base $ApiBaseUrl -Path "/api/v1/health"
$healthResponse = Invoke-WebRequest -Uri $healthUrl -Method GET
$health = $healthResponse.Content | ConvertFrom-Json

if ($health.status -ne "ok") {
    throw "Unexpected health status: $($health.status)"
}

if (-not $healthResponse.Headers["X-Request-Id"]) {
    throw "Missing X-Request-Id header from backend health response."
}

Write-Host "Backend OK: $($health.service) $($health.version) [$($health.environment)]"
Write-Host "Request id: $($healthResponse.Headers["X-Request-Id"])"

Write-Host ""
Write-Host "==> Backend readiness"
$readyUrl = Join-Url -Base $ApiBaseUrl -Path "/api/v1/ready"
$readyResponse = Invoke-WebRequest -Uri $readyUrl -Method GET
$ready = $readyResponse.Content | ConvertFrom-Json
if ($ready.status -ne "ok" -or $ready.database -ne "ok") {
    throw "Unexpected readiness response."
}
Write-Host "Readiness OK: database $($ready.database)"

Write-Host ""
Write-Host "==> Bootstrap guard"
$bootstrapUrl = Join-Url -Base $ApiBaseUrl -Path "/api/v1/auth/bootstrap"
$bootstrapBody = @{
    email = "smoke@example.com"
    name = "Smoke Test"
    workspace_name = "Smoke Test Workspace"
} | ConvertTo-Json

try {
    Invoke-WebRequest -Uri $bootstrapUrl -Method POST -ContentType "application/json" -Body $bootstrapBody | Out-Null
    if (-not $AdminApiKey) {
        throw "Bootstrap unexpectedly succeeded without X-Admin-Secret."
    }
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -ne 401) {
        throw
    }
    Write-Host "Bootstrap guard OK: missing secret returns 401."
}

if ($AdminApiKey) {
    $headers = @{ "X-Admin-Secret" = $AdminApiKey }
    $allowed = Invoke-WebRequest -Uri $bootstrapUrl -Method POST -Headers $headers -ContentType "application/json" -Body $bootstrapBody
    if ($allowed.StatusCode -lt 200 -or $allowed.StatusCode -ge 300) {
        throw "Bootstrap with admin secret failed: $($allowed.StatusCode)"
    }
    $bootstrap = $allowed.Content | ConvertFrom-Json
    $workspaceId = $bootstrap.data.workspace.id
    $userEmail = $bootstrap.data.user.email
    $userToken = $bootstrap.data.access_token
    Write-Host "Bootstrap with admin secret OK."

    Write-Host ""
    Write-Host "==> Workspace member guard"
    $membersUrl = Join-Url -Base $ApiBaseUrl -Path "/api/v1/workspaces/$workspaceId/members"
    $memberHeaders = @{
        "X-User-Email" = $userEmail
        "X-User-Token" = $userToken
    }
    $members = Invoke-WebRequest -Uri $membersUrl -Method GET -Headers $memberHeaders
    if ($members.StatusCode -lt 200 -or $members.StatusCode -ge 300) {
        throw "Workspace member check failed: $($members.StatusCode)"
    }
    Write-Host "Workspace member guard OK."
}

if ($WebBaseUrl) {
    Write-Host ""
    Write-Host "==> Frontend"
    $webResponse = Invoke-WebRequest -Uri $WebBaseUrl -Method GET
    if ($webResponse.StatusCode -lt 200 -or $webResponse.StatusCode -ge 300) {
        throw "Frontend returned unexpected status: $($webResponse.StatusCode)"
    }
    Write-Host "Frontend OK: $WebBaseUrl"
}

Write-Host ""
Write-Host "Hosted staging smoke test passed."
