# =================================================================
# CRIP Enterprise Platform - Performance Test Runner (PowerShell)
# =================================================================
#
# This script starts the Locust performance test against the platform.
#
# USAGE:
#   .\scripts\run_perf_test.ps1
#
# It will:
# 1. Check if Docker services are running.
# 2. Run the Locust test.
# 3. Provide a link to the web UI.
#
# =================================================================

# --- Configuration ---
$LocustFile = "scripts/locustfile.py"
$LocustWebUiPort = "8089"
$ProjectDir = $PSScriptRoot | Split-Path

# --- Functions ---
function Check-Docker-Services {
    Write-Host "🔍 Checking if platform services are running..."
    $runningServices = docker-compose ps --services --filter "status=running"
    if ($runningServices.Length -lt 7) {
        Write-Host "⚠️ Not all services are running."
        $choice = Read-Host "Do you want to start them now? (y/n)"
        if ($choice -eq 'y') {
            Write-Host "🚀 Starting services with 'docker-compose up -d'..."
            docker-compose up -d
            Write-Host "⏳ Waiting 15 seconds for services to initialize..."
            Start-Sleep -Seconds 15
        } else {
            Write-Host "❌ Aborting. Please start services manually with 'docker-compose up -d'."
            exit 1
        }
    }
    Write-Host "✅ All services appear to be running."
}

# --- Main Script ---
Write-Host "🚀 Starting CRIP Performance Test..." -ForegroundColor Green
Set-Location $ProjectDir

Check-Docker-Services

Write-Host "📈 Launching Locust..." -ForegroundColor Green
Write-Host "   Open your browser and navigate to: http://localhost:$LocustWebUiPort" -ForegroundColor Cyan
Write-Host "   Press CTRL+C in this terminal to stop the test."

locust -f $LocustFile