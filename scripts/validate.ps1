#requires -Version 5.1
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

function Assert-Condition {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

function Get-Text {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Assert-Regex {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if ($Text -notmatch $Pattern) { throw $Message }
}

function Get-Frontmatter {
    param([Parameter(Mandatory = $true)][string]$Path)
    $lines = [System.IO.File]::ReadAllLines($Path, [System.Text.Encoding]::UTF8)
    Assert-Condition ($lines.Count -ge 4 -and $lines[0] -eq "---") "invalid Skill frontmatter opener"
    $closing = -1
    for ($index = 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -eq "---") { $closing = $index; break }
    }
    Assert-Condition ($closing -gt 1) "invalid Skill frontmatter closer"
    $result = @{}
    for ($index = 1; $index -lt $closing; $index++) {
        if ([string]::IsNullOrWhiteSpace($lines[$index])) { continue }
        Assert-Condition ($lines[$index] -match "^(?<key>[a-z_]+):\s*(?<value>.+)$") "invalid Skill frontmatter line"
        Assert-Condition (-not $result.ContainsKey($Matches.key)) "duplicate Skill frontmatter key"
        $result[$Matches.key] = $Matches.value.Trim().Trim('"')
    }
    Assert-Condition ($result.Count -eq 2 -and $result.ContainsKey("name") -and $result.ContainsKey("description")) "Skill frontmatter must contain only name and description"
    return $result
}

$requiredFiles = @(
    ".agents/skills/codex-prove/SKILL.md",
    ".agents/skills/codex-prove/agents/openai.yaml",
    ".agents/skills/codex-air/references/orchestration.md",
    ".agents/skills/codex-air/references/runtime-notes.md",
    ".agents/skills/codex-air/scripts/persist-visible-candidate.sh",
    ".agents/skills/codex-air/SKILL.md",
    ".agents/skills/codex-air/agents/openai.yaml",
    ".agents/skills/codex-air/assets/icon-small.svg",
    ".agents/skills/codex-air/assets/icon-large.svg",
    ".codex/agents/air-controller.toml",
    ".codex/agents/air-critical-controller.toml",
    ".codex/agents/air-complex-worker.toml",
    ".codex/agents/air-efficient-worker.toml",
    ".codex/agents/air-challenger.toml",
    "scripts/install.sh",
    "scripts/validate.sh",
    "scripts/uninstall.sh",
    "scripts/install.ps1",
    "scripts/validate.ps1",
    "scripts/uninstall.ps1",
    "scripts/doctor.ps1",
    "scripts/default.ps1",
    "scripts/test.sh",
    "scripts/doctor.sh",
    "scripts/default.sh",
    "scripts/benchmark_ab.py",
    "scripts/microbench.py",
    "README.md",
    "README.zh-CN.md",
    "README.en.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/pull_request_template.md",
    "tests/windows-lifecycle.ps1",
    "tests/fixtures/v100-ab-benchmark.json",
    "tests/fixtures/deepswe-v11-ab.json",
    "tests/fixtures/microbench-v1.json",
    "tests/fixtures/microbench-screen-20260827.json",
    "tests/deepswe-v11-ab.md",
    "tests/deepswe-v11-microbench.md",
    "tests/v100-ab-benchmark.md",
    "tests/v100-live-smoke.md",
    "tests/test_v100_benchmark.py",
    "tests/test_v100_evidence_control.py",
    "tests/test_hard_benchmark_protocol.py",
    "tests/test_microbench.py",
    "tests/test_default_routing.py",
    "CODEX_AIR_V1_IMPLEMENTATION_REPORT.md",
    "docs/ubuntu-cli-install.md",
    "docs/prompt-recipes.md",
    ".github/workflows/windows-validation.yml",
    ".github/workflows/posix-validation.yml",
    "NOTICE",
    "LICENSE"
)
foreach ($relative in $requiredFiles) {
    $path = Join-Path $repoRoot $relative
    Assert-Condition (Test-Path -LiteralPath $path -PathType Leaf) "missing required file: $relative"
}

foreach ($relative in @(
    ".agents/skills/sol-luna",
    ".agents/skills/orchestrate-sol-luna",
    ".agents/skills/sol-control",
    ".codex/agents/prove-controller.toml",
    ".codex/agents/prove-critical-controller.toml",
    ".codex/agents/prove-complex-worker.toml",
    ".codex/agents/prove-efficient-worker.toml",
    ".codex/agents/prove-challenger.toml",
    ".codex/agents/sol-controller.toml",
    ".codex/agents/terra-high-worker.toml",
    ".codex/agents/luna-max-worker.toml",
    ".codex/agents/sol-planner.toml"
)) {
    Assert-Condition (-not (Test-Path -LiteralPath (Join-Path $repoRoot $relative))) "legacy runtime source remains: $relative"
}

$skillPath = Join-Path $repoRoot ".agents/skills/codex-air/SKILL.md"
$skillMeta = Get-Frontmatter $skillPath
Assert-Condition ($skillMeta.name -eq "codex-air") "canonical Skill name is invalid"
Assert-Condition ($skillMeta.description.Contains('$codex-air') -and $skillMeta.description.Contains('explicitly invokes')) "canonical Skill description is invalid"

$compatSkillPath = Join-Path $repoRoot ".agents/skills/codex-prove/SKILL.md"
$compatMeta = Get-Frontmatter $compatSkillPath
Assert-Condition ($compatMeta.name -eq "codex-prove" -and $compatMeta.description.Contains('$codex-prove') -and $compatMeta.description.Contains('$codex-air')) "compatibility Skill frontmatter is invalid"

$skillText = Get-Text $skillPath
$contractText = Get-Text (Join-Path $repoRoot ".agents/skills/codex-air/references/orchestration.md")
$runtimeText = Get-Text (Join-Path $repoRoot ".agents/skills/codex-air/references/runtime-notes.md")
$combined = $skillText + "`n" + $contractText + "`n" + $runtimeText
$normalizedCombined = [regex]::Replace($combined, '\s+', ' ')
foreach ($marker in @(
    "Planning", "Routing", "Ownership", "Verification", "Evidence",
    "Requirement ID", "one owner", "Native Nested", "Compatibility",
    "Sol xhigh", "Fast requested", "actual tier", "Terra is forbidden", "Mode: Single Executor",
    "deterministic candidate persistence", "persist-visible-candidate.sh", "VISIBLE_CANDIDATE", "Final file SHA256",
    "hard wall time", "PYTHONDONTWRITEBYTECODE=1", "evaluation isolation",
    'fork_turns="none"', "Fail Closed", "PASS | FIX | BLOCKED",
    "Status: PASS | REPLAN_NEEDED | BLOCKED", "one Sol semantic controller",
    "verify the verifier", "result-only", "remaining budget", "Run envelope", "Critical In-Place",
    "exact-relative-path", "Direct", "Controlled AIR",
    "air-controller", "air-critical-controller", "air-complex-worker", "air-efficient-worker", "air-challenger"
)) {
    $normalizedMarker = [regex]::Replace($marker, '\s+', ' ')
    Assert-Condition ($normalizedCombined.IndexOf($normalizedMarker, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) "orchestration contract is missing: $marker"
}

$openaiText = Get-Text (Join-Path $repoRoot ".agents/skills/codex-air/agents/openai.yaml")
foreach ($pattern in @(
    '(?m)^interface:\s*$',
    '(?m)^\s{2}display_name:\s*"Codex AIR"\s*$',
    '(?m)^\s{2}short_description:\s*"[^"\r\n]{25,64}"\s*$',
    '(?m)^\s{2}icon_small:\s*"\./assets/icon-small\.svg"\s*$',
    '(?m)^\s{2}icon_large:\s*"\./assets/icon-large\.svg"\s*$',
    '(?m)^\s{2}brand_color:\s*"#0F766E"\s*$',
    '(?m)^\s{2}default_prompt:\s*".*\$codex-air.*"\s*$',
    '(?m)^policy:\s*$',
    '(?m)^\s{2}allow_implicit_invocation:\s*false\s*$'
)) {
    Assert-Regex $openaiText $pattern "canonical openai.yaml is invalid"
}
foreach ($iconName in @("icon-small.svg", "icon-large.svg")) {
    $iconPath = Join-Path $repoRoot ".agents/skills/codex-air/assets/$iconName"
    Assert-Condition ((Get-Item -LiteralPath $iconPath).Length -lt 5000) "Skill icon is unexpectedly large"
    Assert-Regex (Get-Text $iconPath) '<svg' "Skill icon is not SVG"
}

$compatText = Get-Text (Join-Path $repoRoot ".agents/skills/codex-prove/agents/openai.yaml")
Assert-Regex $compatText '\$codex-prove' "compatibility openai.yaml misses old invocation"
Assert-Regex $compatText '\$codex-air' "compatibility openai.yaml misses canonical invocation"
Assert-Regex $compatText '(?m)^\s{2}allow_implicit_invocation:\s*false\s*$' "compatibility openai.yaml permits implicit invocation"

$agentExpectations = @(
    @(".codex/agents/air-controller.toml", "air-controller", "gpt-5.6-sol", "xhigh", "read-only", $false),
    @(".codex/agents/air-critical-controller.toml", "air-critical-controller", "gpt-5.6-sol", "xhigh", "read-only", $false),
    @(".codex/agents/air-complex-worker.toml", "air-complex-worker", "gpt-5.6-luna", "max", "workspace-write", $true),
    @(".codex/agents/air-efficient-worker.toml", "air-efficient-worker", "gpt-5.6-luna", "max", "workspace-write", $true),
    @(".codex/agents/air-challenger.toml", "air-challenger", "gpt-5.6-sol", "xhigh", "read-only", $true)
)
$agentFiles = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot ".codex/agents") -File -Filter "*.toml")
Assert-Condition ($agentFiles.Count -eq $agentExpectations.Count) "agent directory contains an unexpected profile"
foreach ($agentFile in $agentFiles) {
    Assert-Condition (-not (Get-Text $agentFile.FullName).Contains('model = "gpt-5.6-terra"')) "Terra is forbidden in AIR agent profiles"
}
foreach ($expectation in $agentExpectations) {
    $text = Get-Text (Join-Path $repoRoot $expectation[0])
    Assert-Regex $text ('(?m)^name\s*=\s*"' + [regex]::Escape($expectation[1]) + '"\s*$') "agent name is invalid"
    Assert-Regex $text ('(?m)^model\s*=\s*"' + [regex]::Escape($expectation[2]) + '"\s*$') "agent model is invalid"
    Assert-Regex $text ('(?m)^model_reasoning_effort\s*=\s*"' + [regex]::Escape($expectation[3]) + '"\s*$') "agent reasoning effort is invalid"
    Assert-Regex $text '(?m)^model_context_window\s*=\s*272000\s*$' "agent must pin the v1.2 profile context window"
    Assert-Regex $text '(?m)^model_auto_compact_token_limit\s*=\s*244800\s*$' "agent must pin the v1.2 profile auto-compact limit"
    Assert-Regex $text ('(?m)^sandbox_mode\s*=\s*"' + [regex]::Escape($expectation[4]) + '"\s*$') "agent sandbox is invalid"
    Assert-Regex $text '(?s)developer_instructions\s*=\s*""".+"""' "agent instructions are missing"
    if ($expectation[5]) { Assert-Regex $text '(?is)(?:do not|never) .*?(spawn|create).*?subagent' "execution agent can create subagents" }
}
$efficientText = Get-Text (Join-Path $repoRoot ".codex/agents/air-efficient-worker.toml")
$complexText = Get-Text (Join-Path $repoRoot ".codex/agents/air-complex-worker.toml")
foreach ($entry in @(@($efficientText, "efficient"), @($complexText, "complex"))) {
    Assert-Regex $entry[0] '(?m)^service_tier\s*=\s*"fast"\s*$' "$($entry[1]) agent fast service tier is missing"
    Assert-Regex $entry[0] '(?ms)^\[features\]\s*.*?^fast_mode\s*=\s*true\s*$' "$($entry[1]) agent fast feature is missing"
}
foreach ($entry in @(@($efficientText, "efficient"), @($complexText, "complex"))) {
    foreach ($pattern in @(
        '(?m)^model_verbosity\s*=\s*"low"\s*$',
        '(?m)^model_reasoning_summary\s*=\s*"none"\s*$',
        '(?m)^tool_output_token_limit\s*=\s*4000\s*$',
        '(?m)^personality\s*=\s*"none"\s*$'
    )) {
        Assert-Regex $entry[0] $pattern "$($entry[1]) agent latency configuration is incomplete"
    }
}
Assert-Regex $efficientText '(?ms)^\[agents\]\s*.*?^enabled\s*=\s*false\s*$' "efficient agent nesting guard is missing"
Assert-Regex $complexText '(?ms)^\[agents\]\s*.*?^enabled\s*=\s*false\s*$' "complex agent nesting guard is missing"
foreach ($relative in @(
    ".codex/agents/air-controller.toml",
    ".codex/agents/air-critical-controller.toml",
    ".codex/agents/air-challenger.toml"
)) {
    $text = Get-Text (Join-Path $repoRoot $relative)
    Assert-Regex $text '(?m)^service_tier\s*=\s*"default"\s*$' "Sol agent must pin the Standard service tier"
}

foreach ($script in @(
    "scripts/install.ps1",
    "scripts/validate.ps1",
    "scripts/uninstall.ps1",
    "scripts/doctor.ps1",
    "scripts/default.ps1",
    "tests/windows-lifecycle.ps1"
)) {
    $path = Join-Path $repoRoot $script
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
    Assert-Condition ($errors.Count -eq 0) "PowerShell syntax failed: $script"
}

$benchmark = Get-Content -LiteralPath (Join-Path $repoRoot "tests/fixtures/v100-ab-benchmark.json") -Raw | ConvertFrom-Json
Assert-Condition ($null -ne $benchmark) "benchmark fixture is invalid"
$hardBenchmark = Get-Content -LiteralPath (Join-Path $repoRoot "tests/fixtures/deepswe-v11-ab.json") -Raw | ConvertFrom-Json
Assert-Condition ($hardBenchmark.status -eq "FROZEN_NOT_RUN" -and $hardBenchmark.source.task_count -eq 113) "hard benchmark fixture is invalid"
Assert-Condition ($hardBenchmark.evidence_class -eq "prospective_protocol_only" -and $hardBenchmark.architecture_version -eq "1.2") "hard benchmark evidence boundary is invalid"
Assert-Condition ($hardBenchmark.arms.direct.Contains("sol / xhigh / default") -and $hardBenchmark.arms.air.Contains("Fast requested")) "hard benchmark routing is stale"
Assert-Condition ($hardBenchmark.arms.terra -eq "zero calls and zero tokens") "hard benchmark Terra boundary is invalid"
Assert-Condition ($hardBenchmark.frontier_difficulty_evidence.gpt_5_6_sol_max_percent -lt 100) "hard benchmark does not separate Sol max"
Assert-Condition ($hardBenchmark.frontier_difficulty_evidence.claude_fable_5_max_percent -lt 100) "hard benchmark does not separate Fable 5 max"
$microbench = Get-Content -LiteralPath (Join-Path $repoRoot "tests/fixtures/microbench-v1.json") -Raw | ConvertFrom-Json
Assert-Condition ($microbench.evidence_class -eq "historical_direct_replay_development_gate") "microbenchmark evidence class is invalid"
Assert-Condition ($microbench.tasks.Count -eq 4 -and $microbench.stages.Count -eq 2) "microbenchmark task stages are invalid"
Assert-Condition ($microbench.budget.screen_credit_cap -eq 70 -and $microbench.budget.cumulative_credit_hard_cap -eq 220) "microbenchmark credit caps are invalid"
Assert-Condition ($microbench.pricing.models.'gpt-5.6-luna'.requested_tier_multiplier -eq 2.5) "microbenchmark Luna Fast price is invalid"

$credentialPatterns = @(
    'AKIA[0-9A-Z]{16}',
    '-----BEGIN [A-Z0-9 ]+ PRIVATE KEY-----',
    'gh[pousr]_[A-Za-z0-9_]{20,}',
    'sk-[A-Za-z0-9]{20,}',
    'xox[baprs]-[A-Za-z0-9-]{20,}'
)
Get-ChildItem -LiteralPath $repoRoot -File -Recurse -Force | Where-Object {
    $_.FullName -notmatch '[\\/]\.git[\\/]' -and $_.FullName -notmatch '[\\/]__pycache__[\\/]'
} | ForEach-Object {
    try { $text = Get-Text $_.FullName } catch { return }
    foreach ($pattern in $credentialPatterns) {
        if ($text -match $pattern) { throw "possible credential detected" }
    }
    if ($text.Length -gt 0 -and -not $text.EndsWith("`n")) { throw "missing final newline: $($_.FullName)" }
    foreach ($line in ($text -split "`n")) {
        if ($line -match '[ \t]\r?$') { throw "trailing whitespace: $($_.FullName)" }
    }
}

foreach ($forbidden in @("IPZOR", "Buzz", "DeepSeek", "OpenPencil")) {
    foreach ($path in @(
        (Join-Path $repoRoot ".agents/skills/codex-air"),
        (Join-Path $repoRoot ".agents/skills/codex-prove")
    )) {
        Get-ChildItem -LiteralPath $path -File -Recurse | ForEach-Object {
            Assert-Condition ((Get-Text $_.FullName) -notmatch [regex]::Escape($forbidden)) "project-specific term remains in Skill"
        }
    }
}

foreach ($activeFile in @("README.md", "README.en.md", "SECURITY.md", "CONTRIBUTING.md", "SUPPORT.md", "CHANGELOG.md", "docs/prompt-recipes.md", ".github/ISSUE_TEMPLATE/config.yml")) {
    Assert-Condition ((Get-Text (Join-Path $repoRoot $activeFile)) -notmatch 'github\.com/yehyakin/codex-codex-air') "old repository URL remains in active documentation"
}

Write-Output "PowerShell syntax: PASS"
Write-Output "YAML/TOML/JSON structure: PASS"
Write-Output "Validation: PASS"
exit 0
