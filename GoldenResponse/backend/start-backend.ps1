# Run Spring Boot backend (no global Maven required)
Set-Location $PSScriptRoot

# Free port 8080 if a previous instance is still running
$portLine = netstat -ano | Select-String ":8080.*LISTENING"
if ($portLine) {
    $pid = ($portLine -split '\s+')[-1]
    Write-Host "Stopping process $pid using port 8080..."
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "Starting backend on http://localhost:8080 ..."
.\mvnw.cmd spring-boot:run
