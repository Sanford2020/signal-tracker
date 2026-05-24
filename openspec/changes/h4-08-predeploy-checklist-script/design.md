# Design

`scripts/predeploy-check.ps1` runs:

1. PowerShell parser checks for helper scripts.
2. `scripts/check-env-readiness.ps1`.
3. `scripts/validate-release.ps1`.

The script fails fast on nonzero exit codes.
