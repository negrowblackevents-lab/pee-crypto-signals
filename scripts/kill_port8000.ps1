$port = 8000
$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if (-not $connections) {
    Write-Output "No connections on port $port"
    exit 0
}
$pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $pids) {
    try {
        Stop-Process -Id $pid -Force -ErrorAction Stop
        Write-Output "Killed PID $pid"
    } catch {
        Write-Output "Failed to kill PID $pid: $_"
    }
}
# Confirm
Start-Sleep -Seconds 1
netstat -ano | Select-String ":$port"
