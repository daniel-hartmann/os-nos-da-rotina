# Motor do jogo (alvo bat). Porta de engine.js: mesmas regras do alvo bash (veja gamegen/model.py).
# Espera a variavel $DataJson (JSON de gamegen/export.py) e os argumentos em $env:GAME_ARGS.
# Este arquivo e so ASCII de proposito: acentos vem dos dados (\uXXXX) ou de U('...').

$ErrorActionPreference = 'Stop'
function U([string]$s) { [regex]::Unescape($s) }
$Msg = @{
    invalid = U('Digite um n\u00famero de 1 a ')
    back    = U('\u21ba o fluxo volta para: ')
    restart = U('Recome\u00e7ar? [s/N] ')
    noTrans = U('[erro] nenhuma transi\u00e7\u00e3o v\u00e1lida a partir de ')
    fim     = U('\u2014 Fim \u2014')
}
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch { }

# ----------------------------------------------------------------- argumentos
$script:Auto = $false
$script:NoPause = $false
$script:DebugOn = $false
$seed = $null
$argv = @()
if ($env:GAME_ARGS) { $argv = @($env:GAME_ARGS -split '\s+' | Where-Object { $_ -ne '' }) }
for ($i = 0; $i -lt $argv.Count; $i++) {
    switch ($argv[$i]) {
        '--auto'     { $script:Auto = $true; $script:NoPause = $true }
        '--no-pause' { $script:NoPause = $true }
        '--debug'    { $script:DebugOn = $true }
        '--seed'     { $i++; $seed = [int]$argv[$i] }
        { $_ -in '-h', '--help', '/?' } {
            Write-Host 'Uso: jogo.bat [--auto] [--no-pause] [--seed N] [--debug]'
            Write-Host '  --auto      joga sozinho, escolhendo ao acaso (para testar o grafo)'
            Write-Host '  --no-pause  nao espera Enter entre as paginas e nao limpa a tela'
            Write-Host '  --seed N    semente do sorteio (reprodutivel)'
            Write-Host '  --debug     mostra o id e o rotulo de design de cada no'
            exit 0
        }
        default { [Console]::Error.WriteLine('Argumento desconhecido: ' + $argv[$i]); exit 2 }
    }
}
$script:Rng = if ($null -ne $seed) { New-Object System.Random -ArgumentList $seed } else { New-Object System.Random }

$script:Data = $DataJson | ConvertFrom-Json
$script:Vars = @{}
$script:Visited = @{}
$script:PageOpen = $false   # ha texto na tela que a pessoa ainda nao "passou adiante"
$script:Fresh = $true       # a tela acabou de ser limpa
$script:Hold = $false       # a proxima pagina se junta a atual (titulo + primeira pagina)
$script:Lines = 0           # blocos ja impressos nesta tela (para o espaco entre eles)
$script:CanClear = ((-not $script:NoPause) -and (-not [Console]::IsOutputRedirected))

# ------------------------------------------------------------------------ tela
function Out-Block([string]$text, [string]$color) {
    if ($script:Lines -gt 0) { Write-Host '' }
    if ($color) { Write-Host $text -ForegroundColor $color } else { Write-Host $text }
    $script:Lines++
}

function Ui-Clear {
    if ($script:CanClear) { try { Clear-Host } catch { Write-Host '' } } else { Write-Host '' }
    $script:Lines = 0
}

function Read-Line {
    $l = [Console]::In.ReadLine()
    if ($null -eq $l) { Write-Host ''; exit 0 }
    return $l
}

function Ui-WaitContinue {
    Write-Host ''
    Write-Host '[Enter para continuar] ' -NoNewline -ForegroundColor DarkGray
    [void](Read-Line)
}

function Ui-Menu([string]$prompt, [string[]]$labels) {
    Out-Block $prompt 'White'
    if ($script:Auto) {
        $idx = $script:Rng.Next($labels.Count)
        Write-Host ('  > ' + $labels[$idx]) -ForegroundColor DarkGray
        return $idx
    }
    for ($i = 0; $i -lt $labels.Count; $i++) { Write-Host ('  {0}) {1}' -f ($i + 1), $labels[$i]) }
    while ($true) {
        Write-Host '> ' -NoNewline
        $ans = Read-Line
        if ($ans -in 'q', 'Q', 'sair') { exit 0 }
        $num = 0
        if ([int]::TryParse($ans, [ref]$num) -and $num -ge 1 -and $num -le $labels.Count) { return ($num - 1) }
        Write-Host ($Msg.invalid + $labels.Count + ' (ou q para sair).')
    }
}

# ---------------------------------------------------------------------- motor
function Get-Var([string]$k) { if ($script:Vars.ContainsKey($k)) { return [string]$script:Vars[$k] } else { return '' } }

function Test-When($when) {
    foreach ($p in $when.PSObject.Properties) {
        if ((Get-Var $p.Name) -cne [string]$p.Value) { return $false }
    }
    return $true
}

function Expand-Text([string]$text) {
    $s = $text
    foreach ($v in @($script:Data.interp)) { if ($v) { $s = $s.Replace('{' + $v + '}', (Get-Var $v)) } }
    return $s
}

function Clear-Page { Ui-Clear; $script:Fresh = $true }

function New-Page {
    if ($script:Hold) { $script:Hold = $false; return }
    if ($script:PageOpen) {
        if (-not $script:NoPause) { Ui-WaitContinue }
        $script:PageOpen = $false
    }
    if (-not $script:Fresh) { Clear-Page }
}

function Before-Input {
    if ((-not $script:PageOpen) -and (-not $script:Fresh)) { Clear-Page }
    $script:Fresh = $false
}

function Show-Block([string]$kind, [bool]$same, [string]$a, [string]$b) {
    if ((-not $same) -or (-not $script:PageOpen)) { New-Page }
    switch ($kind) {
        'art'     { Out-Block $a 'Yellow' }
        'text'    { Out-Block $a $null }
        'pending' {
            Out-Block ('[texto pendente] ' + $a) 'DarkGray'
            if ($b) { Write-Host ('  rascunho: ' + $b) -ForegroundColor DarkGray }
        }
    }
    $script:PageOpen = $true
    $script:Fresh = $false
}

function Read-Menu([string]$prompt, [string[]]$labels) {
    Before-Input
    $script:PageOpen = $false
    return (Ui-Menu $prompt $labels)
}

function Read-Ask($node) {
    Before-Input
    $prompt = Expand-Text $node.ask.prompt
    $def = [string]$node.ask.default
    if ($script:Auto) {
        $ans = if ($def) { $def } else { 'X' }
        Out-Block ($prompt + '  > ' + $ans) 'DarkGray'
    } else {
        Out-Block $prompt 'White'
        while ($true) {
            Write-Host '> ' -NoNewline
            $ans = Read-Line
            if (-not $ans) { $ans = $def }
            if ($ans) { break }
        }
    }
    $script:Vars[[string]$node.ask.var] = $ans
    $script:PageOpen = $false
}

function Reset-State {
    $keep = @{}
    foreach ($k in @($script:Data.persistent)) { if ($k -and $script:Vars.ContainsKey($k)) { $keep[$k] = $script:Vars[$k] } }
    $script:Vars = $keep
    $script:Visited = @{}
}

function Invoke-GoBack($edge) {
    $label = $script:Data.nodes.($edge.to).label
    Out-Block ($Msg.back + $label) 'DarkGray'
    $script:Fresh = $false
    $script:PageOpen = $false
    if ($script:Auto) { return '' }
    Write-Host $Msg.restart -NoNewline
    $ans = Read-Line
    if ($ans -in 's', 'S', 'sim', 'Sim') { Reset-State; return [string]$edge.to }
    return ''
}

function Get-Next($edge) { if ($edge.back) { return (Invoke-GoBack $edge) } else { return [string]$edge.to } }

function Stop-NoTransition([string]$id) {
    [Console]::Error.WriteLine($Msg.noTrans + $id + '; encerrando.')
    return ''
}

function Enter-Panel($node, [string]$panelId) {
    $entries = @($script:Data.panels.$panelId.entries)
    $cands = @($entries | Where-Object { -not $script:Visited.ContainsKey($_) })
    if ($cands.Count -eq 0) { $cands = $entries }
    if ($cands.Count -eq 1) {
        $chosen = [string]$cands[0]
    } elseif ($node.mode -eq 'random') {
        $k = $script:Rng.Next($cands.Count)
        $chosen = [string]$cands[$k]
    } else {
        $prompt = if ($node.prompt) { $node.prompt } else { $script:Data.panelPrompt }
        $labels = @($cands | ForEach-Object { Expand-Text ($script:Data.nodes.$_.menu) })
        $chosen = [string]$cands[(Read-Menu (Expand-Text $prompt) $labels)]
    }
    $script:Visited[$chosen] = $true
    Invoke-From $chosen
}

function Invoke-Node([string]$id) {
    $n = $script:Data.nodes.$id
    if ($script:DebugOn) { Write-Host ('[' + $id + ' ' + $n.kind + '] ' + $n.label) -ForegroundColor DarkGray }
    if ($n.art) { Show-Block 'art' ([bool]$n.same) $n.art '' }
    $same = ([bool]$n.same) -or [bool]$n.art
    if ($null -eq $n.narrative) {
        if ($n.kind -eq 'process') { Show-Block 'pending' $same $n.label $n.draft }
    } elseif ($n.narrative -ne '') {
        Show-Block 'text' $same (Expand-Text $n.narrative) ''
    }
    if ($n.ask) { Read-Ask $n }
    foreach ($p in $n.set.PSObject.Properties) { $script:Vars[$p.Name] = [string]$p.Value }
    foreach ($p in @($n.calls)) { if ($p) { Enter-Panel $n ([string]$p) } }

    $succ = @($n.succ)
    if ($succ.Count -eq 0) { return '' }
    if ($n.mode -eq 'conditional') {
        $hasWhen = @($succ | Where-Object { $_.when }).Count -gt 0
        $fallback = $succ | Where-Object { -not $_.when } | Select-Object -First 1
        foreach ($e in $succ) { if ($e.when -and (Test-When $e.when)) { return (Get-Next $e) } }
        if ((-not $hasWhen) -or $fallback) { return (Get-Next $fallback) }
        return (Stop-NoTransition $id)
    }
    if ($n.mode -eq 'random' -and ($succ.Count -gt 1 -or $succ[0].when)) {
        $elig = @($succ | Where-Object { (-not $_.when) -or (Test-When $_.when) })
        if ($elig.Count -eq 0) { return (Stop-NoTransition $id) }
        $chosenEdge = $elig[$script:Rng.Next($elig.Count)]
        return (Get-Next $chosenEdge)
    }
    if ($succ.Count -eq 1) { return (Get-Next $succ[0]) }
    $prompt = if ($n.prompt) { $n.prompt } else { $script:Data.defaultPrompt }
    $labels = @($succ | ForEach-Object { Expand-Text ($script:Data.nodes.($_.to).menu) })
    $idx = Read-Menu (Expand-Text $prompt) $labels
    return (Get-Next $succ[$idx])
}

function Invoke-From([string]$start) {
    $next = $start
    while ($next) { $next = [string](Invoke-Node $next) }
}

# --------------------------------------------------------------------- partida
Clear-Page
Out-Block $script:Data.title 'Cyan'
$script:Fresh = $false
$script:Hold = $true
Invoke-From $script:Data.start
Write-Host ''
Write-Host $Msg.fim -ForegroundColor DarkGray
