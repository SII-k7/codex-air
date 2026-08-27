#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$Action,
    [Alias("h", "-help")][switch]$Help
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Output "Usage: default.ps1 status|check|disable [-Help|--help]"
    Write-Output "Inspect or remove legacy global routing; Codex AIR remains explicit-only."
}

if ($Help) {
    Show-Usage
    exit 0
}
if ([string]::IsNullOrWhiteSpace($Action)) {
    Show-Usage
    exit 1
}
if (@("status", "check", "disable", "enable") -notcontains $Action) {
    Show-Usage
    exit 1
}
if ($Action -eq "enable") {
    throw "global default routing has been removed; invoke `$codex-air explicitly"
}

function Test-PathExists {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Test-Path -LiteralPath $Path)
}

function Test-ReparsePoint {
    param([Parameter(Mandatory = $true)]$Item)
    return (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Assert-SafeDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-PathExists $Path)) { return }
    $item = Get-Item -LiteralPath $Path -Force
    if (-not $item.PSIsContainer -or (Test-ReparsePoint $item)) { throw "unsafe directory" }
}

function Ensure-SafeDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-PathExists $Path) {
        Assert-SafeDirectory $Path
        return
    }
    $parent = Split-Path -Parent $Path
    if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $Path) { throw "cannot create directory" }
    Ensure-SafeDirectory $parent
    [System.IO.Directory]::CreateDirectory($Path) | Out-Null
}

function Get-OccurrenceCount {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Value
    )
    $count = 0
    $offset = 0
    $found = $Text.IndexOf($Value, $offset, [System.StringComparison]::Ordinal)
    while ($found -ge 0) {
        $count++
        $offset = $found + $Value.Length
        $found = $Text.IndexOf($Value, $offset, [System.StringComparison]::Ordinal)
    }
    return $count
}

function Write-Utf8Text {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding($false)))
}

$rawBase = $env:ORCHESTRATE_HOME
if ([string]::IsNullOrWhiteSpace($rawBase)) { $rawBase = [Environment]::GetFolderPath("UserProfile") }
if ([string]::IsNullOrWhiteSpace($rawBase) -or -not [System.IO.Path]::IsPathRooted($rawBase)) {
    throw "ORCHESTRATE_HOME must be an absolute path"
}
$baseDir = [System.IO.Path]::GetFullPath($rawBase)
if ($baseDir -eq [System.IO.Path]::GetPathRoot($baseDir)) { throw "refusing the filesystem root" }

$codexDir = Join-Path $baseDir ".codex"
$agentsPath = Join-Path $codexDir "AGENTS.md"
$backupRoot = Join-Path $codexDir "codex-air/default-routing-backups"

if (-not (Test-PathExists $baseDir)) {
    if ($Action -eq "disable") { Write-Output "Legacy default routing already disabled" }
    else { Write-Output "Codex AIR explicit-only routing: PASS" }
    exit 0
}
Assert-SafeDirectory $baseDir
if (Test-PathExists $codexDir) { Assert-SafeDirectory $codexDir }

if (Test-PathExists $agentsPath) {
    $agentsItem = Get-Item -LiteralPath $agentsPath -Force
    if ($agentsItem.PSIsContainer -or (Test-ReparsePoint $agentsItem)) {
        throw "global Codex instructions are unsafe"
    }
    $current = [string](Get-Content -LiteralPath $agentsPath -Raw)
}
else {
    $current = ""
}

$markerPairs = @(
    @("<!-- codex-air-default:start -->", "<!-- codex-air-default:end -->"),
    @("<!-- codex-prove-default:start -->", "<!-- codex-prove-default:end -->"),
    @("<!-- sol-control-default:start -->", "<!-- sol-control-default:end -->")
)
$activePairs = New-Object System.Collections.Generic.List[object]
foreach ($pair in $markerPairs) {
    $startCount = Get-OccurrenceCount $current $pair[0]
    $endCount = Get-OccurrenceCount $current $pair[1]
    if ($startCount -gt 0 -or $endCount -gt 0) {
        if ($startCount -ne 1 -or $endCount -ne 1) {
            throw "legacy default-routing markers are malformed or duplicated"
        }
        $activePairs.Add($pair)
    }
}

if ($activePairs.Count -eq 0) {
    if ($Action -eq "disable") { Write-Output "Legacy default routing already disabled" }
    else { Write-Output "Codex AIR explicit-only routing: PASS" }
    exit 0
}
if ($activePairs.Count -ne 1) { throw "legacy default-routing markers are malformed or duplicated" }
if ($Action -eq "status" -or $Action -eq "check") {
    throw "legacy Codex AIR global default routing is enabled; run powershell -File scripts/default.ps1 disable"
}

$start = [string]$activePairs[0][0]
$end = [string]$activePairs[0][1]
$begin = $current.IndexOf($start, [System.StringComparison]::Ordinal)
$endBegin = $current.IndexOf($end, $begin, [System.StringComparison]::Ordinal)
if ($endBegin -lt $begin) { throw "legacy default-routing markers are malformed or duplicated" }
$finish = $endBegin + $end.Length
$prefix = $current.Substring(0, $begin).TrimEnd([char[]]"`r`n")
$suffix = $current.Substring($finish).TrimStart([char[]]"`r`n")
if ($prefix -and $suffix) { $updated = $prefix + "`n`n" + $suffix + "`n" }
elseif ($prefix) { $updated = $prefix + "`n" }
elseif ($suffix) { $updated = $suffix + "`n" }
else { $updated = "" }

Ensure-SafeDirectory $codexDir
Ensure-SafeDirectory $backupRoot
$backupId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ") + "-" + $PID
$backupDir = Join-Path $backupRoot $backupId
if (Test-PathExists $backupDir) {
    $backupDir = Join-Path $backupRoot ($backupId + "-" + [Guid]::NewGuid().ToString("N"))
}
Ensure-SafeDirectory $backupDir
if (Test-PathExists $agentsPath) {
    Copy-Item -LiteralPath $agentsPath -Destination (Join-Path $backupDir "AGENTS.md")
}
else {
    Write-Utf8Text (Join-Path $backupDir "AGENTS.absent") ""
}

if ([string]::IsNullOrEmpty($updated)) {
    if (Test-PathExists $agentsPath) { Remove-Item -LiteralPath $agentsPath }
}
else {
    $temporary = Join-Path $codexDir (".AGENTS.md." + [Guid]::NewGuid().ToString("N"))
    try {
        Write-Utf8Text $temporary $updated
        if (Test-PathExists $agentsPath) {
            [System.IO.File]::Replace($temporary, $agentsPath, $null, $true)
        }
        else {
            [System.IO.File]::Move($temporary, $agentsPath)
        }
    }
    finally {
        if (Test-PathExists $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
}

Write-Output "Legacy default routing: disabled"
Write-Output "Codex AIR explicit-only routing: PASS"
Write-Output "Backup created: yes"
