$ErrorActionPreference = "Stop"

$installerUrl = "https://github.com/Tenqo/SysClock/releases/latest/download/SysClock-Windows-Setup.exe"
$installerPath = Join-Path $env:TEMP "SysClock-Windows-Setup-$([guid]::NewGuid().ToString('N')).exe"

try {
    Write-Host "Downloading SysClock..."
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing

    Write-Host "Installing SysClock for the current Windows user..."
    $process = Start-Process -FilePath $installerPath `
        -ArgumentList @("/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-") `
        -Wait `
        -PassThru

    if ($process.ExitCode -ne 0) {
        throw "SysClock setup failed with exit code $($process.ExitCode)."
    }

    Write-Host "SysClock was installed successfully."
}
finally {
    if (Test-Path -LiteralPath $installerPath) {
        Remove-Item -LiteralPath $installerPath -Force -ErrorAction Stop
    }
}
