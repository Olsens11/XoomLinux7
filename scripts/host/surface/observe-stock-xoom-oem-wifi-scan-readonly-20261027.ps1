# Original Motorola Xoom OEM Android Wi-Fi scan observation (host-only, read-only)
# No rooting, firmware change, Wi-Fi settings change, automatic scan, or device reboot.
# Requires ONE stock Xoom in adb 'device' state and USB debugging enabled.
# Owner opens Settings > Wi-Fi and refreshes/scrolls manually while logcat streams.
# All nearby SSIDs, BSSIDs and identifiers remain in PRIVATE Surface capture files.
$ErrorActionPreference = 'Stop'
$adb = 'C:\Users\olsen\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe'
if (-not (Test-Path -LiteralPath $adb -PathType Leaf)) { throw 'ADB tools missing; no device changed' }
$rows = @(& $adb devices 2>&1)
$ready = @($rows | Where-Object { $_ -match '^(\S+)\s+device\s*$' } | ForEach-Object { $Matches[1] })
$other = @($rows | Where-Object { $_ -match '^(\S+)\s+(unauthorized|offline)\b' })
if ($ready.Count -ne 1 -or $other.Count) {
    throw "Need exactly one authorized OEM Xoom in ADB device state. Check USB cable, Android Settings > Applications > Development > USB debugging, and drivers. No scan was attempted."
}
$serial = [string]$ready[0]
function AdbRead {
    param([string[]] $Commands)
    $result = @(& $script:adb -s $script:serial @Commands 2>&1)
    if ($LASTEXITCODE -ne 0) { throw ('Read-only ADB command failed: ' + ($Commands -join ' ')) }
    return ($result -join [Environment]::NewLine).Trim()
}
$model = AdbRead -Commands @('shell','getprop','ro.product.model')
$device = AdbRead -Commands @('shell','getprop','ro.product.device')
$release = AdbRead -Commands @('shell','getprop','ro.build.version.release')
$fingerprint = AdbRead -Commands @('shell','getprop','ro.build.fingerprint')
$kernel = AdbRead -Commands @('shell','uname','-r')
if (("$model $device") -notmatch '(?i)(xoom|stingray|wingray|mz60[024])' -or $kernel -match '^7\.0\.0-next-') {
    throw 'ADB device is not positively identified as stock-reference Xoom; refusing capture.'
}
$root = 'C:\Users\olsen\xoom-linux-rom\captures\OEM-XOOM-WIFI-SCAN-READONLY-20261027'
New-Item -Path $root -ItemType Directory -Force | Out-Null
$run = Join-Path $root (Get-Date -Format 'yyyyMMdd-HHmmss')
if (Test-Path -LiteralPath $run) { throw 'Capture directory exists; refuse overwrite' }
New-Item -Path $run -ItemType Directory | Out-Null
@("Model: $model","Device: $device","Android: $release","Kernel: $kernel","Build fingerprint: $fingerprint","ADB serial: [private]") | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $run 'private-device-identity.txt')
Write-Host "OEM Xoom detected: $model, Android $release, kernel $kernel"
Write-Host "Private captures stay on the Surface: $run"
& $adb -s $serial shell dumpsys wifi 2>&1 | Out-File -LiteralPath (Join-Path $run 'private-wifi-before.txt') -Encoding utf8
$stdout = Join-Path $run 'private-live-logcat.txt'
$stderr = Join-Path $run 'private-live-logcat-errors.txt'
$proc = $null
try {
    $proc = Start-Process -FilePath $adb -ArgumentList @('-s',$serial,'logcat','-v','time') -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Start-Sleep -Milliseconds 300
    Write-Host 'Recording. On OEM Xoom, open Settings > Wi-Fi, refresh/scroll, and watch security descriptions populate.'
    Read-Host 'Press ENTER here once the Wi-Fi list has settled (ends recording)'
} finally {
    if ($proc) {
        $proc.Refresh()
        if (-not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            $proc.WaitForExit(3000) | Out-Null
        }
    }
}
& $adb -s $serial shell dumpsys wifi 2>&1 | Out-File -LiteralPath (Join-Path $run 'private-wifi-after.txt') -Encoding utf8
& $adb -s $serial shell dmesg 2>&1 | Out-File -LiteralPath (Join-Path $run 'private-dmesg-after.txt') -Encoding utf8
if (Test-Path -LiteralPath $stdout) {
    $lines = @(Get-Content -LiteralPath $stdout)
    $scan = @($lines | Where-Object { $_ -match '(?i)(scan|iscan|escan|wlan|wifi|wpa_supplicant|brcm|scan_complete)' })
    Write-Host ('Logcat lines captured: {0}; possible Wi-Fi/scan lines: {1}' -f $lines.Count,$scan.Count)
}
Write-Host 'OEM_REFERENCE_CAPTURE_COMPLETE_PRIVATE'
Write-Host "Capture folder: $run"
Write-Host 'Keep the raw log private: SSIDs and BSSIDs may be included.'
