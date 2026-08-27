#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$RequireCodex,
    [Alias("h", "-help")][switch]$Help
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Output "Usage: doctor.ps1 [-Json] [-RequireCodex] [-Help|--help]"
    Write-Output "Diagnose the source, installed bundle, routing, and Codex CLI without exposing local paths."
}

if ($Help) {
    Show-Usage
    exit 0
}

function Test-PathExists {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Test-Path -LiteralPath $Path)
}

function Test-ReparsePoint {
    param([Parameter(Mandatory = $true)]$Item)
    return (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Test-PlainFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-PathExists $Path)) { return $false }
    $item = Get-Item -LiteralPath $Path -Force
    return (-not $item.PSIsContainer -and -not (Test-ReparsePoint $item))
}

function Get-SafeText {
    param(
        [AllowEmptyString()][string]$Text,
        [string]$Fallback = "unknown",
        [int]$Limit = 160
    )
    $cleaned = [regex]::Replace([string]$Text, "[\x00-\x1f\x7f]+", " ").Trim()
    if ([string]::IsNullOrWhiteSpace($cleaned)) { return $Fallback }
    if ($cleaned.Length -gt $Limit) { return $cleaned.Substring(0, $Limit) }
    return $cleaned
}

function Get-StateMap {
    param([Parameter(Mandatory = $true)][string]$Path)
    $map = @{}
    foreach ($line in @(Get-Content -LiteralPath $Path)) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line -notmatch "^(?<key>[A-Za-z_][A-Za-z0-9_]*)=(?<value>.*)$") { throw "invalid state" }
        if ($map.ContainsKey($Matches.key)) { throw "duplicate state key" }
        $map[$Matches.key] = $Matches.value
    }
    return $map
}

function Get-MapValue {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Map,
        [Parameter(Mandatory = $true)][string]$Key,
        [string]$Fallback = "unknown"
    )
    if (-not $Map.ContainsKey($Key)) { return $Fallback }
    return [string]$Map[$Key]
}

function Get-AgentHeader {
    param([Parameter(Mandatory = $true)][string]$Path)
    $map = @{}
    foreach ($line in @(Get-Content -LiteralPath $Path)) {
        if ($line -match "^\s*developer_instructions\s*=") { break }
        if ($line -match '^\s*(?<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"(?<value>[^"\r\n]*)"\s*$') {
            $map[$Matches.key] = $Matches.value
        }
        elseif ($line -match '^\s*(?<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?<value>[0-9]+)\s*$') {
            $map[$Matches.key] = [int64]$Matches.value
        }
    }
    return $map
}

function Get-SimpleTomlAssignments {
    param([Parameter(Mandatory = $true)][string]$Path)
    $map = @{}
    $section = ""
    foreach ($line in @(Get-Content -LiteralPath $Path)) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("#")) { continue }
        if ($trimmed -match '^\[(?<section>[A-Za-z0-9_.-]+)\]$') {
            $section = $Matches.section
            continue
        }
        if ($trimmed -match '^(?<key>[A-Za-z_][A-Za-z0-9_-]*)\s*=\s*(?<value>[^#]*?)(?:\s+#.*)?$') {
            $map[($section + "." + $Matches.key)] = $Matches.value.Trim()
        }
    }
    return $map
}

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$releasePattern = "^[0-9A-Za-z][0-9A-Za-z.+-]{0,63}$"
$commitPattern = "^[0-9a-f]{40,64}$"

$rawBase = $env:ORCHESTRATE_HOME
if ([string]::IsNullOrWhiteSpace($rawBase)) { $rawBase = [Environment]::GetFolderPath("UserProfile") }
if ([string]::IsNullOrWhiteSpace($rawBase) -or -not [System.IO.Path]::IsPathRooted($rawBase)) {
    throw "ORCHESTRATE_HOME must be an absolute path"
}
$baseDir = [System.IO.Path]::GetFullPath($rawBase)
if ($baseDir -eq [System.IO.Path]::GetPathRoot($baseDir)) { throw "refusing the filesystem root" }
if (-not (Test-PathExists $baseDir)) { throw "ORCHESTRATE_HOME is missing" }
$baseItem = Get-Item -LiteralPath $baseDir -Force
if (-not $baseItem.PSIsContainer -or (Test-ReparsePoint $baseItem)) { throw "ORCHESTRATE_HOME is unsafe" }

$repoRoot = Split-Path -Parent $PSScriptRoot
$versionPath = Join-Path $repoRoot "VERSION"
$sourceRelease = "unknown"
if (Test-PlainFile $versionPath) {
    $candidate = (Get-Content -LiteralPath $versionPath -Raw).Trim()
    if ($candidate -match $releasePattern) { $sourceRelease = $candidate }
    else { $errors.Add("source VERSION is invalid") }
}
else {
    $errors.Add("source VERSION is unavailable")
}

$sourceCommit = "unknown"
$sourceDirty = $null
$gitCommand = Get-Command git -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -ne $gitCommand) {
    $commitOutput = @(& $gitCommand.Source -C $repoRoot rev-parse --verify HEAD 2>$null)
    if ($LASTEXITCODE -eq 0) {
        $candidate = (($commitOutput | ForEach-Object { [string]$_ }) -join "").Trim()
        if ($candidate -match $commitPattern) {
            $sourceCommit = $candidate
            $statusOutput = @(
                & $gitCommand.Source --no-optional-locks -C $repoRoot status --porcelain --untracked-files=normal 2>$null
            )
            if ($LASTEXITCODE -eq 0) { $sourceDirty = ($statusOutput.Count -gt 0) }
        }
    }
}

$statePath = Join-Path $baseDir ".codex/codex-air/install-state"
$stateVisible = Test-PlainFile $statePath
$state = @{}
if ($stateVisible) {
    try { $state = Get-StateMap $statePath }
    catch { $errors.Add("installed state is invalid") }
}
else {
    $errors.Add("installed state is missing or unsafe")
}
$stateFormat = Get-MapValue $state "version"
if ($state.Count -gt 0 -and $stateFormat -ne "7") { $errors.Add("installed state format is unsupported") }

$installedRelease = Get-MapValue $state "release_version"
if ($installedRelease -ne "unknown" -and $installedRelease -notmatch $releasePattern) {
    $warnings.Add("installed release metadata is invalid")
    $installedRelease = "unknown"
}
$installedCommit = Get-MapValue $state "source_commit"
if ($installedCommit -ne "unknown" -and $installedCommit -notmatch $commitPattern) {
    $warnings.Add("installed commit metadata is invalid")
    $installedCommit = "unknown"
}
$installedDirty = $null
$dirtyValue = Get-MapValue $state "source_dirty"
if ($dirtyValue -eq "true") { $installedDirty = $true }
elseif ($dirtyValue -eq "false") { $installedDirty = $false }
elseif ($dirtyValue -ne "unknown") { $warnings.Add("installed dirty-state metadata is invalid") }
if ($installedRelease -eq "unknown" -and $stateFormat -eq "7") {
    $warnings.Add("installed release metadata predates provenance reporting")
}
elseif ($sourceRelease -ne "unknown" -and $installedRelease -ne $sourceRelease) {
    $warnings.Add("installed release differs from this source checkout")
}
if ($installedDirty -eq $true) { $warnings.Add("installed bundle came from a dirty source checkout") }

$canonicalVisible = Test-PlainFile (Join-Path $baseDir ".agents/skills/codex-air/SKILL.md")
$compatibilityVisible = Test-PlainFile (Join-Path $baseDir ".agents/skills/codex-prove/SKILL.md")
if (-not $canonicalVisible -or -not $compatibilityVisible) {
    $errors.Add("one or more installed Skill entrypoints are missing or unsafe")
}

$expected = [ordered]@{
    "air-controller.toml" = [ordered]@{
        name = "air-controller"
        model = "gpt-5.6-sol"
        model_reasoning_effort = "xhigh"
        model_context_window = 272000
        model_auto_compact_token_limit = 244800
        service_tier = "default"
        sandbox_mode = "read-only"
    }
    "air-critical-controller.toml" = [ordered]@{
        name = "air-critical-controller"
        model = "gpt-5.6-sol"
        model_reasoning_effort = "xhigh"
        model_context_window = 272000
        model_auto_compact_token_limit = 244800
        service_tier = "default"
        sandbox_mode = "read-only"
    }
    "air-complex-worker.toml" = [ordered]@{
        name = "air-complex-worker"
        model = "gpt-5.6-luna"
        model_reasoning_effort = "max"
        model_context_window = 272000
        model_auto_compact_token_limit = 244800
        service_tier = "fast"
        sandbox_mode = "workspace-write"
    }
    "air-efficient-worker.toml" = [ordered]@{
        name = "air-efficient-worker"
        model = "gpt-5.6-luna"
        model_reasoning_effort = "max"
        model_context_window = 272000
        model_auto_compact_token_limit = 244800
        service_tier = "fast"
        sandbox_mode = "workspace-write"
    }
    "air-challenger.toml" = [ordered]@{
        name = "air-challenger"
        model = "gpt-5.6-sol"
        model_reasoning_effort = "xhigh"
        model_context_window = 272000
        model_auto_compact_token_limit = 244800
        service_tier = "default"
        sandbox_mode = "read-only"
    }
}
$agentVisibility = [ordered]@{}
$agentsOk = $true
foreach ($filename in $expected.Keys) {
    $agentPath = Join-Path (Join-Path $baseDir ".codex/agents") $filename
    $visible = Test-PlainFile $agentPath
    $profileMatches = $false
    if ($visible) {
        try {
            $actual = Get-AgentHeader $agentPath
            $profileMatches = $true
            foreach ($key in $expected[$filename].Keys) {
                if (-not $actual.ContainsKey($key) -or $actual[$key] -ne $expected[$filename][$key]) {
                    $profileMatches = $false
                    break
                }
            }
        }
        catch { $profileMatches = $false }
    }
    if (-not $visible -or -not $profileMatches) { $agentsOk = $false }
    $agentVisibility[$filename] = [ordered]@{ visible = $visible; profile_matches = $profileMatches }
}
if (-not $agentsOk) { $errors.Add("one or more installed agent profiles are missing, unsafe, or mismatched") }

$configurationOk = $true
$configPath = Join-Path $baseDir ".codex/config.toml"
if (Test-PathExists $configPath) {
    if (-not (Test-PlainFile $configPath)) {
        $errors.Add("Codex config is unsafe")
        $configurationOk = $false
    }
    else {
        try {
            $config = Get-SimpleTomlAssignments $configPath
            if ($config.ContainsKey("features.multi_agent") -and $config["features.multi_agent"] -eq "false") {
                $errors.Add("Codex config explicitly disables features.multi_agent")
                $configurationOk = $false
            }
            if ($config.ContainsKey("agents.enabled") -and $config["agents.enabled"] -eq "false") {
                $errors.Add("Codex config explicitly disables agents.enabled")
                $configurationOk = $false
            }
            if ($config.ContainsKey("agents.max_concurrent_threads_per_session")) {
                $limit = 0
                $parsed = [int]::TryParse(
                    $config["agents.max_concurrent_threads_per_session"],
                    [ref]$limit
                )
                if (-not $parsed -or $limit -lt 1) {
                    $errors.Add("Codex agent concurrency must be a positive integer")
                    $configurationOk = $false
                }
            }
        }
        catch {
            $errors.Add("Codex config is invalid")
            $configurationOk = $false
        }
    }
}

$explicitOnly = $true
$agentsInstructions = Join-Path $baseDir ".codex/AGENTS.md"
if (Test-PathExists $agentsInstructions) {
    if (-not (Test-PlainFile $agentsInstructions)) {
        $errors.Add("global Codex instructions are unsafe")
        $explicitOnly = $false
    }
    else {
        $instructions = Get-Content -LiteralPath $agentsInstructions -Raw
        foreach ($marker in @(
            "<!-- codex-air-default:start -->",
            "<!-- codex-air-default:end -->",
            "<!-- codex-prove-default:start -->",
            "<!-- codex-prove-default:end -->",
            "<!-- sol-control-default:start -->",
            "<!-- sol-control-default:end -->"
        )) {
            if ($instructions.Contains($marker)) {
                $errors.Add(
                    "legacy Codex AIR global default routing is enabled; " +
                    "run powershell -File scripts/default.ps1 disable"
                )
                $explicitOnly = $false
                break
            }
        }
    }
}

$codexAvailable = $false
$codexVersion = "unknown"
$codexCommand = Get-Command codex -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandType -eq "Application" -or $_.CommandType -eq "ExternalScript"
} | Select-Object -First 1
if ($null -ne $codexCommand) {
    $codexAvailable = $true
    try {
        $versionOutput = @(& $codexCommand.Source --version 2>&1)
        if ($LASTEXITCODE -eq 0) {
            $safeVersionOutput = Get-SafeText (($versionOutput | ForEach-Object { [string]$_ }) -join " ")
            $versionMatch = [regex]::Match(
                $safeVersionOutput,
                "(?<![0-9A-Za-z])(?<version>[0-9]+(?:\.[0-9]+){1,3}(?:[-+][0-9A-Za-z.-]+)?)(?![0-9A-Za-z])"
            )
            if ($versionMatch.Success) { $codexVersion = $versionMatch.Groups["version"].Value }
            else {
                $codexVersion = "unrecognized"
                $warnings.Add("Codex CLI returned an unrecognized version")
            }
        }
        else {
            $codexVersion = "version query failed"
            $warnings.Add("Codex CLI version query failed")
        }
    }
    catch {
        $codexVersion = "version query failed"
        $warnings.Add("Codex CLI version query failed")
    }
}
if ($RequireCodex -and -not $codexAvailable) { $errors.Add("codex is not available on PATH") }

$bundleOk = $canonicalVisible -and $compatibilityVisible -and $agentsOk
$report = [ordered]@{
    schema_version = 1
    status = if ($errors.Count -eq 0) { "pass" } else { "fail" }
    source = [ordered]@{ release_version = $sourceRelease; commit = $sourceCommit; dirty = $sourceDirty }
    installed = [ordered]@{
        state_visible = $stateVisible
        state_format = $stateFormat
        release_version = $installedRelease
        source_commit = $installedCommit
        source_dirty = $installedDirty
    }
    codex_cli = [ordered]@{ available = $codexAvailable; version = $codexVersion }
    bundle = [ordered]@{
        skills = [ordered]@{ canonical = $canonicalVisible; compatibility = $compatibilityVisible }
        agents = $agentVisibility
        all_visible_and_matching = $bundleOk
    }
    configuration = [ordered]@{ multi_agent_not_disabled = $configurationOk }
    routing = [ordered]@{ explicit_only = $explicitOnly }
    warnings = @($warnings)
    errors = @($errors)
}
$encoded = $report | ConvertTo-Json -Depth 8 -Compress

if ($Json) {
    Write-Output $encoded
}
else {
    Write-Output "Source version: $sourceRelease ($sourceCommit)"
    Write-Output "Installed version: $installedRelease ($installedCommit)"
    if ($codexAvailable) { Write-Output "Codex CLI: AVAILABLE ($codexVersion)" }
    else { Write-Output "Codex CLI: UNAVAILABLE" }
    Write-Output "Installed Skill and five agent profiles: $(if ($bundleOk) { 'PASS' } else { 'FAIL' })"
    Write-Output "Codex multi-agent configuration is not disabled: $(if ($configurationOk) { 'PASS' } else { 'FAIL' })"
    Write-Output "Codex AIR subagent context isolation: $(if ($bundleOk) { 'PASS' } else { 'FAIL' })"
    Write-Output "Codex AIR explicit-only routing: $(if ($explicitOnly) { 'PASS' } else { 'FAIL' })"
    foreach ($warning in $warnings) { Write-Output "Doctor warning: $warning" }
    foreach ($failure in $errors) { Write-Output "Doctor error: $failure" }
    Write-Output "Doctor JSON: $encoded"
    Write-Output "Doctor: $(if ($errors.Count -eq 0) { 'PASS' } else { 'FAIL' })"
    if ($errors.Count -eq 0) {
        Write-Output "Restart Codex, verify `$codex-air in /skills, then inspect agents with /agent."
        Write-Output (
            "Exact model entitlement, actual service tier, and runtime selection " +
            "require authoritative live launch telemetry."
        )
    }
}

if ($errors.Count -gt 0) { exit 1 }
exit 0
