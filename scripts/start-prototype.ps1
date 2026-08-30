$ErrorActionPreference = "Stop"
$RepoDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoDir

& ".venv\Scripts\python.exe" "scripts\prototype_tools.py" check
$Api = Start-Process -PassThru -NoNewWindow ".venv\Scripts\python.exe" `
  -ArgumentList "-m", "uvicorn", "apps.api.main:app", "--host", "127.0.0.1", "--port", "8000"

try {
  Set-Location "$RepoDir\apps\dashboard"
  npm run dev -- --host 0.0.0.0
}
finally {
  Stop-Process -Id $Api.Id -ErrorAction SilentlyContinue
}
