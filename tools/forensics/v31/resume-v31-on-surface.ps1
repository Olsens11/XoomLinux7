#requires -Version 5.1
# Resume V31 after a staging-only validator error. No transfer or overwrite.
# Requires the exact five previously SHA-verified files.
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:USERPROFILE 'xoom-linux-rom\captures\MZ600-V31-CONDITIONAL-UP-20261027'
$trial = 'up31a-01-mask000'
$runDir = Join-Path $root 'runs'
$expected = @(
  @{ Name='mz600-v31-oem2012.bin'; Bytes=264140; SHA='5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834' }
  @{ Name='brcmfmac-wcc-matched-v31.ko'; Bytes=5892; SHA='6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d' }
  @{ Name='mz600-v31-escan-event69.ko'; Bytes=354392; SHA='c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8' }
  @{ Name='mz600-v31-normal-scan.sh'; Bytes=11426; SHA='5b168d624d23e68c828b6d169c4425de54b4f10e97c618d7a449cbe5f31033ea' }
  @{ Name='mz600-v31-owner-once.py'; Bytes=19753; SHA='9b54594f65c9b1ceb2e03f4ef793c201d0eaf16fd6a24217cdc37426ac3e9b29' }
)
if ($env:COMPUTERNAME -ne 'SURFACE-BOOK-2') { throw 'STOP: wrong computer' }
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'STOP: staged V31 directory absent' }
if (Test-Path -LiteralPath $runDir) {
  $existing = @(Get-ChildItem -LiteralPath $runDir -Force -ErrorAction Stop)
  if ($existing.Count -ne 0) { throw 'STOP: V31 runs directory has existing evidence; do not reuse this trial' }
}
foreach ($entry in $expected) {
  $path = Join-Path $root $entry.Name
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw ('STOP: missing ' + $entry.Name) }
  $info = Get-Item -LiteralPath $path
  if ($info.Length -ne $entry.Bytes) { throw ('STOP: byte-count mismatch ' + $entry.Name) }
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
  if ($hash -ne $entry.SHA) { throw ('STOP: SHA256 mismatch ' + $entry.Name) }
  Write-Host ('SHA PASS ' + $entry.Name + ' ' + $info.Length + ' bytes')
}
if (-not ([System.IO.Ports.SerialPort]::GetPortNames() -contains 'COM9')) {
  throw 'STOP: COM9 missing'
}
& py -3 -c 'import serial; print("pyserial ready")'
if ($LASTEXITCODE -ne 0) { throw 'STOP: Python 3 or pyserial unavailable' }
Write-Host 'STAGED INPUTS VALID. No Xoom commands have been sent by this launcher.'
Write-Host 'About to run one RAM-only V31 diagnostic with COM9 exclusive access,'
Write-Host 'temporary module/firmware overlays, two ordinary scans, private logs,'
Write-Host 'and independent original-state rollback checks. No p7/p8 flashing.'
$confirmation = Read-Host 'Type RUN to begin the one-time V31 trial (anything else cancels)'
if ($confirmation -cne 'RUN') { Write-Host 'Canceled; no test started'; exit 0 }
Push-Location $root
try {
  & py -3 '.\mz600-v31-owner-once.py' --masks 0 --series up31a
  $exitCode = $LASTEXITCODE
} finally {
  Pop-Location
}
Write-Host ('V31 runner exit code: ' + $exitCode)
Write-Host ('Private results: ' + $runDir)
Write-Host 'Do not rerun the same trial if the second scan fails.'
exit $exitCode
