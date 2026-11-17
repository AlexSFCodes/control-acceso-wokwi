$ErrorActionPreference = 'Stop'
$cliProyecto = Join-Path $env:LOCALAPPDATA 'Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe'
if (-not (Test-Path -LiteralPath $cliProyecto)) {
    $comandoCli = Get-Command arduino-cli -ErrorAction SilentlyContinue
    if (-not $comandoCli) {
        throw 'No se encontro Arduino CLI. Compila desde Arduino IDE o instala Arduino CLI.'
    }
    $cliProyecto = $comandoCli.Source
}
$argumentosProyecto = @('compile', '--fqbn', 'arduino:avr:uno', '--output-dir', (Join-Path $PSScriptRoot 'build'))
$configProyecto = Join-Path $env:USERPROFILE '.arduinoIDE\arduino-cli.yaml'
if (Test-Path -LiteralPath $configProyecto) {
    $argumentosProyecto += @('--config-file', $configProyecto)
}
$argumentosProyecto += $PSScriptRoot
& $cliProyecto @argumentosProyecto
if ($LASTEXITCODE -ne 0) {
    throw 'La compilacion fallo. Comprueba que Arduino AVR Boards este instalado en el gestor de placas del IDE.'
}
Write-Host 'Firmware actualizado en build/. Ya puedes iniciar Wokwi en VS Code.'
