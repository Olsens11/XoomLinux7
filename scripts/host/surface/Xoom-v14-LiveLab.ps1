<#
  Replacement MZ600 v14 USB Wi-Fi live-lab host client.
  Uses the existing CDC-ACM USB cable; never flashes or touches emmc.
  Requires PING response from v14 exactly before sending any command.
  Examples:
    .\Xoom-v14-LiveLab.ps1 -Action Status
    .\Xoom-v14-LiveLab.ps1 -Action Start
    .\Xoom-v14-LiveLab.ps1 -Action Stop
    .\Xoom-v14-LiveLab.ps1 -Action Upload -Kind BRCMFMAC -FilePath C:\path\brcmfmac.ko
#>
param(
 [ValidateSet('Status','Start','Stop','Retry','Debug','Upload','Logs','BootLog')][string]$Action='Status',
 [ValidateSet('BRCMFMAC','BRCMUTIL','FIRMWARE','NVRAM')][string]$Kind='BRCMFMAC',
 [string]$FilePath='',
 [ValidateRange(0,65535)][int]$DebugLevel=6
)
$ErrorActionPreference='Stop'
$devices=@(Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPDeviceID -match 'VID_0525&PID_A4A7' -and $_.Name -match '\(COM[0-9]+\)' })
if($devices.Count -ne 1){throw "Exactly one active Xoom CDC serial port is required; found $($devices.Count)."}
if($devices[0].Name -notmatch '\((COM[0-9]+)\)'){throw 'COM name unresolved'}
$portName=$Matches[1]
$serial=New-Object System.IO.Ports.SerialPort
$serial.PortName=$portName;$serial.BaudRate=115200
$serial.DataBits=8;$serial.Parity=[System.IO.Ports.Parity]::None
$serial.StopBits=[System.IO.Ports.StopBits]::One
$serial.ReadTimeout=400;$serial.WriteTimeout=8000
$serial.DtrEnable=$true;$serial.RtsEnable=$true

function Read-Until([string]$Expected,[int]$Seconds=6){
 $buffer='';$until=[DateTime]::UtcNow.AddSeconds($Seconds)
 while([DateTime]::UtcNow -lt $until){
   Start-Sleep -Milliseconds 35
   try{$buffer+=$serial.ReadExisting()}catch{throw "USB serial connection lost: $($_.Exception.Message)"}
   if($buffer.Contains($Expected)){return $buffer}
 }
 throw ("Serial response timeout awaiting '"+$Expected+"' ; received "+$buffer.Substring(0,[Math]::Min(1500,$buffer.Length)))
}
function Send-Command([string]$Command,[string]$Marker,[int]$Seconds=6){
 $serial.DiscardInBuffer()
 $serial.Write($Command+[char]10)
 return (Read-Until $Marker $Seconds)
}
function Crc32([byte[]]$Data){
 [uint32]$crc=[Convert]::ToUInt32('FFFFFFFF',16)
 [uint32]$poly=[Convert]::ToUInt32('EDB88320',16)
 foreach($bt in $Data){
  $crc=$crc -bxor [uint32]$bt
  for($i=0;$i -lt 8;$i++){
   if($crc -band [uint32]1){$crc=($crc -shr 1) -bxor $poly}
   else{$crc=$crc -shr 1}
  }
 }
 return ($crc -bxor [Convert]::ToUInt32('FFFFFFFF',16))
}
try{
 $serial.Open()
 Start-Sleep -Milliseconds 250
 $ident=Send-Command 'PING' 'PONG XOOM-LINUX V14' 7
 Write-Output ('VERIFIED_V14_USB='+$portName)
 if($Action -eq 'Upload'){
   if(-not $FilePath){throw 'Upload requires -FilePath'}
   $resolved=(Resolve-Path -LiteralPath $FilePath).ProviderPath
   $data=[IO.File]::ReadAllBytes($resolved)
   if($data.Length -lt 16 -or $data.Length -gt 1048576){throw 'Allowed upload size 16 through 1,048,576 bytes'}
   if($Kind -eq 'BRCMFMAC' -or $Kind -eq 'BRCMUTIL'){
      if($data.Length -lt 4 -or $data[0] -ne 127 -or $data[1] -ne 69 -or $data[2] -ne 76 -or $data[3] -ne 70){throw 'Module file does not have ELF header'}
   }
   if($Kind -eq 'NVRAM'){
     $text=[Text.Encoding]::ASCII.GetString($data)
     if($text -match '(?im)^\s*(macaddr|ccode|regrev)\s*='){throw 'NVRAM contains device identity or country/regrev override'}
   }
   $expected=(Crc32 $data).ToString('X8')
   $ack=Send-Command ("UPLOAD "+$Kind+" "+$data.Length) 'UPLOAD READY BYTES' 7
   if(!$ack.Contains("UPLOAD READY BYTES $($data.Length)")){throw 'Unexpected upload length acknowledgment'}
   $offset=0
   while($offset -lt $data.Length){
     $chunk=[Math]::Min(1024,$data.Length-$offset)
     $serial.Write($data,$offset,$chunk)
     $offset+=$chunk
   }
   $reply=Read-Until 'UPLOAD DONE' 45
   Write-Output $reply.Trim()
   if($reply -notmatch ('UPLOAD DONE SIZE '+$data.Length+' CRC32 0x'+$expected)){throw "Device CRC32 mismatch; expected $expected"}
   Write-Output ('RAM_ONLY_UPLOAD_VERIFIED Kind='+$Kind+' Size='+$data.Length+' CRC32='+$expected)
 }else{
   switch($Action){
      Status{$cmd='WIFI_STATUS';$marker='NO SCAN/ASSOCIATION/DHCP'}
      Start{$cmd='WIFI_START';$marker='WIFI PROBE STARTED'}
      Stop{$cmd='WIFI_STOP';$marker='brcmutil_rc'}
      Retry{$cmd='WIFI_RETRY';$marker='WIFI PROBE STARTED'}
      Debug{$cmd='WIFI_DEBUG '+$DebugLevel;$marker='WIFI DEBUG SET'}
      Logs{$cmd='LOGS';$marker='KERNEL LOGS'}
      BootLog{$cmd='BOOTLOG';$marker='BOOT'}
   }
   $response=Send-Command $cmd $marker 12
   Write-Output $response.Trim()
 }
}finally{
 try{if($serial.IsOpen){$serial.Close()}}catch{}
 $serial.Dispose()
}
