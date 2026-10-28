# Windows Surface host-side bridge for the Xoom's USB gadget ttyGS0.
# No device reboot, no password storage, no kernel or filesystem writes.
[CmdletBinding()]
param(
    [string]$PortName = 'COM9',
    [int]$BaudRate = 115200,
    [switch]$Probe
)
$ErrorActionPreference = 'Stop'
$port = [System.IO.Ports.SerialPort]::new(
    $PortName, $BaudRate,
    [System.IO.Ports.Parity]::None, 8,
    [System.IO.Ports.StopBits]::One)
$port.ReadTimeout = 250
$port.WriteTimeout = 1400
$port.DtrEnable = $true
$port.RtsEnable = $true
$port.Encoding = [System.Text.Encoding]::ASCII
try {
    $port.Open()
    Write-Host "Xoom Linux 7 USB console | $PortName | $BaudRate baud"
    $port.Write([string][char]13)
    Start-Sleep -Milliseconds 350
    $initial = $port.ReadExisting()
    if ($Probe) {
        Write-Host ('COM_PORT_READABLE=' + ($initial.Length -gt 0))
        Write-Host ('LOGIN_OR_SHELL=' + ($initial -match '(login:|@xoom|root@)'))
        Write-Host 'Probe complete; no device changes made.'
        exit 0
    }
    Write-Host 'Ctrl+] disconnects the host console without rebooting the Xoom.'
    Write-Host 'Close any other COM9/serial tools first; only one owns this port.'
    if ($initial.Length -gt 0) { [Console]::Write($initial) }
    while ($true) {
        $incoming = $port.ReadExisting()
        if ($incoming.Length -gt 0) { [Console]::Write($incoming) }
        if ([Console]::KeyAvailable) {
            $key = [Console]::ReadKey($true)
            $c = [int][char]$key.KeyChar
            if ($c -eq 29) { break }
            switch ($key.Key.ToString()) {
                'Enter'      { $port.Write([string][char]13); break }
                'Backspace'  { $port.Write([string][char]127); break }
                'UpArrow'    { $port.Write(([string][char]27) + '[A'); break }
                'DownArrow'  { $port.Write(([string][char]27) + '[B'); break }
                'RightArrow' { $port.Write(([string][char]27) + '[C'); break }
                'LeftArrow'  { $port.Write(([string][char]27) + '[D'); break }
                default      { if ($c -ne 0) { $port.Write([string]$key.KeyChar) } }
            }
        } else {
            Start-Sleep -Milliseconds 25
        }
    }
} catch {
    Write-Warning ("USB serial console unavailable: " + $_.Exception.Message)
    Write-Warning 'Check the cable, ttyGS0 getty, device boot, and COM port number.'
} finally {
    if ($port.IsOpen) { $port.Close() }
    $port.Dispose()
    Write-Host 'Host USB console disconnected (tablet not rebooted).'
}
