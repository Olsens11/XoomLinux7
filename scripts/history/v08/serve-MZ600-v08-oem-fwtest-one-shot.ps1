$ErrorActionPreference='Stop'
$ip=[System.Net.IPAddress]::Parse('192.168.0.125')
$allow='192.168.0.40'
$listener=[System.Net.Sockets.TcpListener]::new($ip,43157)
$path='C:\Users\olsen\XoomLinux\Phase1\Diagnostic-MZ600-v08-OEM-FWTEST\MZ600-stingray-diagnostic-v08-OEM-FWTEST-TEMPBOOT-ONLY.img'
$expect='75F75405C88C3FF1F011E7A79955CDCB7036DF80E4E4C911D59EDBF55881B2E5'
if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $expect){throw 'Source hash mismatch'}
try{
 $listener.Start()
 Write-Output 'ONE_SHOT_LISTENING=192.168.0.125:43157'
 $client=$listener.AcceptTcpClient()
 try {
  $peer=([System.Net.IPEndPoint]$client.Client.RemoteEndPoint).Address.ToString()
  Write-Output ('PEER='+$peer)
  $client.ReceiveTimeout=15000;$client.SendTimeout=30000
  if($peer -ne $allow){throw 'Unexpected client address'}
  $stream=$client.GetStream()
  $req=New-Object System.Collections.Generic.List[byte]
  $x=New-Object byte[] 1
  while($req.Count -lt 2048){
   $n=$stream.Read($x,0,1)
   if($n -le 0){break}
   $req.Add($x[0])
   if($req.Count -ge 4 -and $req[$req.Count-4] -eq 13 -and $req[$req.Count-3] -eq 10 -and $req[$req.Count-2] -eq 13 -and $req[$req.Count-1] -eq 10){break}
  }
  $s=[Text.Encoding]::ASCII.GetString($req.ToArray())
  Write-Output ('REQUEST='+($s.Split([char]10)[0]).Trim())
  if(!$s.StartsWith("GET /xoom-mz600-diagnostic-v08-oem-ab HTTP/1.1") -and !$s.StartsWith("GET /xoom-mz600-diagnostic-v08-oem-ab HTTP/1.0")){throw 'Unexpected request'}
  $len=(Get-Item -LiteralPath $path).Length
  $header=[Text.Encoding]::ASCII.GetBytes("HTTP/1.1 200 OK`r`nContent-Type: application/octet-stream`r`nContent-Length: $len`r`nConnection: close`r`nCache-Control: no-store`r`n`r`n")
  $stream.Write($header,0,$header.Length)
  $file=[IO.File]::OpenRead($path)
  try {$file.CopyTo($stream)} finally {$file.Dispose()}
  $stream.Flush()
  Write-Output ('TRANSFERRED='+$len)
 } finally{$client.Dispose()}
} finally {$listener.Stop()}




