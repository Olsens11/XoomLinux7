param(
 [ValidateSet('PING','HELP','STATUS','CPU','MEM','STORAGE','INPUT','THERMAL','USB','LOGS','CMDLINE','GRID','WIFI','WIFI_START','WIFILOG','WIFIDIRS','SDIO','BOOTWIFI','BOOTLOG','TOUCH','TOUCHSTOP','REBOOT','POWEROFF','CANCEL','CONFIRM REBOOT','CONFIRM POWEROFF')]
 [string]$Command='STATUS',
 [int]$ReadSeconds=5
)
$ErrorActionPreference='Stop'
# Filter strictly for Linux gadget CDC ACM VID:PID 0525:A4A7 (not Android Xoom).
$usb=@(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match 'VID_0525&PID_A4A7' })
Write-Output '=== XOOM LINUX USB CDC ACM ENUMERATION ==='
if($usb.Count -eq 0){
 Write-Output 'NOT DETECTED: no VID_0525&PID_A4A7 USB gadget is visible.'
 exit 2
}
$usb|Select-Object Class,Status,FriendlyName,InstanceId|Format-Table -AutoSize|Out-String|Write-Output
$coms=@(Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPDeviceID -match 'VID_0525&PID_A4A7' -and $_.Name -match '\(COM[0-9]+\)' })
if($coms.Count -ne 1){
 Write-Output "COM PORT NOT READY: Found $($coms.Count) suitable ports. Check Windows CDC-ACM USB serial driver."
 exit 3
}
if($coms[0].Name -notmatch '\((COM[0-9]+)\)'){throw 'COM port parsing failed'}
$portName=$Matches[1]
Write-Output ('SELECTED PORT='+$portName)
$port=New-Object System.IO.Ports.SerialPort;$port.PortName=$portName;$port.BaudRate=115200;$port.Parity=[System.IO.Ports.Parity]::None;$port.DataBits=8;$port.StopBits=[System.IO.Ports.StopBits]::One
$port.ReadTimeout=500
$port.WriteTimeout=1200
$port.DtrEnable=$true
$port.RtsEnable=$true
try{
 $port.Open()
 Start-Sleep -Milliseconds 500
 $port.DiscardInBuffer()
 Write-Output ('SENDING='+$Command)
 $port.Write($Command+"`n")
 $until=[DateTime]::UtcNow.AddSeconds([Math]::Max(2,[Math]::Min($ReadSeconds,30)))
 $reply=''
 while([DateTime]::UtcNow -lt $until){
  Start-Sleep -Milliseconds 180
  $chunk=$port.ReadExisting()
  if($chunk.Length -gt 0){$reply+=$chunk;if($reply.Length -gt 30000){break}}
 }
 Write-Output '=== LINUX RESPONSE ==='
 if($reply.Length){Write-Output $reply}else{Write-Output 'NO SERIAL RESPONSE - device may not have initialized ttyGS0'}
}finally{
 if($port.IsOpen){$port.Close()}
 $port.Dispose()
}


