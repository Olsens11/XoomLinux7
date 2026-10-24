$ErrorActionPreference='Stop'
$linux=@(Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPDeviceID -match 'VID_0525&PID_A4A7' -and $_.Name -match '\(COM[0-9]+\)' })
if($linux.Count -ne 1){ throw "Linux Xoom USB serial port ambiguous: $($linux.Count)" }
if($linux[0].Name -notmatch '\((COM[0-9]+)\)'){ throw 'COM port unresolved' }
$portName=$Matches[1]
Write-Output ('VERIFIED_LINUX_PORT='+$portName+' ID='+$linux[0].PNPDeviceID)
$p=New-Object System.IO.Ports.SerialPort
$p.PortName=$portName
$p.BaudRate=115200
$p.Parity=[System.IO.Ports.Parity]::None
$p.DataBits=8
$p.StopBits=[System.IO.Ports.StopBits]::One
$p.ReadTimeout=300
$p.WriteTimeout=1000
$p.DtrEnable=$true
$p.RtsEnable=$true
try{
 $p.Open()
 Start-Sleep -Milliseconds 300
 $p.DiscardInBuffer()
 $p.Write('REBOOT'+[char]10)
 $armed=''
 $deadline=[DateTime]::UtcNow.AddSeconds(5)
 while([DateTime]::UtcNow -lt $deadline){
   Start-Sleep -Milliseconds 100
   $armed+=$p.ReadExisting()
   if($armed.Contains('REBOOT ARMED: send CONFIRM REBOOT')){break}
 }
 Write-Output ('ARM_RESPONSE='+$armed.Trim())
 if(!$armed.Contains('REBOOT ARMED: send CONFIRM REBOOT')){ throw 'Reboot not armed; confirmation deliberately withheld' }
 $p.Write('CONFIRM REBOOT'+[char]10)
 Write-Output 'REBOOT_CONFIRMATION_SENT_TO_REPLACEMENT_MZ600'
 Start-Sleep -Milliseconds 700
 try{Write-Output ('DEVICE_RESPONSE='+$p.ReadExisting().Trim())}catch{Write-Output ('USB_DISCONNECT_EXPECTED='+$_.Exception.Message)}
}finally{
 try{if($p.IsOpen){$p.Close()}}catch{}
 $p.Dispose()
}
