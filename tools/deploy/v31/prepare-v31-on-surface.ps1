#requires -Version 5.1
# Owner-run; stage V31 in Xoom /run over the established COM9 transfer.
# No permanent Xoom installation or wireless connection in this command.
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if ($env:COMPUTERNAME -ne 'SURFACE-BOOK-2') { throw 'STOP: not Surface Book 2' }
$old = Join-Path $env:USERPROFILE 'xoom-linux-rom\captures\MZ600-V31-CONDITIONAL-UP-20261027'
if (-not (Test-Path -LiteralPath (Join-Path $old 'mz600-v31-owner-once.py'))) { throw 'Missing original V31 transport' }
if (-not ([System.IO.Ports.SerialPort]::GetPortNames() -contains 'COM9')) { throw 'COM9 unavailable' }
$dir = Join-Path $env:TEMP 'mz600-v31-p8-preparation-20261027'
if (Test-Path -LiteralPath $dir) { throw 'Stage folder exists: do not overwrite attempt' }
New-Item -ItemType Directory -Path $dir | Out-Null
$commit = '4852c875cdec6027da60a27d80addf7e2430d69a'
$base = "https://raw.githubusercontent.com/Olsens11/XoomLinux7/$commit/tools/deploy/v31"
$files = @(
    @{ Name='install-v31-provisional.sh'; Size=5876; SHA='e8874a5edfad04c516ad22bd8230fe0332126acce1e8a59e559c543fccb64575' },
    @{ Name='restore-before-v31.sh'; Size=2824; SHA='4744d7cd4b2338b3d5cb34a6572a20403296eebb5972fcd8429316b9c4c1e31d' },
    @{ Name='stage-v31-from-surface.py'; Size=3214; SHA='cadc394bf06337b9b089f3116c7aecc3c1cc32e79cb441a8289058a7f2eebb54' }
)
foreach ($item in $files) {
    $p = Join-Path $dir $item.Name
    Invoke-WebRequest -UseBasicParsing -Uri "$base/$($item.Name)" -OutFile $p
    if ((Get-Item -LiteralPath $p).Length -ne $item.Size) { throw "Size mismatch $($item.Name)" }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLowerInvariant()
    if ($hash -ne $item.SHA) { throw "SHA mismatch $($item.Name)" }
    Write-Host "SHA PASS $($item.Name)"
}
Write-Host 'Close your interactive COM9 terminal before proceeding.'
$confirm=Read-Host 'Type STAGE to copy verified assets into Xoom RAM only'
if ($confirm -cne 'STAGE') { Write-Host 'Canceled; no COM9 operation'; exit 0 }
& py -3 (Join-Path $dir 'stage-v31-from-surface.py')
if ($LASTEXITCODE -ne 0) { throw 'V31 COM9 stage/dry-run failed; do not apply' }
Write-Host ''
Write-Host 'V31 in-RAM staging and dry-run passed. No permanent files modified.'
Write-Host 'Reconnect the COM9 root terminal, inspect the installer, and only then run:'
Write-Host 'bash /run/xoom-v31-install/install-v31-provisional.sh --apply'
