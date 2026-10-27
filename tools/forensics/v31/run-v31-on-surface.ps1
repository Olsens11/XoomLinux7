#requires -Version 5.1
<#
Owner-operated Motorola Xoom MZ600 V31 conditional WLC_UP diagnostic.
Run on SURFACE-BOOK-2 after starting the standard temporary desktop HTTP
file server on LAN port 43157. Only RAM/module temporary state on Xoom.
#>
param([string]$DesktopIp = "192.168.0.125", [switch]$PrepareOnly)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$commit = "ce08f2dee856f050ee8c91b447b65c0b9596978f"
$raw = "https://raw.githubusercontent.com/Olsens11/XoomLinux7/$commit/tools/forensics/v31"
$old = Join-Path $env:USERPROFILE "xoom-linux-rom\captures\MZ600-V30-UPSTATE-20261027"
$root = Join-Path $env:USERPROFILE "xoom-linux-rom\captures\MZ600-V31-CONDITIONAL-UP-20261027"
$temp = Join-Path $env:TEMP ("mz600-v31-verified-" + [Guid]::NewGuid().ToString("N"))
$moduleHash = "c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8"
$firmwareHash = "5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834"
$wccHash = "6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d"
$shellHash = "5b168d624d23e68c828b6d169c4425de54b4f10e97c618d7a449cbe5f31033ea"
$hostHash = "9b54594f65c9b1ceb2e03f4ef793c201d0eaf16fd6a24217cdc37426ac3e9b29"
function Assert-ShaSize {
  param([string]$Path,[string]$ExpectedHash,[long]$ExpectedBytes)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing file: $Path" }
  $item = Get-Item -LiteralPath $Path
  if ($item.Length -ne $ExpectedBytes) { throw "Size mismatch: $Path" }
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
  if ($hash -ne $ExpectedHash) { throw "SHA mismatch: $Path" }
  Write-Host "SHA PASS $($item.Name) $($item.Length) bytes"
}
if ($env:COMPUTERNAME -ne "SURFACE-BOOK-2") { throw "STOP: wrong host" }
if (Test-Path -LiteralPath $root) { throw "STOP: V31 directory exists. Do not overwrite or reuse trial" }
if (-not (Test-Path -LiteralPath $old -PathType Container)) { throw "STOP: private V30 source directory missing" }
if (-not ([System.IO.Ports.SerialPort]::GetPortNames() -contains "COM9")) { throw "STOP: COM9 unavailable" }
$fwOld = Join-Path $old "mz600-v30-oem2012.bin"
$wccOld = Join-Path $old "brcmfmac-wcc-matched-v30.ko"
Assert-ShaSize $fwOld $firmwareHash 264140
Assert-ShaSize $wccOld $wccHash 5892
& py -3 -c "import serial; print('pyserial ready')"
if ($LASTEXITCODE -ne 0) { throw "STOP: Python 3 + pyserial required" }
New-Item -ItemType Directory -Path $temp | Out-Null
try {
  $core = Join-Path $temp "mz600-v31-escan-event69.ko"
  $bash = Join-Path $temp "mz600-v31-normal-scan.sh"
  $runner = Join-Path $temp "mz600-v31-owner-once.py"
  $coreUri = "http://" + $DesktopIp + ":43157/mz600-v31-escan-event69.ko"
  Write-Host "Fetching verified module from Desktop temporary server $coreUri"
  Invoke-WebRequest -UseBasicParsing -Uri $coreUri -OutFile $core
  Assert-ShaSize $core $moduleHash 354392
  Invoke-WebRequest -UseBasicParsing -Uri "$raw/mz600-v31-normal-scan.sh" -OutFile $bash
  Assert-ShaSize $bash $shellHash 11426
  Invoke-WebRequest -UseBasicParsing -Uri "$raw/mz600-v31-owner-once.py" -OutFile $runner
  Assert-ShaSize $runner $hostHash 19753
  New-Item -ItemType Directory -Path $root | Out-Null
  Copy-Item -LiteralPath $fwOld -Destination (Join-Path $root "mz600-v31-oem2012.bin")
  Copy-Item -LiteralPath $wccOld -Destination (Join-Path $root "brcmfmac-wcc-matched-v31.ko")
  Copy-Item -LiteralPath $core -Destination (Join-Path $root "mz600-v31-escan-event69.ko")
  Copy-Item -LiteralPath $bash -Destination (Join-Path $root "mz600-v31-normal-scan.sh")
  Copy-Item -LiteralPath $runner -Destination (Join-Path $root "mz600-v31-owner-once.py")
  Assert-ShaSize (Join-Path $root "mz600-v31-oem2012.bin") $firmwareHash 264140
  Assert-ShaSize (Join-Path $root "brcmfmac-wcc-matched-v31.ko") $wccHash 5892
  Assert-ShaSize (Join-Path $root "mz600-v31-escan-event69.ko") $moduleHash 354392
  Assert-ShaSize (Join-Path $root "mz600-v31-normal-scan.sh") $shellHash 11426
  Assert-ShaSize (Join-Path $root "mz600-v31-owner-once.py") $hostHash 19753
} finally {
  if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force -Recurse }
}
Write-Host "STAGING PASS: no device commands have been issued"
if ($PrepareOnly) { Write-Host "PrepareOnly selected; exiting"; exit 0 }
Write-Host "The next step takes exclusive COM9 access; temporarily reloads Wi-Fi"
Write-Host "with SHA-pinned RAM firmware/WCC; makes two normal scans; retains"
Write-Host "private numeric diagnostic logs and restores original installed state."
Write-Host "No boot partition, root partition or NVRAM flashing is performed."
$confirm = Read-Host "Type RUN to begin one-time V31 test (anything else cancels)"
if ($confirm -cne "RUN") { Write-Host "Canceled, staged files retained"; exit 0 }
Push-Location $root
try {
  & py -3 ".\mz600-v31-owner-once.py" --masks 0 --series up31a
  $status = $LASTEXITCODE
} finally {
  Pop-Location
}
Write-Host "V31 test exit code $status"
Write-Host "Private receipts and trace are in $root\runs"
Write-Host "If scan 2 fails, nonzero test status is expected: independently check"
Write-Host "the receipt's independent_poststate_ok and original-file restoration."
exit $status
