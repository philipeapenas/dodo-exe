<#
.SYNOPSIS
Instala o workspace Dodo.exe nesta pasta: monta o Vault a partir do modelo e sincroniza as skills.

.DESCRIPTION
Faz so a parte mecanica e pode rodar quantas vezes quiser: nada que ja exista no Vault e sobrescrito.
A conversa que preenche a sua Identidade acontece depois, no Claude Code: abra esta pasta e diga "instala o Dodo.exe".

.EXAMPLE
.\install.ps1

.EXAMPLE
.\install.ps1 --dry-run
Mostra o que seria criado, sem escrever nada.
#>

$ErrorActionPreference = "Stop"

$instalador = Join-Path $PSScriptRoot ".agents\skills\instalador-expert\tools\instalar.py"
if (-not (Test-Path $instalador)) {
    Write-Error "Nao achei $instalador. Rode install.ps1 de dentro da pasta do repositorio."
    exit 1
}

# 'python' no Windows pode ser o atalho da Microsoft Store, que existe mas nao roda nada.
# Por isso cada candidato e testado de verdade antes de ser usado.
$candidatos = @(@("py", "-3"), @("python"), @("python3"))
$python = $null
foreach ($c in $candidatos) {
    if (-not (Get-Command $c[0] -ErrorAction SilentlyContinue)) { continue }
    $pre = @($c | Select-Object -Skip 1)
    & $c[0] @pre -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $python = $c; break }
}

if (-not $python) {
    Write-Host "ERRO: precisa de Python 3.8 ou mais novo. Instale em https://www.python.org/downloads/ e marque 'Add python.exe to PATH'." -ForegroundColor Red
    exit 1
}

$pre = @($python | Select-Object -Skip 1)
& $python[0] @pre $instalador @args
exit $LASTEXITCODE
