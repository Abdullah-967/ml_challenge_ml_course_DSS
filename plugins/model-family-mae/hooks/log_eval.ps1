# PostToolUse hook for the model-family-mae plugin.
#
# Receives the shell tool's PostToolUse payload as JSON on stdin. If the command
# invoked the bundled `eval_family.py` or `mfm_cli.py run`, append one audit line
# to `experiments/_mfm_hook.log` in the project root.
#
# This is a transcript of every canonical CV invocation, so an iteration
# log can never silently miss a run. The hook is non-blocking and never
# fails the parent tool call.

$ErrorActionPreference = 'SilentlyContinue'

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    $payload = $raw | ConvertFrom-Json
    $command = $null
    if ($payload.tool_input -and $payload.tool_input.command) {
        $command = [string]$payload.tool_input.command
    }
    if (-not $command) { exit 0 }
    if ($command -notmatch 'eval_family\.py' -and $command -notmatch 'mfm_cli\.py"\s+run|mfm_cli\.py\s+run') { exit 0 }

    $projectDir = $env:CLAUDE_PROJECT_DIR
    if (-not $projectDir) { $projectDir = $env:CODEX_PROJECT_DIR }
    if (-not $projectDir) { $projectDir = (Get-Location).Path }
    $expDir = Join-Path $projectDir 'experiments'
    if (-not (Test-Path $expDir)) {
        New-Item -ItemType Directory -Force -Path $expDir | Out-Null
    }
    $logPath = Join-Path $expDir '_mfm_hook.log'

    $stamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'
    $exitCode = if ($null -ne $payload.tool_response.exit_code) { $payload.tool_response.exit_code } else { 'n/a' }
    $line = "[{0}] mfm evaluation invoked (exit={1}) :: {2}" -f $stamp, $exitCode, $command
    Add-Content -LiteralPath $logPath -Value $line -Encoding utf8
} catch {
    # Hook must never fail the parent tool call; swallow errors.
}
exit 0
