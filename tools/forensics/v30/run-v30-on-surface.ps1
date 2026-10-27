#requires -Version 5.1
<#
Owner-operated Motorola Xoom MZ600 V30 read-only firmware-UP/MPC diagnostic.
Run on SURFACE-BOOK-2 after starting the standard temporary desktop HTTP
file server on LAN port 43157. Only RAM/module temporary state on Xoom.
#>
param([string]$DesktopIp = "192.168.0.125", [switch]$PrepareOnly)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$commit = "9438ba83b58bb7d482a0fe186a214edc4bf8ce20"
$raw = "https://raw.githubusercontent.com/Olsens11/XoomLinux7/$commit/tools/forensics/v30"
$old = Join-Path $env:USERPROFILE "xoom-linux-rom\captures\MZ600-V28-NATIVE-SCAN-20261027"
$root = Join-Path $env:USERPROFILE "xoom-linux-rom\captures\MZ600-V30-UPSTATE-20261027"
$temp = Join-Path $env:TEMP ("mz600-v30-verified-" + [Guid]::NewGuid().ToString("N"))
$moduleHash = "c064cd5c23c50d423e1c09be106e61633bdf35ef57046d00f211e10659223738"
$firmwareHash = "5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834"
$wccHash = "6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d"
$shellHash = "df1349edb4dad1797df849208ae6be891bbfc131d8f3ee9a68819f6204522444"
$hostHash = "784cb7d18ebb1db39769401255bd22ce80120b08a482cdb9074ba9532755dfa4"
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
if (Test-Path -LiteralPath $root) { throw "STOP: V30 directory exists. Do not overwrite or reuse trial" }
if (-not (Test-Path -LiteralPath $old -PathType Container)) { throw "STOP: private V28 source directory missing" }
if (-not ([System.IO.Ports.SerialPort]::GetPortNames() -contains "COM9")) { throw "STOP: COM9 unavailable" }
$fwOld = Join-Path $old "mz600-v28-oem2012.bin"
$wccOld = Join-Path $old "brcmfmac-wcc-matched-v28.ko"
Assert-ShaSize $fwOld $firmwareHash 264140
Assert-ShaSize $wccOld $wccHash 5892
& py -3 -c "import serial; print('pyserial ready')"
if ($LASTEXITCODE -ne 0) { throw "STOP: Python 3 + pyserial required" }
New-Item -ItemType Directory -Path $temp | Out-Null
try {
  $core = Join-Path $temp "mz600-v30-escan-event69.ko"
  $bash = Join-Path $temp "mz600-v30-normal-scan.sh"
  $runner = Join-Path $temp "mz600-v30-owner-once.py"
  $coreUri = "http://" + $DesktopIp + ":43157/mz600-v30-escan-event69.ko"
  Write-Host "Fetching verified module from Desktop temporary server $coreUri"
  Invoke-WebRequest -UseBasicParsing -Uri $coreUri -OutFile $core
  Assert-ShaSize $core $moduleHash 353372
  Invoke-WebRequest -UseBasicParsing -Uri "$raw/mz600-v30-normal-scan.sh" -OutFile $bash
  Assert-ShaSize $bash $shellHash 11386
  Invoke-WebRequest -UseBasicParsing -Uri "$raw/mz600-v30-owner-once.py" -OutFile $runner
  Assert-ShaSize $runner $hostHash 19746
  New-Item -ItemType Directory -Path $root | Out-Null
  Copy-Item -LiteralPath $fwOld -Destination (Join-Path $root "mz600-v30-oem2012.bin")
  Copy-Item -LiteralPath $wccOld -Destination (Join-Path $root "brcmfmac-wcc-matched-v30.ko")
  Copy-Item -LiteralPath $core -Destination (Join-Path $root "mz600-v30-escan-event69.ko")
  Copy-Item -LiteralPath $bash -Destination (Join-Path $root "mz600-v30-normal-scan.sh")
  Copy-Item -LiteralPath $runner -Destination (Join-Path $root "mz600-v30-owner-once.py")
  Assert-ShaSize (Join-Path $root "mz600-v30-oem2012.bin") $firmwareHash 264140
  Assert-ShaSize (Join-Path $root "brcmfmac-wcc-matched-v30.ko") $wccHash 5892
  Assert-ShaSize (Join-Path $root "mz600-v30-escan-event69.ko") $moduleHash 353372
  Assert-ShaSize (Join-Path $root "mz600-v30-normal-scan.sh") $shellHash 11386
  Assert-ShaSize (Join-Path $root "mz600-v30-owner-once.py") $hostHash 19746
} finally {
  if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force -Recurse }
}
Write-Host "STAGING PASS: no device commands have been issued"
if ($PrepareOnly) { Write-Host "PrepareOnly selected; exiting"; exit 0 }
Write-Host "The next step takes exclusive COM9 access; temporarily reloads Wi-Fi"
Write-Host "with SHA-pinned RAM firmware/WCC; makes two normal scans; retains"
Write-Host "private numeric diagnostic logs and restores original installed state."
Write-Host "No boot partition, root partition or NVRAM flashing is performed."
$confirm = Read-Host "Type RUN to begin one-time V30 test (anything else cancels)"
if ($confirm -cne "RUN") { Write-Host "Canceled, staged files retained"; exit 0 }
Push-Location $root
try {
  & py -3 ".\mz600-v30-owner-once.py" --masks 0 --series up30a
  $status = $LASTEXITCODE
} finally {
  Pop-Location
}
Write-Host "V30 test exit code $status"
Write-Host "Private receipts and trace are in $root\runs"
Write-Host "If scan 2 fails, nonzero test status is expected: independently check"
Write-Host "the receipt's independent_poststate_ok and original-file restoration."
exit $status
