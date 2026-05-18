param()
# Datask dev startup script
# Usage: .\dev.ps1

$Root = $PSScriptRoot

# 1. Docker infra
Write-Host "Starting Postgres + Redis..." -ForegroundColor Cyan
docker compose -f "$Root\infra\docker-compose.yml" up -d postgres redis

# Wait until healthy
$MaxWait = 30
$Elapsed = 0
do {
    Start-Sleep -Seconds 2
    $Elapsed += 2
    $pgReady = docker compose -f "$Root\infra\docker-compose.yml" ps postgres 2>$null | Select-String "healthy"
    $rdReady = docker compose -f "$Root\infra\docker-compose.yml" ps redis    2>$null | Select-String "healthy"
} until (($pgReady -and $rdReady) -or ($Elapsed -ge $MaxWait))

if (-not ($pgReady -and $rdReady)) {
    Write-Host "Docker services not healthy after ${MaxWait}s — check: docker compose ps" -ForegroundColor Red
    exit 1
}
Write-Host "Postgres + Redis healthy." -ForegroundColor Green

# 2. DB migration
Write-Host "Running migrations..." -ForegroundColor Cyan
uv run --directory "$Root\apps\api" alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Migration failed — aborting." -ForegroundColor Red
    exit 1
}
Write-Host "Migrations up to date." -ForegroundColor Green

# 3. Service terminals
Write-Host "Opening service terminals..." -ForegroundColor Cyan

$apiCmd    = "uv run --env-file ../../.env --directory apps\api uvicorn datask_api.main:app --reload --port 8000"
$workerCmd = "uv run --env-file ../../.env --directory apps\worker python -m datask_worker.main"
$webCmd    = "npm run dev"

Start-Process wt -ArgumentList "new-tab --title API    -d `"$Root`"           powershell -NoExit -Command `"$apiCmd`""
Start-Process wt -ArgumentList "new-tab --title Worker -d `"$Root`"           powershell -NoExit -Command `"$workerCmd`""
Start-Process wt -ArgumentList "new-tab --title Web    -d `"$Root\apps\web`" powershell -NoExit -Command `"$webCmd`""

Write-Host ""
Write-Host "All services starting:" -ForegroundColor Green
Write-Host "  API    -> http://localhost:8000/docs"
Write-Host "  Worker -> see Worker tab"
Write-Host "  Web    -> http://localhost:3000"
