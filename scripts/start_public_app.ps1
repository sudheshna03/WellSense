# Start WellSense with a secure public HTTPS URL
$ErrorActionPreference = "Stop"

$workspace = "C:\Users\User\.gemini\antigravity\scratch\WellSense"
Set-Location $workspace

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Starting WellSense Live Web Server    " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Fetch public IP for localtunnel password
try {
    $ip = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 5).Trim()
} catch {
    $ip = "Check at https://ipify.org"
}

Write-Host "`n[1/2] Starting Streamlit server on http://localhost:8501..." -ForegroundColor Yellow
$stProcess = Start-Process -FilePath ".\.venv\Scripts\streamlit.exe" -ArgumentList "run","app/main.py","--server.headless","true","--server.port","8501" -PassThru -NoNewWindow

Start-Sleep -Seconds 5

Write-Host "[2/2] Generating public HTTPS URL via localtunnel..." -ForegroundColor Yellow
Write-Host "`nIMPORTANT: If the webpage asks for a 'Tunnel Password' (Endpoint IP), enter:" -ForegroundColor Magenta
Write-Host "  >>>  $ip  <<<`n" -ForegroundColor Green

# Run localtunnel
npx localtunnel --port 8501
